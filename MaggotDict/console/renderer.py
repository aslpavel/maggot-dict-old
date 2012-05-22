# -*- coding: utf-8 -*-
from .console import *

__all__ = ('ConsoleEntryRenderer',)
#------------------------------------------------------------------------------#
# Console Entry Renderer                                                       #
#------------------------------------------------------------------------------#
class ConsoleEntryRenderer (object):
    paint = {
        'bold'        : (COLOR_MAGENTA, COLOR_NONE, ATTR_BOLD | ATTR_FORCE),
        'example'     : (COLOR_DEFAULT, COLOR_NONE, ATTR_FORCE),
        'fold'        : (COLOR_BLACK,   COLOR_NONE, ATTR_BOLD),
        'italic'      : (COLOR_NONE,    COLOR_NONE, ATTR_ITALIC),
        'link'        : (COLOR_MAGENTA, COLOR_NONE, ATTR_FORCE),
        'stress'      : (COLOR_NONE,    COLOR_NONE, ATTR_UNDERLINE),
        'transcript'  : (COLOR_GREEN,   COLOR_NONE, ATTR_BOLD | ATTR_FORCE),
        'translation' : (COLOR_WHITE,   COLOR_NONE, ATTR_BOLD),
        'type'        : (COLOR_GREEN,   COLOR_NONE, ATTR_FORCE),
        'underline'   : (COLOR_NONE,    COLOR_NONE, ATTR_UNDERLINE),
    }

    def __init__ (self, console):
        self.console = console

    #--------------------------------------------------------------------------#
    # Renderer Interface                                                       #
    #--------------------------------------------------------------------------#
    def __call__ (self, is_node, node):
        if is_node:
            if node.Name == 'indent':
                self.console.Write ('  ' * node.Value)
            elif node.Name == 'sound':
                with self.console.Scope (COLOR_DEFAULT, COLOR_CYAN, ATTR_BOLD):
                    self.console.Write ('[sound]')
                    yield False
                    return
            else:
                scope = self.paint.get (node.Name)
                if scope:
                    with self.console.Scope (*scope):
                        yield True
                        return
            yield True
        else:
            self.console.Write (node)
            yield False
                
    #--------------------------------------------------------------------------#
    # Disposable                                                               #
    #--------------------------------------------------------------------------#
    def Dispose (self):
        self.console.Flush ()
    
    def __enter__ (self):
        return self
    
    def __exit__ (self, et, eo, tb):
        self.Dispose ()
        return False
# vim: nu ft=python columns=120 :
