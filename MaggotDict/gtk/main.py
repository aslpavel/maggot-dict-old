# -*- coding: utf-8 -*-
from gi.repository import Gtk

from .resources import *
from .card import *

from ..pretzel.glib import *
from ..pretzel.async import *
from ..pretzel.observer import *

__all__ = ('MainWindow',)
#------------------------------------------------------------------------------#
# Main Window                                                                  #
#------------------------------------------------------------------------------#
class MainWindow (object):
    list_size = 30
    def __init__ (self, app, dct):
        self.app     = app
        self.dct     = dct
        self.cards   = {}

        # build
        self.builder = Gtk.Builder ()
        self.builder.add_from_string (Resources ['main_window_ui'])

        # toolbar
        settings_button = self.builder.get_object ('settings_button')
        settings_button.set_icon_widget (Gtk.Image.new_from_pixbuf (ResourceIcon ('cogs', 24)))

        # word list
        self.list_store = self.builder.get_object ('list_store')
        self.list_map   = {index: self.list_store.append (('',)) for index in range (self.list_size)}
        self.list_fill (self.dct_startswith (''))

        # word list view
        list_view = self.builder.get_object ('list_view')
        def on_selection_changed (selection):
            store, index = selection.get_selected ()
            word = store [index][0]
            word_entry.set_text (word)
        GEvent (list_view.get_selection (), 'changed').Add (on_selection_changed)

        # scroll
        adjust              = self.builder.get_object ('list_adjust')
        self.adjust_changed = Observable.FromEvent (GEvent (adjust, 'value-changed')).Throttle (self.app.Core, .25)
        self.app.Watch (self.adjust_list (), 'scroll worker')

        # entry
        word_entry = self.builder.get_object ('word_entry')
        GEvent (word_entry, 'changed').Add (lambda s: self.list_fill (self.dct_startswith (s.get_text ())))
        GEvent (word_entry, 'activate').Add (lambda s: app.Watch (self.show_card (s), 'show card'))

        # window
        self.window  = self.builder.get_object ('main_window')
        self.window.show_all ()
        self.OnDelete = GEvent (self.window, 'delete-event')

    #--------------------------------------------------------------------------#
    # Private                                                                  #
    #--------------------------------------------------------------------------#
    @Async
    def show_card (self, word_entry):
        word = word_entry.get_text ()
        self.app.Log.Info (word)

        card = self.cards.get (word)
        if card is not None:
            card.window.present ()
            return

        entry = self.dct.get (word)
        if entry is not None:
            card = Card (entry)
            card.OnSound += lambda file: self.app.Log.Debug (file)
            self.cards [word] = card
            yield card.OnDelete.Await ()
            self.cards.pop (word)

    @Async
    def adjust_list (self):
        while True:
            adjust = (yield self.adjust_changed.Await ()) [0]
            word   = self.dct.Scroll (adjust.get_value ()).Word
            self.list_fill (entry.Word for entry in self.dct [word:])

    def list_fill (self, source):
        filled = 0
        for itr, value in zip (self.list_map.values (), source):
            filled += 1
            self.list_store [itr] = (value,)
        for index in range (filled, len (self.list_map)):
            self.list_store [self.list_map [index]] = ('',)

    def dct_startswith (self, text):
        for entry in self.dct [text:]:
            if not entry.Word.startswith (text):
                break
            yield entry.Word

# vim: nu ft=python columns=120 :
