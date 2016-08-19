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

import os

from eppy.iddcurrent import iddcurrent
from eppy.idf_msequence import Idf_MSequence
from eppy.modeleditor import IDF
from eppy.pytest_helpers import IDF_FILES
from eppy.pytest_helpers import do_integration_tests
import pytest
from six import StringIO

from eppy.geometry.intersect_match import getidfsurfaces
from eppy.geometry.intersect_match import intersect_idf_surfaces

idf_txt = """
    Building, Building 1, , , , , , , ;  GlobalGeometryRules, UpperLeftCorner, Counterclockwise, Relative, Relative, Relative;
    Zone, osgb01 Thermal Zone, 0.0, 0.0, 0.0, 0.0, , 1, , , , , , Yes;
    Zone, osgb02 Thermal Zone, 0.0, 0.0, 0.0, 0.0, , 1, , , , , , Yes;
    BuildingSurface:Detailed, osgb01_lv01_FLOOR, FLOOR, , osgb01 Thermal Zone, ground, , NoSun, NoWind, , , 1.0, 2.1, 0.0, 2.0, 2.0, 0.0, 2.0, 1.0, 0.0, 1.0, 1.1, 0.0;
    BuildingSurface:Detailed, osgb01_lv01_WALL_0001, WALL, , osgb01 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 1.0, 1.1, 0.5, 1.0, 1.1, 0.0, 1.0, 2.1, 0.0, 1.0, 2.1, 0.5;
    BuildingSurface:Detailed, osgb01_lv01_WALL_0002, WALL, , osgb01 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 1.0, 2.1, 0.5, 1.0, 2.1, 0.0, 2.0, 2.0, 0.0, 2.0, 2.0, 0.5;
    BuildingSurface:Detailed, osgb01_lv01_WALL_0003, WALL, , osgb01 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 2.0, 2.0, 0.5, 2.0, 2.0, 0.0, 2.0, 1.0, 0.0, 2.0, 1.0, 0.5;
    BuildingSurface:Detailed, osgb01_lv01_WALL_0004, WALL, , osgb01 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 2.0, 1.0, 0.5, 2.0, 1.0, 0.0, 1.0, 1.1, 0.0, 1.0, 1.1, 0.5;
    BuildingSurface:Detailed, osgb01_lv02_FLOOR, FLOOR, , osgb01 Thermal Zone, ground, , NoSun, NoWind, , , 1.0, 2.1, 0.5, 2.0, 2.0, 0.5, 2.0, 1.0, 0.5, 1.0, 1.1, 0.5;
    BuildingSurface:Detailed, osgb02_lv01_FLOOR, FLOOR, , osgb02 Thermal Zone, ground, , NoSun, NoWind, , , 1.5, 3.05, 0.0, 2.5, 2.95, 0.0, 2.5, 1.95, 0.0, 1.5, 2.05, 0.0;
    BuildingSurface:Detailed, osgb02_lv01_WALL_0001, WALL, , osgb02 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 1.5, 2.05, 0.5, 1.5, 2.05, 0.0, 1.5, 3.05, 0.0, 1.5, 3.05, 0.5;
    BuildingSurface:Detailed, osgb02_lv01_WALL_0002, WALL, , osgb02 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 1.5, 3.05, 0.5, 1.5, 3.05, 0.0, 2.5, 2.95, 0.0, 2.5, 2.95, 0.5;
    BuildingSurface:Detailed, osgb02_lv01_WALL_0003, WALL, , osgb02 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 2.5, 2.95, 0.5, 2.5, 2.95, 0.0, 2.5, 1.95, 0.0, 2.5, 1.95, 0.5;
    BuildingSurface:Detailed, osgb02_lv01_WALL_0004, WALL, , osgb02 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 2.5, 1.95, 0.5, 2.5, 1.95, 0.0, 1.5, 2.05, 0.0, 1.5, 2.05, 0.5;
    BuildingSurface:Detailed, osgb02_lv02_FLOOR, FLOOR, , osgb02 Thermal Zone, ground, , NoSun, NoWind, , , 1.5, 3.05, 0.5, 2.5, 2.95, 0.5, 2.5, 1.95, 0.5, 1.5, 2.05, 0.5;
"""

class TestIntersectMatch():
    
    def test_getidfsurfaces(self):    
        iddfhandle = StringIO(iddcurrent.iddtxt)
        if IDF.getiddname() == None:
            IDF.setiddname(iddfhandle)
        
        idf = IDF(StringIO(idf_txt))

        surfaces = getidfsurfaces(idf)
        assert isinstance(surfaces, Idf_MSequence)
        assert len(surfaces) == 12
    
    def test_intersect_idf_surfaces(self):       
        iddfhandle = StringIO(iddcurrent.iddtxt)
        if IDF.getiddname() == None:
            IDF.setiddname(iddfhandle)
        
        idf = IDF(StringIO(idf_txt))
        
        starting = len(idf.idfobjects['BUILDINGSURFACE:DETAILED'])
        intersect_idf_surfaces(idf)
        ending = len(idf.idfobjects['BUILDINGSURFACE:DETAILED'])
        assert starting == 12
        assert ending == 14
        idf.printidf()
