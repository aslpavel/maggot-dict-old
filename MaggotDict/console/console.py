# -*- coding: utf-8 -*-
from ..pretzel.disposable import *

__all__ = ('Console',
    'COLOR_NONE', 'COLOR_BLACK', 'COLOR_RED', 'COLOR_GREEN', 'COLOR_YELLOW', 'COLOR_BLUE', 'COLOR_MAGENTA',
    'COLOR_CYAN','COLOR_WHITE', 'COLOR_DEFAULT', 'ATTR_NONE', 'ATTR_NORMAL', 'ATTR_BOLD', 'ATTR_ITALIC',
    'ATTR_UNDERLINE', 'ATTR_BLINK', 'ATTR_NEGATIVE', 'ATTR_FORCE')
#------------------------------------------------------------------------------#
# Constants                                                                    #
#------------------------------------------------------------------------------#
COLOR_NONE    = 0
COLOR_BLACK   = 1
COLOR_RED     = 2
COLOR_GREEN   = 3
COLOR_YELLOW  = 4
COLOR_BLUE    = 5
COLOR_MAGENTA = 6
COLOR_CYAN    = 7
COLOR_WHITE   = 8
COLOR_DEFAULT = 10

ATTR_NONE      = 0
ATTR_NORMAL    = 1 << 0
ATTR_BOLD      = 1 << 1
ATTR_ITALIC    = 1 << 3
ATTR_UNDERLINE = 1 << 4
ATTR_BLINK     = 1 << 5
ATTR_NEGATIVE  = 1 << 7
ATTR_FORCE     = 1 << 10 # non CSI attribute

#------------------------------------------------------------------------------#
# Console                                                                      #
#------------------------------------------------------------------------------#
class Console (object):
    def __init__ (self, stream, color = None):
        self.stream = stream
        self.color  = stream.isatty () if color is None else color
        self.stack  = [State (COLOR_DEFAULT, COLOR_DEFAULT, ATTR_NORMAL)]
        self.reset_state = State (COLOR_DEFAULT, COLOR_DEFAULT, ATTR_NONE)

    #--------------------------------------------------------------------------#
    # Scope                                                                    #
    #--------------------------------------------------------------------------#
    def Scope (self, fg = 0, bg = 0, attr = 0):
        if self.color:
            self.push (State (fg, bg, attr))
            return Disposable (self.pop)
        else:
            return Disposable ()

    #--------------------------------------------------------------------------#
    # Write                                                                    #
    #--------------------------------------------------------------------------#
    def Write (self, data):
        self.stream.write (data)

    #--------------------------------------------------------------------------#
    # Flush                                                                    #
    #--------------------------------------------------------------------------#
    def Flush (self):
        self.stream.flush ()

    #--------------------------------------------------------------------------#
    # Dispose                                                                  #
    #--------------------------------------------------------------------------#
    def Dispose (self):
        while len (self.stack):
            self.pop ()
        self.Flush ()

    def __enter__ (self):
        return self

    def __exit__ (self, et, eo, tb):
        self.Dispose ()
        return False

    #--------------------------------------------------------------------------#
    # Private                                                                  #
    #--------------------------------------------------------------------------#
    def push (self, new):
        if new.attr & ATTR_FORCE:
            new.attr &= ~ATTR_FORCE 
            new.attr |= ATTR_NORMAL
            curr = self.reset_state
        else:
            curr = self.stack [-1]
            new |= curr
        self.stack.append (new)
        self.stream.write (curr >> new)

    def pop (self):
        curr, new  = self.stack.pop () if len (self.stack) > 1 else self.stack [-1], self.stack [-1]
        self.stream.write (curr >> new)

#------------------------------------------------------------------------------#
# State                                                                        #
#------------------------------------------------------------------------------#
class State (object):
    __slots__ = ('fg', 'bg', 'attr')

    def __init__ (self, fg, bg, attr):
        self.fg, self.bg, self.attr = fg, bg, attr

    #--------------------------------------------------------------------------#
    # Combination                                                              #
    #--------------------------------------------------------------------------#
    def __or__ (self, other):
        return State (
            self.fg if self.fg else other.fg,
            self.bg if self.bg else other.bg,
            self.attr | other.attr)

    def __ior__ (self, other):
        return self | other

    #--------------------------------------------------------------------------#
    # Control Sequence                                                         #
    #--------------------------------------------------------------------------#
    def __rshift__ (self, other):
        """Control sequence to chnage state from 'this' to 'other'"""
        flags = []

        # atributes
        attr_changed = self.attr ^ other.attr
        attr_on, attr_off = other.attr & attr_changed, self.attr & attr_changed
        if attr_off:
            flags.extend (('2%s' % attr) for attr in range (attr_off.bit_length ()) if attr_off & (1 << attr))
        if attr_on:
            flags.extend (('0%s' % attr) for attr in range (attr_on.bit_length ()) if attr_on & (1 << attr))

        # foreground
        if other.fg and other.fg != self.fg:
            flags.append ('3%s' % (other.fg - 1))

        # background
        if other.bg and other.bg != self.bg:
            flags.append ('4%s' % (other.bg - 1))

        return '\x1b[{0}m'.format (';'.join (flags)) if flags else ''

    def __lshift__ (self, other):
        return other >> self

    #--------------------------------------------------------------------------#
    # Representation                                                           #
    #--------------------------------------------------------------------------#
    colors_names = {
        COLOR_NONE    : 'none',
        COLOR_BLACK   : 'black',
        COLOR_RED     : 'red',
        COLOR_GREEN   : 'green',
        COLOR_YELLOW  : 'yellow',
        COLOR_BLUE    : 'blue',
        COLOR_MAGENTA : 'magenta',
        COLOR_CYAN    : 'cyan',
        COLOR_WHITE   : 'white',
        COLOR_DEFAULT : 'default'
    }

    attrs_names =  {
        ATTR_NORMAL    : 'normal',
        ATTR_BOLD      : 'bold',
        ATTR_ITALIC    : 'italic',
        ATTR_UNDERLINE : 'underlined',
        ATTR_BLINK     : 'blink',
        ATTR_NEGATIVE  : 'negative'
    }

    def __repr__ (self):
        return 'fg:{} bg:{} attrs:[{}]'.format (
            self.colors_names [self.fg],
            self.colors_names [self.bg],
            ','.join (self.attrs_names [1 << attr]
                for attr in range (self.attr.bit_length ()) if self.attr & (1 << attr)))

# vim: nu ft=python columns=120 :
