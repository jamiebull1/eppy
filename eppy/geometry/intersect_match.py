# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""Intersect and match all surfaces in an IDF.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools

from eppy.geometry.polygons import Polygon3D
from eppy.geometry.polygons import normalize_coords
from six.moves import zip_longest


def intersect_idf_surfaces(idf):
    """Intersect all surfaces in an IDF.
    
    Parameters
    ----------
    idf : IDF object
        The IDF.
    
    Returns
    -------
    IDF object
    
    """
    surfaces = getidfsurfaces(idf)
    """
    @TODO: Add the Polygon3D as a field for all EPlus building surfaces so we
    can call surface1.poly.intersect(surface2.poly) and avoid all the indexing
    in the code below.
    """ 
    surfaces = [[s, Polygon3D(s.coords)] for s in surfaces]
    ggr = idf.idfobjects['GLOBALGEOMETRYRULES']
    if ggr:
        clockwise = ggr[0].Vertex_Entry_Direction
    else:
        clockwise = 'counterclockwise'
    for s1, s2 in itertools.combinations(surfaces, 2):
        # get a point outside the zone, assuming surface is oriented correctly
        outside_s1 = s1[1].outside_point(clockwise)
        outside_s2 = s2[1].outside_point(clockwise)
            
        if s1[0].Zone_Name == s2[0].Zone_Name:
            continue
        if not s1[1].is_coplanar(s2[1]):
            continue
        intersects = s1[1].intersect(s2[1])
        if not intersects:
            continue
        # create new surfaces for the intersects, and their reflections
        for i, intersect in enumerate(intersects, 1):
            # regular intersection
            """
            @TODO: Check the intersection touches an edge of both surfaces.
            If it doesn't touch an edge then we need to make subsurfaces in
            each surface.
            """
            """
            @TODO: Handle any existing subsurfaces which may need to be split.
            """
            new = idf.copyidfobject(s1[0])
            new.Name = "%s_%s_%i" % (s1[0].Name, 'new', i)
            set_coords(new, intersect, outside_s2, ggr)
            new.Outside_Boundary_Condition = "Zone"
            new.Outside_Boundary_Condition_Object = s2[0].Zone_Name
            # inverted intersection
            new_inv = idf.copyidfobject(s2[0])
            new_inv.Name = "%s_%s_%i" % (s2[0].Name, 'new', i)
            new_inv.Outside_Boundary_Condition = "Zone"
            new_inv.Outside_Boundary_Condition_Object = s1[0].Zone_Name
            set_coords(new_inv, intersect.invert_orientation(), outside_s2, ggr)
        # edit the original two surfaces
        s1_new = s1[1].difference(s2[1])
        s2_new = s2[1].difference(s1[1])
        if s1_new:
            # modify the original s1[0]
            set_coords(s1[0], s1_new[0], outside_s1, ggr)
        if s2_new:
            # modify the original s2[0]
            set_coords(s2[0], s2_new[0], outside_s2, ggr)
    
        
def set_coords(surface, poly, outside_pt, ggr=None):
    """Update the coordinates of a surface.
    
    This functions follows the GlobalGeometryRules of the IDF where available.
    
    Parameters
    ----------
    surface : EPBunch
        The surface to modify.
    coords : list
        The new coordinates.
    outside_pt : Point3D
        A point outside the zone the surface belongs to.
    ggr : EPBunch
        The section of the IDF that give rules for the order of vertices in a
        surface.
    
    """
    # make new_coords follow the GlobalGeometryRules
    poly = normalize_coords(poly, outside_pt, ggr)
    coords = [i for vertex in poly for i in vertex]
    # find the vertex fields
    n_vertices_index = surface.fieldnames.index('Number_of_Vertices')
    last_z = len(surface.obj)
    first_x = n_vertices_index + 1 # X of first coordinate
    vertex_fields = surface.fieldnames[first_x:last_z] # Z of final coordinate
    
    # set the vertex field values
    for field, x in zip_longest(vertex_fields, coords, fillvalue=""):
        surface[field] = x
    

def getidfsurfaces(idf):
    """Return all surfaces in an IDF.
    
    """
    surfaces = idf.idfobjects['BUILDINGSURFACE:DETAILED']
    return surfaces
