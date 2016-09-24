# Copyright (c) 2012 Santosh Philip
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""
Module wrapping esoreader.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from eppy.iddcurrent import iddcurrent
from eppy.modeleditor import IDF
from esoreader import DataDictionary
from esoreader import EsoFile as BaseEsoFile
from six import StringIO

from eppy.results import eso_data


iddfhandle = StringIO(iddcurrent.iddtxt)
if IDF.getiddname() == None:
    IDF.setiddname(iddfhandle)

class EsoFile(BaseEsoFile):
    """Monkeypatched until the patch below is accepted into a new release.
    """
    def __init__(self, *args, **kwargs):
        super(EsoFile, self).__init__(*args, **kwargs)
    
    def _read_data_dictionary(self):
        """parses the head of the eso_file, returning the data dictionary.
        the file object eso_file is advanced to the position needed by
        read_data.
        
        """
        print(help(self.eso_file))
        version, timestamp = [s.strip() for s
                              in self.eso_file.readline().split(',')[-2:]]
        dd = DataDictionary(version, timestamp)
        line = self.eso_file.readline().strip()
        while line != 'End of Data Dictionary':
            line, reporting_frequency = self._read_reporting_frequency(line)
            if reporting_frequency:
                fields = [f.strip() for f in line.split(',')]
                if len(fields) >= 4:
                    id, nfields, key, variable = fields[:4]
                else:
                    id, nfields, variable = fields[:3]
                    key = None
                variable, unit = self._read_variable_unit(variable)
                dd.variables[int(id)] = [reporting_frequency, key,
                                         variable, unit]
            else:
                # ignore the lines that aren't report variables
                pass
            line = self.eso_file.readline().strip()
        dd.ids = set(dd.variables.keys())
        return dd
    

esohandle = StringIO(eso_data.test_results)
results = EsoFile(esohandle)

def test_no_results():
    """Test that idf.results responds with None if no results.
    """
    idf = IDF()
    
    assert idf.results is None


def test_some_results():
    """Test that idf.results responds with something if results are set.
    """
    idf = IDF()
    idf.set_results(results)
    assert idf.results is not None


def test_esoreader_api():
    idf = IDF()
    idf.set_results(results)
    assert idf.results.find_variable('Cooling', frequency='Hourly')
