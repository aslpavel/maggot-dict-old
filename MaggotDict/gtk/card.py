# -*- coding: utf-8 -*-
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
class Card (object):
    def __init__ (self, entry):
        # build
        self.builder = Gtk.Builder ()
        self.builder.add_from_string (Resources ['card_window_ui'])
        self.view   = view   = self.builder.get_object ('view')
        self.buffer = buffer = self.builder.get_object ('buffer')
        # tags
        self.word_tag = buffer.create_tag (None, weight = Pango.Weight.BOLD)
        self.name_tag = buffer.create_tag (None, justification = Gtk.Justification.RIGHT,
            foreground = 'dark grey')

        # render
        headers  = []
        first    = True
        renderer = GtkEntryRenderer (view)
        with renderer:
            for provider_name, provider_entry in entry:
                self.header_create (entry.Word, provider_name)
                provider_entry.Render (renderer)
                buffer.insert_at_cursor ('\n')

        # folds
        fold_toggle = self.builder.get_object ('fold_toggle')
        fold_toggle.set_icon_widget (Gtk.Image.new_from_pixbuf (ResourceIcon ('upload', 24)))
        GEvent (fold_toggle, 'toggled').Add (lambda toggle: renderer.FoldSet (not toggle.get_active ()))

        # debug
        debug = self.builder.get_object ('debug')
        debug.set_icon_widget (Gtk.Image.new_from_pixbuf (ResourceIcon ('edit', 24)))
        def on_debug (source):
            for n, e in entry:
                print (n)
                print (e)
        GEvent (debug, 'clicked').Add (on_debug)

        # show
        self.window = self.builder.get_object ('window')
        self.window.set_title (entry.Word)
        self.window.show_all ()

        # event
        self.OnDelete = GEvent (self.window, 'delete-event')
        self.OnSound  = renderer.OnSound

    #--------------------------------------------------------------------------#
    # Private                                                                  #
    #--------------------------------------------------------------------------#
    def separator_create (self, anchor):
        return
        separator  = Gtk.Separator ()
        (GEvent (self.view, 'size-allocate')
            .Add (lambda source, rect: separator.set_size_request (rect.width - 10, 5)))
        self.view.add_child_at_anchor (separator, anchor)

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

        """
        # provider
        rect  = self.view.get_iter_location (get_insert_iter ())
        label = Gtk.Label (label = name)  
        self.view.add_child_in_window (label, Gtk.TextWindowType.WIDGET, rect.x, rect.y)

        anchor = buffer.create_child_anchor (get_insert_iter ())
        label  = Gtk.Label (label = provider_name)  
        view.add_child_at_anchor (label, anchor)
        # view_allocate.Add (lambda s, r: label.set_size_request ())
        """

    """
    def header_create (self, name, mark):
        # view
        def mark_location ():
            rect = self.view.get_iter_location  (self.buffer.get_iter_at_mark (mark))
            return self.view.buffer_to_window_coords (Gtk.TextWindowType.WIDGET, rect.x, rect.y)

        # header
        sep   = Gtk.Separator (height_request = 5)
        label = Gtk.Label (label = name, halign = Gtk.Align.END)
        box   = Gtk.Box (orientation = Gtk.Orientation.VERTICAL, valign = Gtk.Align.START, margin = 3)
        box.pack_start (sep, False, False, 0)
        box.pack_start (label, False, False, 0)

        # overlay
        overlay = self.builder.get_object ('view_overlay')
        overlay.add_overlay (box)
        overlay.override_background_color (Gtk.StateFlags.NORMAL, Gdk.RGBA (0, 0, 0, 0))
        def on_overlay_event (overlay, widget, rect):
            print (overlay, widget)
            rect.x, rect.y = 50, 50
            rect.width, rect.height = 300, 100
            print (mark_location ())
            return rect
        overlay.connect ('get-child-position', on_overlay_event)
    """

# vim: nu ft=python columns=120 :
