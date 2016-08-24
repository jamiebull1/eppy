# Copyright (c) 2012 Santosh Philip
# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""helpers for pytest"""

import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

RESOURCES_DIR = os.path.join(THIS_DIR, 'resources')

IDD_FILES = os.path.join(RESOURCES_DIR, 'iddfiles')
IDF_FILES = os.path.join(RESOURCES_DIR, 'idffiles')

def almostequal(first, second, places=7):
    """docstring for almostequal"""
    # try converting to float first
    try:
        first = float(first)
        second = float(second)
    except ValueError:
        # handle non-float types
        return str(first) == str(second)
    except TypeError:
        # handle iterables
        return all([a==b for a,b in zip(first, second)])
    # test for equality
    if first == second:
        return True
    # test floats for near-equality
    if round(abs(second-first), places) != 0:
        return False
    else:
        return True


def do_integration_tests():
    """
    Check whether the 'EPPY_INTEGRATION' environment variable has been set to do
    integration tests.
    
    Returns
    -------
    bool
    
    """
    return os.getenv('EPPY_INTEGRATION', False)
