# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
from eppy.pytest_helpers import almostequal
"""
Heavy lifting geometry for IDF surfaces.

PyClipper is used for clipping.

"""
import pyclipper as pc


try:
    import numpy as np
except ImportError:
    import tinynumpy.tinynumpy as np


class Point2D(object):
    """Two dimensional point."""
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.args = (self.x, self.y)
    
    def __iter__(self):
        return (i for i in self.args)

    def __repr__(self):
        class_name = type(self).__name__
        return '{}({!r}, {!r})'.format(class_name, *self.args)
    
    def __eq__(self, other): 
        return self.__dict__ == other.__dict__
            
        
class Point3D(Point2D):
    """Three dimensional point."""
    def __init__(self, x, y, z):
        super(Point3D, self).__init__(x, y)
        self.z = float(z)
        self.args = (self.x, self.y, self.z)
        
    def __repr__(self):
        class_name = type(self).__name__
        return '{}({!r}, {!r}, {!r})'.format(class_name, *self.args)


class Polygon(object):
    """Two-dimensional polygon."""
    n_dims = 2

    def __init__(self, vertices):
        self.vertices = [Point2D(*v) for v in vertices]
    
    def __iter__(self):
        return (i for i in self.vertices)
    
    def __repr__(self):
        class_name = type(self).__name__
        return '{}({!r})'.format(class_name, self.vertices)

    def __eq__(self, other):
        if self.__dict__ == other.__dict__:  # try the simple case first
            return True
        else:  # also cover same shape in different orientation
            return self.difference(other) == False
    
    def __len__(self):
        return len(self.vertices)
            
    @property
    def points_matrix(self):
        """[[x1, x2,... xn]
            [y1, y2,... yn]
            [z1, z2,... zn]  # all 0 for 2D polygon
        """
        points = np.zeros((len(self.vertices), self.n_dims))
        for i, v in enumerate(self.vertices):
            points[i,:] = pt_to_array(v, dims=self.n_dims)
        return points

    @property
    def xs(self):
        return [pt.x for pt in self.vertices]

    @property
    def ys(self):
        return [pt.y for pt in self.vertices]
   
    @property
    def zs(self):
        return [0.0] * len(self.vertices)
   
    @property
    def vertices_list(self):
        """A list of the vertices in the format required by pyclipper.
        
        Returns
        -------
        list of tuples
            Like [(x1, y1), (x2, y2),... (xn, yn)].
        
        """
        return [pt_to_tuple(pt, dims=self.n_dims) for pt in self.vertices]
        
    def project_to_3D(self, example3d):
        """Project the 2D polygon rotated into 3D space.
        
        This is used to return a previously rotated 3D polygon back to its
        original orientation, or to to put polygons generated from pyclipper
        into the desired orientation.
        
        Parameters
        ----------
        example3D : Polygon3D
            A 3D polygon in the desired plane.
                
        Returns
        -------
        Polygon3D
        
        """
        points = self.points_matrix
        proj_axis = example3d.projection_axis
        a = example3d.distance
        v = example3d.normal_vector
        projected_points = project_to_3D(points, proj_axis, a, v)
        return Polygon3D(projected_points)
    
    def union(self, poly):
        """Union with another 2D polygon.
        
        Parameters
        ----------
        poly : Polygon
            The clip polygon.

        Returns
        -------
        list
        
        """
        return union_2D_polys(self, poly)
        
    def intersect(self, poly):
        """Intersect with another 2D polygon.
        
        Parameters
        ----------
        poly : Polygon
            The clip polygon.

        Returns
        -------
        list or False
            False if no intersection, otherwise a list of lists of 2D
            coordinates representing each intersection.
        
        """
        return intersect_2D_polys(self, poly)
        
    def difference(self, poly):
        """Intersect with another 2D polygon.
        
        Parameters
        ----------
        poly : Polygon
            The clip polygon.

        Returns
        -------
        list or False
            False if no intersection, otherwise a list of lists of 2D
            coordinates representing each difference.
        
        """
        return difference_2D_polys(self, poly)
        
        
def prep_2D_polys(poly1, poly2):
    """Prepare two 2D polygons for clipping operations.
    
    Parameters
    ----------
    poly1 : Polygon
        The subject polygon.
    poly2 : Polygon
        The clip polygon.
    
    Returns
    -------
    Pyclipper object
    
    """
    s1 = pc.scale_to_clipper(poly1.vertices_list)
    s2 = pc.scale_to_clipper(poly2.vertices_list)
    clipper = pc.Pyclipper()
    clipper.AddPath(s1, poly_type=pc.PT_SUBJECT, closed=True)
    clipper.AddPath(s2, poly_type=pc.PT_CLIP, closed=True)
    return clipper


def union_2D_polys(poly1, poly2):
    """Union of two 2D polygons.
    
    Find the combined shape of poly1 and poly2.
    
    Parameters
    ----------
    poly1 : Polygon
        The subject polygon.
    poly2 : Polygon
        The clip polygon.
    
    Returns
    -------
    list or False
        False if no intersection, otherwise a list of lists of 2D coordinates
        representing each intersection.
        
    """
    clipper = prep_2D_polys(poly1, poly2)        
    intersections = clipper.Execute(
        pc.CT_UNION, pc.PFT_NONZERO, pc.PFT_NONZERO)
    result = process_clipped_2D_polys(intersections)

    return result


def intersect_2D_polys(poly1, poly2):
    """Intersect two 2D polygons.
    
    Find the area/s that poly1 shares with poly2.
    
    Parameters
    ----------
    poly1 : Polygon
        The subject polygon.
    poly2 : Polygon
        The clip polygon.
    
    Returns
    -------
    list or False
        False if no intersection, otherwise a list of lists of 2D coordinates
        representing each intersection.
        
    """
    clipper = prep_2D_polys(poly1, poly2)        
    intersections = clipper.Execute(
        pc.CT_INTERSECTION, pc.PFT_NONZERO, pc.PFT_NONZERO)
    result = process_clipped_2D_polys(intersections)

    return result


def difference_2D_polys(poly1, poly2):
    """Difference from two 2D polygons.
    
    Equivalent to subtracting poly2 from poly1.
    
    Parameters
    ----------
    poly1 : Polygon
        The subject polygon.
    poly2 : Polygon
        The clip polygon.
    
    Returns
    -------
    list or False
        False if no difference, otherwise a list of lists of 2D coordinates
        representing each difference.
        
    """
    clipper = prep_2D_polys(poly1, poly2)        
    differences = clipper.Execute(
        pc.CT_DIFFERENCE, pc.PFT_NONZERO, pc.PFT_NONZERO)
    result = process_clipped_2D_polys(differences)

    return result


def process_clipped_2D_polys(results):
    """Process and return the results of a clipping operation.
    
    Parameters
    ----------
    results : list
        A list of results, potentially empty if the operation found no
        interactions between polygons.
        
    Returns
    -------
    list or False
        False if no intersection, otherwise a list of lists of 2D coordinates
        representing each intersection.
        
    """
    if results:
        results = [pc.scale_from_clipper(r) for r in results]
        return [Polygon(r) for r in results]
    else:
        return False
        

class Polygon3D(Polygon):
    """Three-dimensional polygon."""
    n_dims = 3

    def __init__(self, vertices):
        self.vertices = [Point3D(*v) for v in vertices]

    def __eq__(self, other):
        # try the simple case
        if self.__dict__ == other.__dict__:
            return True
        # check they're in the same plane
        if list(self.normal_vector) != list(other.normal_vector):
            return False
        if self.distance != other.distance:
            return False
        # if they are in the same plane, check they completely overlap in 2D
        return (self.project_to_2D() == other.project_to_2D())
    
    @property
    def zs(self):
        return [pt.z for pt in self.vertices]

    @property
    def normal_vector(self):
        """Vector perpendicular to the polygon
        
        Choose a triangle from pt1, pt2, pt3 on the polygon:
            segment a is pt1 to pt2
            segment b is pt2 to pt3
            vector U is p2 - p1
            vector V is p1 - p3
            normal vector N is UxV (cross product)
        
        Returns
        -------
        nd.array

        """
        return normal_vector(self.vertices)

    @property
    def distance(self):
        """
        A number where v[0] * x + v[1] * y + v[2] * z = a is the equation of
        the plane containing the polygon (where v is the polygon normal vector).
        
        """
        v = self.normal_vector
        pt = self.points_matrix[0]  # arbitrary point in the polygon
        d = np.dot(v, pt)
        return d
    
    @property
    def projection_axis(self):
        proj_axis = max(range(3), key=lambda i: abs(self.normal_vector[i]))
        return proj_axis
    
    @property
    def is_horizontal(self):
        """Check if polygon is in the xy plane."""
        return np.array(self.zs).std() < 1e-8
    
    def is_coplanar(self, other):
        """Check if polygon is in the same plane as another polygon.
        
        This includes the same plane but opposite orientation.
        
        Parameters
        ----------
        other : Polygon3D
            Another polygon.
        
        Returns
        -------
        bool
        
        """
        if (almostequal(self.normal_vector, other.normal_vector) and
                almostequal(self.distance, other.distance)):
            return True
        elif (almostequal(self.normal_vector, 
                          inverse_vector(other.normal_vector)) and
              almostequal(self.distance, -other.distance)):
            return True
        else:
            return False

    def project_to_2D(self):
        """Project the 3D polygon into 2D space.
        
        This is so that we can perform operations on it using pyclipper library.
        
        Project onto either the xy, yz, or xz plane. (We choose the one that
        avoids degenerate configurations, which is the purpose of proj_axis.)
        
        Returns
        -------
        Polygon
        
        """        
        points = self.points_matrix
        projected_points = project_to_2D(points, self.projection_axis)
        
        return Polygon([pt[:2] for pt in projected_points])
    
    def invert_orientation(self):
        """Reverse the order of the vertices.
        
        This is to create a matching surface, e.g. the other side of a wall.
        
        Returns
        -------
        Polygon3D
        
        """
        return Polygon3D(reversed(self.vertices))
        
    def union(self, poly):
        """Union with another 3D polygon.
        
        Parameters
        ----------
        poly : Polygon3D
            The clip polygon.

        Returns
        -------
        list or False
            False if no union, otherwise a list of lists of Polygon3D
            objects representing each union.
        
        """
        return union_3D_polys(self, poly)
        
    def intersect(self, poly):
        """Intersect with another 3D polygon.
        
        Parameters
        ----------
        poly : Polygon3D
            The clip polygon.

        Returns
        -------
        list or False
            False if no intersection, otherwise a list of lists of Polygon3D
            objects representing each intersection.
        
        """
        return intersect_3D_polys(self, poly)
        
    def difference(self, poly):
        """Difference from another 3D polygon.
        
        Parameters
        ----------
        poly : Polygon3D
            The clip polygon.

        Returns
        -------
        list or False
            False if no difference, otherwise a list of lists of Polygon3D
            objects representing each intersection.
        
        """
        return difference_3D_polys(self, poly)


def normal_vector(poly):
    """Return the unit normal vector of a polygon.
    
    We use Newell's Method since the cross-product of two edge vectors is not
    valid for concave polygons.
    https://www.opengl.org/wiki/Calculating_a_Surface_Normal#Newell.27s_Method
    
    Parameters
    ----------
    
    """
    n = [0.0, 0.0, 0.0]

    for i, v_curr in enumerate(poly):
        v_next = poly[(i+1) % len(poly)]
        n[0] += (v_curr.y - v_next.y) * (v_curr.z + v_next.z)
        n[1] += (v_curr.z - v_next.z) * (v_curr.x + v_next.x)
        n[2] += (v_curr.x - v_next.x) * (v_curr.y + v_next.y)
    
    return normalise_vector(n)


def normalise_vector(v):
    """Convert a vector to a unit vector
    
    Parameters
    ----------
    v : list
        The vector.
        
    Returns
    -------
    list
    
    """
    magnitude = sum(abs(i) for i in v)
    normalised_v = [i / magnitude for i in v]
    
    return normalised_v


def inverse_vector(v):
    """Convert a vector to the same vector but in the opposite direction
    
    Parameters
    ----------
    v : list
        The vector.
        
    Returns
    -------
    list
    
    """    
    return [-i for i in v]


def prep_3D_polys(poly1, poly2):
    """Prepare two 3D polygons for clipping operations.
    
    Parameters
    ----------
    poly1 : Polygon3D
        The subject polygon.
    poly2 : Polygon3D
        The clip polygon.
    
    Returns
    -------
    Pyclipper object
    
    """    
    poly1 = poly1.project_to_2D()
    poly2 = poly2.project_to_2D()

    s1 = pc.scale_to_clipper(poly1.vertices_list)
    s2 = pc.scale_to_clipper(poly2.vertices_list)
    clipper = pc.Pyclipper()
    clipper.AddPath(s1, poly_type=pc.PT_SUBJECT, closed=True)
    clipper.AddPath(s2, poly_type=pc.PT_CLIP, closed=True)
    
    return clipper


def union_3D_polys(poly1, poly2):
    clipper = prep_3D_polys(poly1, poly2)
        
    unions = clipper.Execute(
        pc.CT_UNION, pc.PFT_NONZERO, pc.PFT_NONZERO)
    
    result = process_clipped_3D_polys(unions, poly1)

    return result


def intersect_3D_polys(poly1, poly2):    
    clipper = prep_3D_polys(poly1, poly2)
    
    intersections = clipper.Execute(
        pc.CT_INTERSECTION, pc.PFT_NONZERO, pc.PFT_NONZERO)
    
    result = process_clipped_3D_polys(intersections, poly1)

    return result


def difference_3D_polys(poly1, poly2):
    clipper = prep_3D_polys(poly1, poly2)
    
    differences = clipper.Execute(
        pc.CT_DIFFERENCE, pc.PFT_NONZERO, pc.PFT_NONZERO)
    
    result = process_clipped_3D_polys(differences, poly1)

    return result


def process_clipped_3D_polys(results, example3d):
    """Convert 2D clipping results back to 3D.
    
    Parameters
    ----------
    example3d : Polygon3D
        Used to find the plane to project the 2D polygons into.
    
    Returns
    -------
    list or False
        List of Poygon3D if result found, otherwise False.
        
    """
    if results:
        res_vertices = [pc.scale_from_clipper(r) for r in results]
        return [Polygon(v).project_to_3D(example3d) for v in res_vertices]
    else:
        return False

        
def project_to_2D(vertices, proj_axis):
    """
    """
    points = [project(x, proj_axis) for x in vertices]
    return points


def project(pt, proj_axis):
    """Project point pt onto either the xy, yz, or xz plane
    
    We choose the one that avoids degenerate configurations, which is the
    purpose of proj_axis.
    See http://stackoverflow.com/a/39008641/1706564
    
    """
    return tuple(c for i, c in enumerate(pt) if i != proj_axis)


def project_to_3D(vertices, proj_axis, a, v):
    """Project a 2D polygon into 3D space.
    
    Parameters
    ----------
    vertices : list 
        The two-dimensional vertices of the polygon.
    proj_axis : int
        The axis to project into.
    a : float
        Distance to the origin for the plane to project into.
    v : list
        Normal vector of the plane to project into.
    
    Returns
    -------
    list
        The transformed vertices.
    
    """
    return [project_inv(pt, proj_axis, a, v) for pt in vertices]


def project_inv(pt, proj_axis, a, v):
    """Returns the vector w in the surface's plane such that project(w) equals
    x.
    
    See http://stackoverflow.com/a/39008641/1706564
    
    Parameters
    ----------
    pt : list 
        The two-dimensional point.
    proj_axis : int
        The axis to project into.
    a : float
        Distance to the origin for the plane to project into.
    v : list
        Normal vector of the plane to project into.
    
    Returns
    -------
    list
        The transformed point.
    
    """
    w = list(pt)
    w[proj_axis:proj_axis] = [0.0]
    c = a
    for i in range(3):
        c -= w[i] * v[i]
    c /= v[proj_axis]
    w[proj_axis] = c
    return tuple(w)


def pt_to_tuple(pt, dims=3):
    """Convert a point to a numpy array.
    
    Convert a Point3D to an (x,y,z) tuple or a Point2D to an (x,y) tuple.
    Ensures all values are floats since some other types cause problems in 
    pyclipper (notably where sympy.Zero is used to represent 0.0).

    Parameters
    ----------
    pt : sympy.Point3D, sympy.Point2D
        The point to convert.
    dims : int, optional
        Number of dimensions {default : 3}.
        
    Returns
    -------
    tuple

    """
    # handle Point3D
    if dims == 3:
        return float(pt.x), float(pt.y), float(pt.z)
    # handle Point2D
    elif dims == 2:
        return float(pt.x), float(pt.y)


def pt_to_array(pt, dims=3):
    """Convert a point to a numpy array.
    
    Converts a Point3D to a numpy.array([x,y,z]) or a Point2D to a 
    numpy.array([x,y]).
    Ensures all values are floats since some other types cause problems in 
    pyclipper (notably where sympy.Zero is used to represent 0.0).
    
    Parameters
    ----------
    pt : sympy.Point3D
        The point to convert.
    dims : int, optional
        Number of dimensions {default : 3}.
    
    Returns
    -------
    numpy.ndarray

    """
    # handle Point3D
    if dims == 3:
        return np.array([float(pt.x), float(pt.y), float(pt.z)])
    # handle Point2D
    elif dims == 2:
        return np.array([float(pt.x), float(pt.y)])
