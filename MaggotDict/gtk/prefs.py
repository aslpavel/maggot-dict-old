# -*- coding: utf-8 -*-
from .built import *

from ..pretzel.glib import *
from ..pretzel.event import *

from gi.repository import Gtk

__all__ = ('Preferences',)
#------------------------------------------------------------------------------#
# Preferences                                                                  #
#------------------------------------------------------------------------------#
class Preferences (BuiltObject):
    def __init__ (self, main_window):
        BuiltObject.__init__ (self, 'prefs_window')

        # events
        self.OnDelete = Event ()

        # events handlers
        GEvent (self.ok_button, 'clicked').Add (lambda button: (
            self.window.destroy (),
            self.OnDelete ()))
        GEvent (self.window, 'delete-event').Add (lambda *args: self.OnDelete ())

        # window
        self.window.set_transient_for (main_window)
        self.window.show_all ()

# vim: nu ft=python columns=120 :
