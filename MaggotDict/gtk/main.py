# -*- coding: utf-8 -*-
from gi.repository import Gtk

from .card import *
from .grid import *
from .resources import *

from ..pretzel.glib import *
from ..pretzel.async import *
from ..pretzel.observer import *

__all__ = ('MainWindow',)
#------------------------------------------------------------------------------#
# Main Window                                                                  #
#------------------------------------------------------------------------------#
class MainWindow (object):
    def __init__ (self, app, dct):
        self.app   = app
        self.dct   = dct
        self.cards = {}

        # build
        self.builder = Gtk.Builder ()
        self.builder.add_from_string (Resources ['main_window_ui'])

        # toolbar
        settings_button = self.builder.get_object ('settings_button')
        settings_button.set_icon_widget (Gtk.Image.new_from_pixbuf (ResourceIcon ('cogs', 24)))

        # entry
        self.entry             = self.builder.get_object ('word_entry')
        self.entry.set_can_default (True)
        self.entry.grab_default ()
        self.entry_changed     = Observable.FromEvent (GEvent (self.entry, 'changed')).Throttle (self.app.Core, .25)
        self.entry_activate    = GEvent (self.entry, 'activate')
        self.tranlate_clilcked = GEvent (self.builder.get_object ('translate_button'), 'clicked')

        # grid
        self.grid = Grid (app.Core, dct)
        grid_box  = self.builder.get_object ('grid_box')
        grid_box.pack_start (self.grid, True, True, 0)

        # window
        self.window  = self.builder.get_object ('main_window')
        self.window.show_all ()

        # events
        self.entry_activate    += lambda entry: self.ShowCard (self.entry.get_text ())
        self.tranlate_clilcked += lambda button: self.ShowCard (self.entry.get_text ())
        self.grid.OnActivated  += self.ShowCard
        self.grid.OnSelected   += lambda word: self.entry.set_text (word)
        self.OnDelete = GEvent (self.window, 'delete-event')

        # workers
        app.Watch (self.entry_changed_worker (), 'entry changed worker')

    #--------------------------------------------------------------------------#
    # Show Card                                                                #
    #--------------------------------------------------------------------------#
    def ShowCard (self, word):
        self.app.Log.Debug ('show card: {}'.format (word))

        # check if shown
        card = self.cards.get (word)
        if card is not None:
            card.window.present ()
            return

        entry = self.dct.get (word)
        if entry is not None:
            # create card
            card = Card (entry)
            self.cards [word] = card

            # events
            card.OnSound  += lambda file: self.app.Log.Debug (file)
            card.OnDelete += lambda card, event: (self.cards.pop (word, None) and False)

    #--------------------------------------------------------------------------#
    # Workers                                                                  #
    #--------------------------------------------------------------------------#
    @Async
    def entry_changed_worker (self):
        while True:
            yield self.entry_changed.Await ()
            if self.entry.get_text () == self.grid.Selected:
                continue
            self.grid.Scroll (self.entry.get_text ())

    #--------------------------------------------------------------------------#
    # Private                                                                  #
    #--------------------------------------------------------------------------#
# vim: nu ft=python columns=120 :
