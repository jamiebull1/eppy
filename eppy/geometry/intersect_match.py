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

from copy import deepcopy
import itertools

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
    surfaces = [[s, Polygon3D(s.coords)] for s in surfaces]
    global_geometry_rules = idf.idfobjects['GLOBALGEOMETRYRULES']

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
            new = deepcopy(s1[0])
            new.Name = "%s_%s_%i" % (s1[0].Name, 'new', i)
            set_coords(new, s.points_matrix, global_geometry_rules)
            new.Outside_Boundary_Condition = "Zone"
            new.Outside_Boundary_Condition_Object = s2[0].Zone_Name
            idf.copyidfobject(new)
            # inverted intersection
            new_inv = deepcopy(s2[0])
            new_inv.Name = "%s_%s_%i" % (s2[0].Name, 'new', i)
            new_inv.Outside_Boundary_Condition = "Zone"
            new_inv.Outside_Boundary_Condition_Object = s1[0].Zone_Name
            set_coords(new_inv, reversed(s.points_matrix), global_geometry_rules)
            idf.copyidfobject(new_inv)
        # edit the original two surfaces
        s1_new = s1[1].difference(s2[1])
        s2_new = s2[1].difference(s1[1])
        if s1_new:
            # modify the original s1[0]
            set_coords(s2[0], s2_new[0].points_matrix, global_geometry_rules)
        if s2_new:
            # modify the original s2[0]
            set_coords(s2[0], s2_new[0].points_matrix, global_geometry_rules)
    
        
def set_coords(surface, new_coords, ggr):
    """Update the coordinates of a surface.
    
    This functions follows the GlobalGeometryRules of the IDF where available.
    
    Parameters
    ----------
    surface : EPBunch
        The surface to modify.
    new_coords : list
        The new coordinates.
    ggr : EPBunch, optional
        The section of the IDF that give rules for the order of vertices in a
        surface {default : None}.
    """
    # make new_coords follow the GlobalGeometryRules
    if not ggr:
        starting_position = 'UpperLeftCorner'  # EnergyPlus default
        entry_direction = 'Counterclockwise'  # EnergyPlus default
    else:
        starting_position = ggr[0].Starting_Vertex_Position
        entry_direction = ggr[0].Vertex_Entry_Direction
    
    coords = itertools.chain(*new_coords)

    # find the vertex fields
    n_vertices_index = surface.fieldnames.index('Number_of_Vertices')
    last_x = len(surface.obj)
    first_x = n_vertices_index + 1 # X of first coordinate
    vertex_fields = surface.fieldnames[first_x:last_x]
    
    # set the vertex field values
    for field, x in itertools.izip_longest(vertex_fields, coords, fillvalue=""):
        surface[field] = x
    
    
def getidfsurfaces(idf):
    """Return all surfaces in an IDF.
    
    """
    surfaces = idf.idfobjects['BUILDINGSURFACE:DETAILED']
    return surfaces
