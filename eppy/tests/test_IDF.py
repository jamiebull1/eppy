# Copyright (c) 2012 Santosh Philip
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""py.test for class IDF"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from eppy import IDF
from eppy.idf_msequence import Idf_MSequence


class TestIDFNew(object):

    def test_IDF_new(self):
        """
        py.test for creating a blank IDF with the simple constructor.
        """
        idf = IDF()
        empty_idf_msequence = Idf_MSequence([], [], None)
        assert idf.idfobjects["ZONE"] == empty_idf_msequence


    def test_get_set_iddname(self):
        """py.test for class IDF"""
        stored_idd = IDF.iddname
        IDF.iddname = None
        assert IDF.iddname == None
        IDF.setiddname("gumby", testing=True)
        assert IDF.iddname == "gumby"
        IDF.setiddname("karamba", testing=True)
        assert IDF.iddname != "karamba"
        assert IDF.iddname == "gumby"
        IDF.iddname = stored_idd


class TestIDF(object):

    """py.test for IDF function"""

    def test_removeidfobject(self):
        """py.test for IDF.removeidfobject """
        idf = IDF()
        key = "BUILDING"
        idf.newidfobject(key, Name="Building_remove")
        idf.newidfobject(key, Name="Building1")
        idf.newidfobject(key, Name="Building_remove")
        idf.newidfobject(key, Name="Building2")
        buildings = idf.idfobjects["building".upper()]
        removethis = buildings[-2]
        idf.removeidfobject(removethis)
        assert buildings[2].Name == "Building2"
        assert idf.model.dt[key][2][1] == "Building2"

    def test_popidfobject(self):
        idf = IDF()
        key = "BUILDING"
        idf.newidfobject(key, Name="Building_remove")
        idf.newidfobject(key, Name="Building1")
        idf.newidfobject(key, Name="Building_remove")
        idf.newidfobject(key, Name="Building2")
        buildings = idf.idfobjects["building".upper()]
        removethis = buildings[-2]
        idf.popidfobject(key, 2)
        assert buildings[2].Name == "Building2"
        assert idf.model.dt[key][2][1] == "Building2"
