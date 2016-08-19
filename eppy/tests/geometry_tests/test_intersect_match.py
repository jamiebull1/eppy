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
from geometry.intersect_match import intersect_idf_surfaces


iddsnippet = iddcurrent.iddtxt

iddfhandle = StringIO(iddcurrent.iddtxt)
if IDF.getiddname() == None:
    IDF.setiddname(iddfhandle)

idf = IDF('C:\\Users\\Jamie\\git\\eppy\\eppy\\tests\\geometry_tests\\test_intersect_match.idf')

def test_getidfsurfaces():    
    surfaces = getidfsurfaces(idf)
    assert isinstance(surfaces, Idf_MSequence)
    assert len(surfaces) == 12

def test_intersect_idf_surfaces():
    starting = len(idf.idfobjects['BUILDINGSURFACE:DETAILED'])
    intersect_idf_surfaces(idf)
    ending = len(idf.idfobjects['BUILDINGSURFACE:DETAILED'])
    assert starting == 12
    assert ending == 14
    idf.printidf()
