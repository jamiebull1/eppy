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


class TestIntersectMatch():
    
    @pytest.mark.skipif(
        not do_integration_tests(), reason="$EPPY_INTEGRATION env var not set")
    def test_getidfsurfaces(self):    
        iddfhandle = StringIO(iddcurrent.iddtxt)
        if IDF.getiddname() == None:
            IDF.setiddname(iddfhandle)
        
        idf = IDF(os.path.join(IDF_FILES, 'V8_3_0/test_intersect_match.idf'))
        
        surfaces = getidfsurfaces(idf)
        assert isinstance(surfaces, Idf_MSequence)
        assert len(surfaces) == 12
    
    @pytest.mark.skipif(
        not do_integration_tests(), reason="$EPPY_INTEGRATION env var not set")
    def test_intersect_idf_surfaces(self):       
        iddfhandle = StringIO(iddcurrent.iddtxt)
        if IDF.getiddname() == None:
            IDF.setiddname(iddfhandle)
        
        idf = IDF(os.path.join(IDF_FILES, 'V8_3_0/test_intersect_match.idf'))
        
        starting = len(idf.idfobjects['BUILDINGSURFACE:DETAILED'])
        intersect_idf_surfaces(idf)
        ending = len(idf.idfobjects['BUILDINGSURFACE:DETAILED'])
        assert starting == 12
        assert ending == 14
        idf.printidf()
