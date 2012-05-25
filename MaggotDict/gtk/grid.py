# -*- coding: utf-8 -*-
from ..pretzel.glib import *
from ..pretzel.async import *
from ..pretzel.event import *
from ..pretzel.observer import *

from gi.repository import Gtk
__all__ = ('Grid',)
#------------------------------------------------------------------------------#
# Grid                                                                         #
#------------------------------------------------------------------------------#
class Grid (Gtk.Box):
    store_size = 32

    def __init__ (self, core, dct):
        Gtk.Box.__init__ (self)
        self.core = core
        self.dct  = dct

        # widgets
        self.store     = Gtk.ListStore (str)
        self.view      = Gtk.TreeView (model = self.store)
        self.selection = self.view.get_selection ()
        self.adjust    = Gtk.Adjustment (lower = 0, upper = len (dct))
        self.scroll    = Gtk.Scrollbar (orientation = Gtk.Orientation.VERTICAL, adjustment  = self.adjust)

        # init
        self.view.append_column (Gtk.TreeViewColumn ('Word', Gtk.CellRendererText (), text = 0))
        self.store_map = {index: self.store.append (('',)) for index in range (self.store_size)}

        # pack
        self.pack_start (self.view, True, True, 0)
        self.pack_start (self.scroll, False, False, 0)

        # events
        self.OnActivated = Event ()
        self.OnSelected  = Event ()
        self.adjust_changed = Observable.FromEvent (GEvent (self.adjust, 'value-changed')).Throttle (core, .25)

        GEvent (self.view, 'row-activated').Add (lambda source, path, column: self.OnActivated (self.store [path][0]))
        GEvent (self.selection, 'changed').Add (lambda selection: self.OnSelected (self.Selected))

        # start
        self.Scroll ('')
        self.adjust_changed_worker ().Traceback ('adjust changed')

    #--------------------------------------------------------------------------#
    # Scroll                                                                   #
    #--------------------------------------------------------------------------#
    def Scroll (self, value):
        filled, index = 0, None
        for itr, entry in zip (self.store_map.values (), self.dct [value:]):
            if index is None:
                index = entry.Index
            self.store [itr] = (entry.Word,)
            filled += 1
        for index in range (filled, self.store_size):
            self.store [self.store_map [index]] = ('',)
        self.view.set_cursor (0)
        self.adjust.set_value (index)

    @property
    def Selected (self):
        store, index = self.selection.get_selected ()
        return store [index][0]

    #--------------------------------------------------------------------------#
    # Workers                                                                  #
    #--------------------------------------------------------------------------#
    @Async
    def adjust_changed_worker (self):
        while True:
            yield self.adjust_changed.Await ()
            entry = self.dct.FindByIndex (int (self.adjust.get_value ()))
            self.adjust.freeze_notify ()
            self.Scroll (entry.Word)
            self.adjust.thaw_notify ()

# vim: nu ft=python columns=120 :