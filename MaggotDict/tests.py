# -*- coding: utf-8 -*-
import unittest

from .fenwick import *
#------------------------------------------------------------------------------#
# Fenwicki                                                                     #
#------------------------------------------------------------------------------#
class FenwickTest (unittest.TestCase):
    def testSimple (self):
        sum = [0] * 1024
        fs  = FenwickSum (len (sum))

        # init
        count = 0
        for index in range (len (sum)):
            count += index
            sum [index] = count
            fs.Add (index, index)

        for index, value in enumerate (sum):
            self.assertEqual (fs [index], value)

# vim: nu ft=python columns=120 :
