# -*- coding: utf-8 -*-
import io
import sys

__all__ = ('Entry',)
#------------------------------------------------------------------------------#
# Entry                                                                        #
#------------------------------------------------------------------------------#
class Entry (object):
    __slots__ = ('Name', 'Value', 'Children')

    def __init__ (self, name = '', value = None):
        self.Name     = name
        self.Value    = value
        self.Children = []

    #--------------------------------------------------------------------------#
    # Add Child                                                                #
    #--------------------------------------------------------------------------#
    def AddChild (self, name, value = None):
        child = Entry (name, value)
        self.Children.append ((True, child))
        return child

    def AddText (self, text):
        self.Children.append ((False, text))

    #--------------------------------------------------------------------------#
    # Render                                                                   #
    #--------------------------------------------------------------------------#
    def Render (self, renderer):
        """Render entry

        renderer is callable object with signature: Func (is_node:Boolean, node:Entry) -> Generator<Boolen>?
        """

        def render (node):
            for is_node, child in node:
                scope = renderer (is_node, child)
                if scope is None:
                    render (child)
                else:
                    try:
                        if scope.send (None):
                            render (child)
                            scope.send (None)
                    except StopIteration: pass
                    finally:
                        scope.close ()

        render (self)
                    
    #--------------------------------------------------------------------------#
    # Access                                                                   #
    #--------------------------------------------------------------------------#
    def __iter__ (self):
        return iter (self.Children)

    def __len__ (self):
        return len (self.Children)

    def __getitem__ (self, index):
        return self.Children [index]

    def __setitem__ (self, index, child):
        self.Children [index] = child

    #--------------------------------------------------------------------------#
    # Representation                                                           #
    #--------------------------------------------------------------------------#
    def __str__ (self):
        stream = io.StringIO () if sys.version_info [0] > 2 else io.BytesIO ()

        def dump (node, indent = 0):
            stream.write ('{}{{ \'{}{}\' :\n'.format ('  ' * indent, node.Name,
                '' if node.Value is None else ':{}'.format (node.Value)))
            for is_node, child in node:
                if is_node:
                    dump (child, indent + 1)
                else:
                    stream.write ('{}\'{}\'\n'.format ('  ' * (indent + 1), child.replace ('\n', '\\n')))
            stream.write ('{}}}\n'.format ('  ' * indent))
        dump (self)

        return stream.getvalue ()

    __repr__ = __str__

# vim: nu ft=python columns=120 :
