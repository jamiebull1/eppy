import os

import pytest

from eppy import modeleditor
from eppy.tests.test_runner import versiontuple

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

RESOURCES_DIR = os.path.join(THIS_DIR, os.pardir, 'resources')

IDD_FILES = os.path.join(RESOURCES_DIR, 'iddfiles')
IDF_FILES = os.path.join(RESOURCES_DIR, 'idffiles')
try:
    VERSION = os.environ["ENERGYPLUS_INSTALL_VERSION"]  # used in CI files
except KeyError:
    VERSION = '8-9-0'  # current default for integration tests on local system
TEST_IDF = "V{}/smallfile.idf".format(VERSION[:3].replace('-', '_'))
TEST_EPW = 'USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw'
TEST_IDD = "Energy+V{}.idd".format(VERSION.replace('-', '_'))
TEST_OLD_IDD = 'Energy+V7_2_0.idd'


@pytest.fixture()
def test_idf():
    idd_file = os.path.join(IDD_FILES, TEST_IDD)
    idf_file = os.path.join(IDF_FILES, TEST_IDF)
    modeleditor.IDF.setiddname(idd_file, testing=True)
    idf = modeleditor.IDF(idf_file, TEST_EPW)
    try:
        ep_version = idf.idd_version
        assert ep_version == versiontuple(VERSION)
    except AttributeError:
        raise
    return idf
