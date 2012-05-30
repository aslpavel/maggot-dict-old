# -*- coding: utf-8 -*-
from gi.repository import Gtk

from .card import *
from .grid import *
from .prefs import *
from .built import *
from .resources import *

from ..pretzel.glib import *
from ..pretzel.async import *
from ..pretzel.observer import *

__all__ = ('MainWindow',)
#------------------------------------------------------------------------------#
# Main Window                                                                  #
#------------------------------------------------------------------------------#
class MainWindow (BuiltObject):
    def __init__ (self, app, dct):
        BuiltObject.__init__ (self, 'main_window')

        # props
        self.app   = app
        self.dct   = dct
        self.cards = {}
        self.prefs = None

        # toolbar
        self.prefs_button.set_icon_widget (Gtk.Image.new_from_pixbuf (ResourceIcon ('cogs', 24)))
        self.prefs_clicked = GEvent (self.prefs_button, 'clicked')


        # entry
        self.entry.set_can_default (True)
        self.entry.grab_default ()
        self.entry_changed     = Observable.FromEvent (GEvent (self.entry, 'changed')).Throttle (self.app.Core, .25)
        self.entry_activate    = GEvent (self.entry, 'activate')
        self.tranlate_clilcked = GEvent (self.translate_button, 'clicked')

        # grid
        self.grid = Grid (app.Core, dct)
        self.grid_box.pack_start (self.grid, True, True, 0)

        # window
        self.window.show_all ()

        # events
        self.entry_activate    += lambda entry: self.ShowCard (self.entry.get_text ())
        self.tranlate_clilcked += lambda button: self.ShowCard (self.entry.get_text ())
        self.prefs_clicked    += lambda button: self.prefs_worker ().Traceback ('preferences worker')
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

    @Async
    def prefs_worker (self):
        if self.prefs is not None:
            self.prefs.window.present ()
            return

        self.prefs = Preferences (self.window)
        try:
            yield self.prefs.OnDelete.Await ()
        finally:
            self.prefs = None
# vim: nu ft=python columns=120 :
