# -*- coding: utf-8 -*-
from .dictionary import *
from .console import *

__all__ = ('Dictionary', 'Console',)

#------------------------------------------------------------------------------#
# Load Test Protocol                                                           #
#------------------------------------------------------------------------------#
def load_tests (loader, tests, pattern):
    import unittest
    from . import pretzel
    from . import tests

    suite = unittest.TestSuite ()
    for test in (tests, pretzel):
        suite.addTests (loader.loadTestsFromModule (test))

    return suite

# vim: nu ft=python columns=120 :
