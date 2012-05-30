# -*- coding: utf-8 -*-
from .resources import *
from gi.repository import Gtk

__all__ = ('BuiltObject',)
#------------------------------------------------------------------------------#
# Built Gtk Object                                                             #
#------------------------------------------------------------------------------#
class BuiltObject (object):
    def __init__ (self, name):
        self.name     = name
        self.resource = Resources.get (name + '_ui')
        if self.resource is None:
            raise ValueError ('No such resouce: \'{}\''.format (self.name + '_ui'))

        self.builder = Gtk.Builder ()
        self.builder.add_from_string (self.resource)

    def __getattr__ (self, name):
        instance = self.builder.get_object (name)
        if instance is None:
            raise AttributeError ('No such attribute: \'{}\''.format (name))
        return instance

# vim: nu ft=python columns=120 :
