#! /usr/bin/env python
import array
import zlib

__all__ = ('FenwickSum',)
#------------------------------------------------------------------------------#
# Fenwick Sum                                                                  #
#------------------------------------------------------------------------------#
class FenwickSum (object):
    def __init__ (self, size):
        self.table = array.array ('I', (0 for i in range (size)))

    #--------------------------------------------------------------------------#
    # Add                                                                      #
    #--------------------------------------------------------------------------#
    def Add (self, index, value):
        if not value:
            return self

        while index < len (self.table):
            self.table [index] += value 
            index |= index + 1
        return self

    #--------------------------------------------------------------------------#
    # Value                                                                    #
    #--------------------------------------------------------------------------#
    def Value (self, index):
        result  = 0
        while index >= 0:
            result += self.table [index]
            index   = (index & (index + 1)) - 1
        return result

    def __getitem__ (self, index):
        return self.Value (index)

    #--------------------------------------------------------------------------#
    # Size                                                                     #
    #--------------------------------------------------------------------------#
    def __len__ (self):
        return len (self.table)

    #--------------------------------------------------------------------------#
    # Dump | Load                                                              #
    #--------------------------------------------------------------------------#
    def Dump (self):
        return zlib.compress (self.table.tostring ())

    @classmethod
    def Load (cls, data):
        table = array.array ('I')
        table.fromstring (zlib.decompress (data))
        fenwick_sum = cls (0)
        fenwick_sum.table = table
        return fenwick_sum

# vim: nu ft=python columns=120 :
