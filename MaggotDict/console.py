# -*- coding: utf-8 -*-
from .pretzel.disposable import *

__all__ = ('Console',)
#------------------------------------------------------------------------------#
# Console                                                                      #
#------------------------------------------------------------------------------#
class Console (object):
    __slots__ = ('stream', 'color', 'stack')

    def __init__ (self, stream, color = None):
        self.stream = stream
        self.stack  = []
        self.color  = stream.isatty () if color is None else color

    #--------------------------------------------------------------------------#
    # State                                                                    #
    #--------------------------------------------------------------------------#
    def State (self, fg, bg, attr):
        if self.color:
            self.save (fg, bg, attr)
            return Disposable (self.restore)
        else:
            return Disposable ()

    #--------------------------------------------------------------------------#
    # Write                                                                    #
    #--------------------------------------------------------------------------#
    def Write (self, data):
        self.stream.write (data)

    #--------------------------------------------------------------------------#
    # Dispose                                                                  #
    #--------------------------------------------------------------------------#
    def Dispose (self):
        while len (self.stack):
            self.restore ()

    def __enter__ (self):
        return self

    def __exit__ (self, et, eo, tb):
        self.Dispose ()
        return False

    #--------------------------------------------------------------------------#
    # Private                                                                  #
    #--------------------------------------------------------------------------#
    def update (self, fg, bg, attr):
        self.stream.write ('\x1b[%s;%s;%sm' % (attr, fg, bg))

    def save (self, fg, bg, attr):
        # previous
        fg_prev, bg_prev, attr_prev = self.stack [-1] if self.stack else ('39', '49', '00')
        # inherit
        fg = fg_prev if fg is None else '3%s' % fg 
        bg = bg_prev if bg is None else '4%s' % bg
        attr = attr_prev if attr is None else '0%s' % attr
        # save
        self.stack.append ((fg, bg, attr))
        # update
        self.update (fg, bg, attr)

    def restore (self):
        # resotre
        self.stack.pop ()
        # update
        self.update (*(self.stack [-1] if self.stack else ('39', '49', '00')))

# vim: nu ft=python columns=120 :
