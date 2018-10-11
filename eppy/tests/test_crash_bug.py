import os
import shutil
import sys

import pytest

from eppy.modeleditor import IDF
from eppy.runner.run_functions import paths_from_version, EnergyPlusRunError

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

RESOURCES_DIR = os.path.join(THIS_DIR, os.pardir, 'resources')

IDD_FILES = os.path.join(RESOURCES_DIR, 'iddfiles')
IDF_FILES = os.path.join(RESOURCES_DIR, 'idffiles')


@pytest.mark.xfail
def test_reproduce_i204():
    """This test is not failing. Perhaps if we had the actual files it would."""
    idfname = os.path.join(IDF_FILES, "V8_9/AirCooledElectricChiller.idf")
    _, eplus_home = paths_from_version("8-9-0")
    epwfile = os.path.join(eplus_home, "WeatherData/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")
    idf = IDF(idfname, epwfile)
    try:
        with pytest.raises(EnergyPlusRunError):
            idf.run(output_directory="test_dir", ep_version="8-9-0")
    except Exception:
        raise
    finally:
        shutil.rmtree("test_dir", ignore_errors=True)
