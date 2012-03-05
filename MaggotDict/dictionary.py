# -*- coding: utf-8 -*-
import json
from os import path

# local
from . import providers
from . import xdg
from .utils import *
from .udb import *
from .udb.bptree import *

__all__ = ('Dictionary',)

CELL_INDEX = 0
CELL_CONFIG = 1
#------------------------------------------------------------------------------#
# Dictionary                                                                   #
#------------------------------------------------------------------------------#
class Dictionary (object):
    def __init__ (self, root, recursive = False, storage_file = None):
        self.disposable = CompositeDisposable ()
        self.root = root

        # discover providers
        self.providers = {}
        for provider_type in providers.All:
            for provider in provider_type.Discover (root, recursive):
                self.providers [provider.Name] = provider
                self.disposable += provider
        
        # open storage
        if storage_file is None:
            storage_file = path.join (xdg.xdg_cache_home, 'maggot-dict.db')
        self.storage = FileSack (storage_file, 'c')
        self.disposable += self.storage

        # open config
        config = self.storage.Cell [CELL_CONFIG].decode ('utf-8')
        if config is None:
            config = {
                'dict_path' : [path.join (xdg.xdg_data_home, 'maggot-dict')],
            }
            self.storage.Cell [CELL_CONFIG] = json.dumps (config).encode ('utf-8')
        else:
            config = json.loads (config)
        self.config = config

        # open index
        self.index = BPTree (BytesProvider (storage, order = 256, cell = CELL_INDEX))

        # open providers
        self.provider = {}
        for provider_type in providers.All:
            for dict_path in config ['dict_path']:
                for provider in provider_type.Discover (dict_path):
                    pass

    #--------------------------------------------------------------------------#
    # Mapping Interface                                                        #
    #--------------------------------------------------------------------------#
    def __getitem__ (self, word):
        if isinstance (word, slice):
            pass

    def __len__ (self):
        return len (self.index)

    #--------------------------------------------------------------------------#
    # Context                                                                  #
    #--------------------------------------------------------------------------#
    def Close (self):
        self.disposable.Dispose ()

    def __enter__ (self):
        return self

    def __exit__ (self, et, eo, tb):
        self.Close ()
        return False

# vim: nu ft=python columns=120 :
