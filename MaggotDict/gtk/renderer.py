# -*- coding: utf-8 -*-
from collections import deque
from gi.repository import Gtk, Gdk, Pango 

from .resources import *
from ..pretzel.glib import *
from ..pretzel.event import *
from ..pretzel.async import *
from ..pretzel.disposable import *

__all__ = ('GtkEntryRenderer',)
#------------------------------------------------------------------------------#
# Gtk Entry Renderer                                                           #
#------------------------------------------------------------------------------#
class GtkEntryRenderer (object):
    def __init__ (self, view):
        self.view   = view
        self.buffer = view.get_buffer ()

        # scopes
        # a71d5d : violet
        self.scope = Scope (self.buffer, {
            'bold'        : {'weight': Pango.Weight.BOLD},
            'example'     : {'foreground-rgba': ParseColor ('#794938')},
            'fold'        : {'foreground-rgba': ParseColor ('#a9a9a9')},
            'italic'      : {'style': Pango.Style.ITALIC},
            'link'        : {'foreground-rgba': ParseColor ('#6a4ab7')},
            'stress'      : {'underline': Pango.Underline.SINGLE},
            'transcript'  : {'foreground-rgba': ParseColor ('#5a525f')},
            'translation' : {},
            'type'        : {'foreground-rgba': ParseColor ('#0b6125'), 'style': Pango.Style.ITALIC},
            'underline'   : {'underline': Pango.Underline.SINGLE},
        })

        # folds
        self.folded       = True
        self.folds        = []   # mark, node
        self.folds_tags   = None # list of tags inside folds
        self.folds_ranges = None # list of folds ranges (begin_mark, end_mark)

        # sounds
        self.Sounds  = {}

        # resources
        self.sound_icon  = ResourceIcon ('speaker', 10)
        self.link_icon   = ResourceIcon ('link', 10)
        self.hand_cursor = Gdk.Cursor (Gdk.CursorType.HAND1)

        # events
        self.OnSound = Event ()
        self.OnLink  = Event ()

    #--------------------------------------------------------------------------#
    # Renderer Interface                                                       #
    #--------------------------------------------------------------------------#
    def __call__ (self, is_node, node):
        if is_node:
            if node.Name == 'indent':
                self.buffer.insert_at_cursor ('    ' * node.Value)
            elif node.Name == 'sound':
                self.sound_widget (node)
                yield False
                return
            elif node.Name == 'link':
                with self.scope ('link'):
                    yield True
                    self.buffer.insert_at_cursor (' ')
                    self.link_widget (node)
                return
            elif node.Name == 'fold':
                self.folds.append ((CopyMark (self.buffer.get_insert ()), node))
                yield False
                return
            else:
                if node.Name in self.scope:
                    with self.scope (node.Name):
                        yield True
                        return
            yield True
        else:
            self.buffer.insert_at_cursor (node)
            yield False

    #--------------------------------------------------------------------------#
    # Folds                                                                    #
    #--------------------------------------------------------------------------#
    def FoldSet (self, value):
        if value == self.folded:
            return
        self.folded = value

        if value:
            # fold
            table = self.buffer.get_tag_table ()
            for tag in self.folds_tags:
                table.remove (tag)
            self.folds_tags = None

            for begin, end in self.folds_ranges:
                self.buffer.delete (self.buffer.get_iter_at_mark (begin), self.buffer.get_iter_at_mark (end))
                self.buffer.delete_mark (begin)
                self.buffer.delete_mark (end)
            self.folds_ranges = None
        else:
            # unfold
            self.folds_ranges = []
            for mark, node in (self.folds):
                self.buffer.place_cursor (self.buffer.get_iter_at_mark (mark))
                with self.scope ('fold'):
                    node.Render (self)
                self.folds_ranges.append ((CopyMark (mark), CopyMark (self.buffer.get_insert ())))
            self.folds_tags = self.scope.Apply ()

    #--------------------------------------------------------------------------#
    # Disposable                                                               #
    #--------------------------------------------------------------------------#
    def Dispose (self):
        self.scope.Apply ()
    
    def __enter__ (self):
        return self
    
    def __exit__ (self, et, eo, tb):
        self.Dispose ()
        return False

    #--------------------------------------------------------------------------#
    # Private                                                                  #
    #--------------------------------------------------------------------------#
    def sound_widget (self, node):
        # create
        mark   = self.buffer.get_insert ()
        widget = Gtk.EventBox (visible_window = False)
        widget.add (Gtk.Image.new_from_pixbuf (self.sound_icon))
        widget.add_events (Gdk.EventMask.ALL_EVENTS_MASK)
        self.view.add_child_at_anchor (widget, self.buffer.create_child_anchor (
            self.buffer.get_iter_at_mark (mark)))

        # click
        GEvent (widget, 'button-release-event').Add (lambda a, b: self.OnSound (node.Value))
        GEvent (widget, 'motion-notify-event').Add (lambda *args: self.hand_cursor_scope ())

    def link_widget (self, node):
        widget = Gtk.Image.new_from_pixbuf (self.link_icon)
        self.view.add_child_at_anchor (widget, self.buffer.create_child_anchor (
            self.buffer.get_iter_at_mark (self.buffer.get_insert ())))

    def hand_cursor_scope (self):
        window = self.view.get_window (Gtk.TextWindowType.WIDGET)
        if window is None:
            return Disposable ()
        prev_cursor = window.get_cursor ()
        window.set_cursor (self.hand_cursor)
        return Disposable (lambda: window.set_cursor (prev_cursor))
#------------------------------------------------------------------------------#
# Scope                                                                        #
#------------------------------------------------------------------------------#
class Scope (object):
    def __init__ (self, buffer, tags):
        self.tags     = tags
        self.buffer   = buffer

        # tree
        self.tree  = [None, None, None, []]
        self.stack = [self.tree]

        # name -> tags
        self.tag_map = {name : [] for name in self.tags}

    #--------------------------------------------------------------------------#
    # Scope                                                                    #
    #--------------------------------------------------------------------------#
    def __call__ (self, tag_name):
        """Create and enter new scope"""

        if tag_name not in self.tags:
            raise ValueError ('no such tag \'{}\''.format (tag_name))

        begin = CopyMark (self.buffer.get_insert ())

        # open scope
        scope_node = [tag_name, begin, None, []]
        self.stack [-1][3].append (scope_node)
        self.stack.append (scope_node)

        # close scope
        def close_scope ():
            scope_node [2] = CopyMark (self.buffer.get_insert ())
            self.stack.pop ()
        return Disposable (close_scope)

    def Apply (self):
        """Apply created scopes"""

        # apply breadth first traversed tree of tags
        tags  = []
        queue = deque ((self.tree,))
        while queue:
            tag_name, begin, end, scopes = queue.popleft ()

            if begin is not None:
                tag = self.buffer.create_tag (None, **self.tags [tag_name])
                tags.append (tag)
                self.tag_map [tag_name].append (tag)
                self.buffer.apply_tag (tag,
                        self.buffer.get_iter_at_mark (begin),
                        self.buffer.get_iter_at_mark (end))
                self.buffer.delete_mark (begin)
                self.buffer.delete_mark (end)

            for scope in scopes:
                queue.append (scope)

        # reset scope tree
        self.tree  = [None, None, None, []]
        self.stack = [self.tree]

        return tags

    #--------------------------------------------------------------------------#
    # Access Tags                                                              #
    #--------------------------------------------------------------------------#
    def __contains__ (self, tag_name):
        return tag_name in self.tags

    def __getitem__ (self, tag_name):
        return iter (self.tag_map [tag_name])

#------------------------------------------------------------------------------#
# Copy Text Mark                                                               #
#------------------------------------------------------------------------------#
def CopyMark (mark, left_gravity = True):
    buffer = mark.get_buffer ()
    return buffer.create_mark (None, buffer.get_iter_at_mark (mark), left_gravity)

#------------------------------------------------------------------------------#
# Parse Color                                                                  #
#------------------------------------------------------------------------------#
def ParseColor (color_string):
    color = Gdk.RGBA ()
    if not Gdk.RGBA.parse (color, color_string):
        raise ValueError ('Bad color string: \'{}\''.format (color_string))
    return color

# vim: nu ft=python columns=120 :
