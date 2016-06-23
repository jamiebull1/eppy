# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""py.test for thermal_properties.py"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from StringIO import StringIO

from eppy.iddcurrent import iddcurrent
from eppy.modeleditor import IDF

from constructions.thermal_properties import INSIDE_FILM_R
from constructions.thermal_properties import OUTSIDE_FILM_R


iddsnippet = iddcurrent.iddtxt
iddfhandle = StringIO(iddsnippet)


if IDF.getiddname() == None:
    IDF.setiddname(iddfhandle)

single_layer = """
  Construction,
    TestConstruction,                       !- Name
    TestMaterial;                           !- Inside Layer
  Material,
    TestMaterial,
    Rough,                   !- Roughness
    0.10,                     !- Thickness {m}
    0.5,    !- Conductivity {W/m-K}
    1000.0,                 !- Density {kg/m3}
    1200,    !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.6,                     !- Solar Absorptance
    0.6;                     !- Visible Absorptance
    """

class TestThermalProperties(object):
    
    idf = IDF()
    idf.initreadtxt(single_layer)

    def test_rvalue_construction(self):
        idf = self.idf
        construction = idf.getobject('CONSTRUCTION', 'TestConstruction')
        layers = construction.obj[2:]
        rvalue = sum(idf.getobject('MATERIAL', l).rvalue for l in layers)
        rvalue += INSIDE_FILM_R + OUTSIDE_FILM_R
        assert rvalue == 0.35
    
    def test_rvalue_material(self):
        idf = self.idf
        material = idf.getobject('MATERIAL', 'TestMaterial')
        rvalue = material.Thickness / material.Conductivity
        assert rvalue == 0.2
        assert material.rvalue == 0.2
        
    



        