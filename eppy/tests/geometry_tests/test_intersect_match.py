# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""pytest for intersect_match.py"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from eppy.iddcurrent import iddcurrent
from eppy.idf_msequence import Idf_MSequence
from eppy.modeleditor import IDF
from six import StringIO

from eppy.geometry.intersect_match import getidfsurfaces
from eppy.geometry.intersect_match import intersect_idf_surfaces
from eppy.geometry.polygons import Polygon3D
from eppy.geometry.intersect_match import normalise_coords


idf_txt = """
    Building, Building 1, , , , , , , ;  GlobalGeometryRules, UpperLeftCorner, Counterclockwise, Relative, Relative, Relative;
    Zone, z1, 0.0, 0.0, 0.0, 0.0, , 1, , , , , , Yes;
    Zone, z2, 0.0, 0.0, 0.0, 0.0, , 1, , , , , , Yes;
    BuildingSurface:Detailed, z1_FLOOR, FLOOR, , z1, ground, , NoSun, NoWind, , , 1.0, 2.1, 0.0, 2.0, 2.0, 0.0, 2.0, 1.0, 0.0, 1.0, 1.1, 0.0;
    BuildingSurface:Detailed, z1_WALL_0001, WALL, , z1, outdoors, , SunExposed, WindExposed, , , 1.0, 1.1, 0.5, 1.0, 1.1, 0.0, 1.0, 2.1, 0.0, 1.0, 2.1, 0.5;
    BuildingSurface:Detailed, match_01, WALL, , z1, outdoors, , SunExposed, WindExposed, , , 1.0, 2.1, 0.5, 1.0, 2.1, 0.0, 2.0, 2.0, 0.0, 2.0, 2.0, 0.5;
    BuildingSurface:Detailed, z1_WALL_0003, WALL, , z1, outdoors, , SunExposed, WindExposed, , , 2.0, 2.0, 0.5, 2.0, 2.0, 0.0, 2.0, 1.0, 0.0, 2.0, 1.0, 0.5;
    BuildingSurface:Detailed, z1_WALL_0004, WALL, , z1, outdoors, , SunExposed, WindExposed, , , 2.0, 1.0, 0.5, 2.0, 1.0, 0.0, 1.0, 1.1, 0.0, 1.0, 1.1, 0.5;
    BuildingSurface:Detailed, z1_ROOF, ROOF, , z1, outdoors, , SunExposed, WindExposed, , , 1.0, 2.1, 0.5, 2.0, 2.0, 0.5, 2.0, 1.0, 0.5, 1.0, 1.1, 0.5;
    BuildingSurface:Detailed, z2_FLOOR, FLOOR, , z2, ground, , NoSun, NoWind, , , 1.5, 3.05, 0.0, 2.5, 2.95, 0.0, 2.5, 1.95, 0.0, 1.5, 2.05, 0.0;
    BuildingSurface:Detailed, z2_WALL_0001, WALL, , z2, outdoors, , SunExposed, WindExposed, , , 1.5, 2.05, 0.5, 1.5, 2.05, 0.0, 1.5, 3.05, 0.0, 1.5, 3.05, 0.5;
    BuildingSurface:Detailed, z2_WALL_0002, WALL, , z2, outdoors, , SunExposed, WindExposed, , , 1.5, 3.05, 0.5, 1.5, 3.05, 0.0, 2.5, 2.95, 0.0, 2.5, 2.95, 0.5;
    BuildingSurface:Detailed, z2_WALL_0003, WALL, , z2, outdoors, , SunExposed, WindExposed, , , 2.5, 2.95, 0.5, 2.5, 2.95, 0.0, 2.5, 1.95, 0.0, 2.5, 1.95, 0.5;
    BuildingSurface:Detailed, match_02, WALL, , z2, outdoors, , SunExposed, WindExposed, , , 2.5, 1.95, 0.5, 2.5, 1.95, 0.0, 1.5, 2.05, 0.0, 1.5, 2.05, 0.5;
    BuildingSurface:Detailed, z2_ROOF, ROOF, , z2, outdoors, , SunExposed, WindExposed, , , 1.5, 3.05, 0.5, 2.5, 2.95, 0.5, 2.5, 1.95, 0.5, 1.5, 2.05, 0.5;
"""

class TestIntersectMatch():
    def setup(self):
        iddfhandle = StringIO(iddcurrent.iddtxt)
        if IDF.getiddname() == None:
            IDF.setiddname(iddfhandle)
        
        self.idf = IDF(StringIO(idf_txt))
            
    def test_getidfsurfaces(self):    
        idf = self.idf
        surfaces = getidfsurfaces(idf)
        assert isinstance(surfaces, Idf_MSequence)
        assert len(surfaces) == 12
    
    def test_intersect_idf_surfaces(self):       
        idf = self.idf        
        starting = len(idf.idfobjects['BUILDINGSURFACE:DETAILED'])
        intersect_idf_surfaces(idf)
        ending = len(idf.idfobjects['BUILDINGSURFACE:DETAILED'])
        assert starting == 12
        assert ending == 14

        result = [w for w in idf.idfobjects['BUILDINGSURFACE:DETAILED']
                     if w.Name == 'match_01_new_1']
        assert len(result) == 1
        result = [w for w in idf.idfobjects['BUILDINGSURFACE:DETAILED']
                     if w.Name == 'match_02_new_1']
        assert len(result) == 1

    def test_normalise_coords(self):
        idf = self.idf
        ggr = idf.idfobjects['GLOBALGEOMETRYRULES']
        poly = Polygon3D([(0,0,1), (0,0,0), (1,0,0), (1,0,1)])
        inv_poly = Polygon3D(reversed([(0,0,1), (0,0,0), (1,0,0), (1,0,1)]))
        offset_poly = Polygon3D([(1,0,1), (0,0,1), (0,0,0), (1,0,0)])
        inv_offset_poly = Polygon3D(
            reversed([(1,0,1), (0,0,1), (0,0,0), (1,0,0)]))

        entry_direction = 'counterclockwise'
        outside_pt = poly.outside_point(entry_direction)
        expected = poly.points_matrix
        
        # expect no change
        result = normalise_coords(poly, outside_pt, ggr)
        assert (result == expected).all()
        
        # expect direction to be reversed
        result = normalise_coords(inv_poly, outside_pt, ggr)
        assert (result == expected).all()
        
        entry_direction = 'clockwise'
        outside_pt = Polygon3D(poly).outside_point(entry_direction)
        expected = inv_poly.points_matrix
        
        # expect no change
        result = normalise_coords(poly, outside_pt, ggr)
        assert (result == expected).all()
        
        # expect direction to be reversed
        result = normalise_coords(inv_poly, outside_pt, ggr)
        assert (result == expected).all()
        
        entry_direction = 'counterclockwise'
        outside_pt = poly.outside_point(entry_direction)
        expected = poly.points_matrix
        
        # expect to move entry point
        result = normalise_coords(offset_poly, outside_pt, ggr)
        assert (result == expected).all()

        # expect direction to reverse and to move entry point
        result = normalise_coords(inv_offset_poly, outside_pt, ggr)
        assert (result == expected).all()
                
        entry_direction = 'clockwise'
        outside_pt = Polygon3D(poly).outside_point(entry_direction)
        expected = inv_poly.points_matrix
        
        # expect to move entry point
        result = normalise_coords(offset_poly, outside_pt, ggr)
        assert (result == expected).all()

        # expect direction to reverse and to move entry point
        result = normalise_coords(inv_offset_poly, outside_pt, ggr)
        assert (result == expected).all()
        
        
