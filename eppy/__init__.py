"""version number"""
__version__ = '0.5.31'
try:
    from eppy.modeleditor import IDF
except ImportError:
    # we hit this  line during setup.py before dependecies have been installed
    pass
