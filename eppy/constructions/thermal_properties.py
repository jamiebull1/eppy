# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""Functions to calculate the thermal properties of constructions.
"""

INSIDE_FILM_R = 0.12
OUTSIDE_FILM_R = 0.03


def rvalue(ddtt):
    """thickness (m) / conductivity (W/m-K)"""
    if ddtt.obj[0] == 'Material':
        thickness = ddtt.obj[ddtt.objls.index('Thickness')]
        conductivity = ddtt.obj[ddtt.objls.index('Conductivity')]
        rvalue = thickness / conductivity
        return rvalue
    else:
        rvalue = 0
        for material in ddtt.obj[2:]:
            rvalue += material.rvalue


def uvalue(ddtt):
    pass

def heatcapacity(ddtt):
    pass