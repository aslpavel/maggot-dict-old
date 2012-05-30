# -*- coding: utf-8 -*-
from .built import *
from .resources import *
from .renderer  import *

from ..pretzel.glib import *
from ..pretzel.event import *
from ..pretzel.async import *
from ..pretzel.disposable import *

from gi.repository import Gtk, Gdk, Pango

__all__ = ('Card',)
#------------------------------------------------------------------------------#
# Card                                                                         #
#------------------------------------------------------------------------------#
class Card (BuiltObject):
    def __init__ (self, entry):
        BuiltObject.__init__ (self, 'card_window')

        # tags
        self.word_tag = self.buffer.create_tag (None, weight = Pango.Weight.BOLD)
        self.name_tag = self.buffer.create_tag (None, justification = Gtk.Justification.RIGHT,
            foreground = 'dark grey')

        # render
        headers  = []
        first    = True
        renderer = GtkEntryRenderer (self.view)
        with renderer:
            for provider_name, provider_entry in entry:
                self.header_create (entry.Word, provider_name)
                provider_entry.Render (renderer)
                self.buffer.insert_at_cursor ('\n')

        # folds
        self.fold_toggle.set_icon_widget (Gtk.Image.new_from_pixbuf (ResourceIcon ('upload', 24)))
        GEvent (self.fold_toggle, 'toggled').Add (lambda toggle: renderer.FoldSet (not toggle.get_active ()))

        # debug
        self.debug.set_icon_widget (Gtk.Image.new_from_pixbuf (ResourceIcon ('edit', 24)))
        def on_debug (source):
            for n, e in entry:
                print (n)
                print (e)
        GEvent (self.debug, 'clicked').Add (on_debug)

        # show
        self.window.set_title (entry.Word)
        self.window.show_all ()

        # event
        self.OnDelete = GEvent (self.window, 'delete-event')
        self.OnSound  = renderer.OnSound

    #--------------------------------------------------------------------------#
    # Private                                                                  #
    #--------------------------------------------------------------------------#
    def header_create (self, word, name):
        get_insert_iter = lambda: self.buffer.get_iter_at_mark (self.buffer.get_insert ())

        # separator
        anchor    = self.buffer.create_child_anchor (get_insert_iter ())
        separator = Gtk.Separator ()
        self.view.add_child_at_anchor (separator, anchor)
        GEvent (self.view, 'size-allocate').Add (lambda s, r: separator.set_size_request (r.width - 10, 5))

        # header
        self.buffer.insert_with_tags (get_insert_iter (), '\n{}'.format (name), self.name_tag)
        self.buffer.insert_with_tags (get_insert_iter (), '\n{}\n'.format (word), self.word_tag)

# vim: nu ft=python columns=120 :
