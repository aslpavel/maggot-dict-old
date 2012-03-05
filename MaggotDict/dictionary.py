# -*- coding: utf-8 -*-
import sys
import json
from os import path
from collections import Mapping

# local
from . import providers
from . import xdg
from .utils import *
from .udb import *
from .udb.bptree import *

CELL_INDEX = 0
CELL_CONFIG = 1

__all__ = ('Dictionary',)
#------------------------------------------------------------------------------#
# Dictionary                                                                   #
#------------------------------------------------------------------------------#
class Dictionary (Mapping):
    def __init__ (self, storage_file = None):
        self.disposable = CompositeDisposable ()

        # open storage
        if storage_file is None:
            storage_file = path.join (xdg.xdg_cache_home, 'maggot-dict.db')
        self.storage = FileSack (storage_file, 'c', order = 32) # 4GB storage
        self.disposable += self.storage

        # open config
        config = self.storage.Cell [CELL_CONFIG]
        if config is None:
            config = {
                'dict_path' : [path.join (xdg.xdg_data_home, 'maggot-dict')],
                'last_uid' : 0,
                'providers' : {}, # name -> uid, last_modified
            }
            self.storage.Cell [CELL_CONFIG] = json.dumps (config).encode ('utf-8')
        else:
            config = json.loads (config.decode ('utf-8'))
        self.config = config

        # open index
        self.index = BPTree (PickleProvider (self.storage, order = 256, cell = CELL_INDEX))

        # discover providers
        self.providers = {}
        updated = False
        for provider_type in providers.All:
            for dict_path in config ['dict_path']:
                for provider in provider_type.Discover (dict_path):
                    self.disposable += provider
                    info = config ['providers'].get (provider.Name)
                    if info is None:
                        sys.stderr.write (':: indexing \'{}\'\n'.format (provider.Name))

                        # allocate uid
                        uid = config ['last_uid']; config ['last_uid'] += 1
                        self.providers [uid] = provider

                        # build index
                        count = 0
                        for word, desc in provider:
                            count += 1
                            record = self.index.get (word)
                            if record is None:
                                record = []
                            record.append ((uid, desc))
                            self.index [word] = record
                        self.index.provider.Flush ()

                        # update config
                        config ['providers'] [provider.Name] = (uid, provider.LastModified)
                        updated = True
                    else:
                        uid, last_modified = info
                        if last_modified < provider.LastModified:
                            print (':: TODO: rebuild index')
                            pass
                        else:
                            self.providers [uid] = provider
        if updated:
            self.storage.Cell [CELL_CONFIG] = json.dumps (config).encode ('utf-8')

    #--------------------------------------------------------------------------#
    # Mapping Interface                                                        #
    #--------------------------------------------------------------------------#
    def __len__ (self):
        return len (self.index)

    def __iter__ (self):
        return self.index

    def __getitem__ (self, word):
        if isinstance (word, slice):
            return (Entry (self, word, record) for word, record in self.index [word])
        else:
            return Entry (self, word, self.index [word])

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

#------------------------------------------------------------------------------#
# Entry                                                                        #
#------------------------------------------------------------------------------#
class Entry (object):
    __slots__ = ('owner', 'word', 'record')
    def __init__ (self, owner, word, record):
        self.owner = owner
        self.word = word
        self.record = record

    @property
    def Word (self):
        return self.word

    def __iter__ (self):
        for uid, desc in self.record:
            provider = self.owner.providers [uid]
            yield provider.Name, provider [desc]

# vim: nu ft=python columns=120 :
