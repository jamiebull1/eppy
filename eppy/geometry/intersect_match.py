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
from six.moves import zip_longest

from eppy.geometry.polygons import Polygon3D


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

    for s1, s2 in itertools.combinations(surfaces, 2):
        if s1[0].Zone_Name == s2[0].Zone_Name:
            continue
        if s1[1] == s2[1]:
            continue
        if not s1[1].is_coplanar(s2[1]):
            continue
        intersects = s1[1].intersect(s2[1])
        if not intersects:
            continue
        # create new surfaces for the intersects, and their reflections
        for i, s in enumerate(intersects, 1):
            # regular intersection
            new = idf.copyidfobject(s1[0])
            new.Name = "%s_%s_%i" % (s1[0].Name, 'new', i)
            set_coords(new, s.points_matrix, ggr)
            new.Outside_Boundary_Condition = "Zone"
            new.Outside_Boundary_Condition_Object = s2[0].Zone_Name
            # inverted intersection
            new_inv = idf.copyidfobject(s2[0])
            new_inv.Name = "%s_%s_%i" % (s2[0].Name, 'new', i)
            new_inv.Outside_Boundary_Condition = "Zone"
            new_inv.Outside_Boundary_Condition_Object = s1[0].Zone_Name
            set_coords(new_inv, reversed(s.points_matrix), ggr)
        # edit the original two surfaces
        s1_new = s1[1].difference(s2[1])
        s2_new = s2[1].difference(s1[1])
        if s1_new:
            # modify the original s1[0]
            set_coords(s2[0], s2_new[0].points_matrix, ggr)
        if s2_new:
            # modify the original s2[0]
            set_coords(s2[0], s2_new[0].points_matrix, ggr)
    
        
def set_coords(surface, coords, ggr):
    """Update the coordinates of a surface.
    
    This functions follows the GlobalGeometryRules of the IDF where available.
    
    Parameters
    ----------
    surface : EPBunch
        The surface to modify.
    coords : list
        The new coordinates.
    ggr : EPBunch, optional
        The section of the IDF that give rules for the order of vertices in a
        surface {default : None}.
    """
    # make new_coords follow the GlobalGeometryRules
    coords = normalise_coords(coords, ggr)

    # find the vertex fields
    n_vertices_index = surface.fieldnames.index('Number_of_Vertices')
    last_x = len(surface.obj)
    first_x = n_vertices_index + 1 # X of first coordinate
    vertex_fields = surface.fieldnames[first_x:last_x]
    
    # set the vertex field values
    for field, x in zip_longest(vertex_fields, coords, fillvalue=""):
        surface[field] = x
    

def normalise_coords(coords, ggr):
    """Put coordinates into the correct format for EnergyPlus.
    
    coords : list
        The new coordinates.
    ggr : EPBunch, optional
        The section of the IDF that give rules for the order of vertices in a
        surface {default : None}.
    
    Returns
    -------
    list
    
    """
    if not ggr:
        starting_position = 'UpperLeftCorner'  # EnergyPlus default
        entry_direction = 'Counterclockwise'  # EnergyPlus default
    else:
        starting_position = ggr[0].Starting_Vertex_Position
        entry_direction = ggr[0].Vertex_Entry_Direction
    
    coords = itertools.chain(*coords)
    
    return coords


def getidfsurfaces(idf):
    """Return all surfaces in an IDF.
    
    """
    surfaces = idf.idfobjects['BUILDINGSURFACE:DETAILED']
    return surfaces
