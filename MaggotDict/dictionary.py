# -*- coding: utf-8 -*-
import sys
import json
from os import path
from collections import Mapping

# local
from . import providers
from . import xdg

# pretzel
from .pretzel.log import *
from .pretzel.config import *
from .pretzel.udb import *
from .pretzel.udb.bptree import *
from .pretzel.disposable import *

CELL_INDEX = 0
CELL_CONFIG = 1

__all__ = ('Dictionary',)
#------------------------------------------------------------------------------#
# Dictionary                                                                   #
#------------------------------------------------------------------------------#
class Dictionary (Mapping):
    def __init__ (self, storage_file = None, logger = None):
        # init logger
        self.log = Log ('dictionary')
        if logger is not None:
            self.log.Subscribe (logger)

        self.disposable = CompositeDisposable ()

        # open storage
        if storage_file is None:
            storage_file = path.join (xdg.xdg_cache_home, 'maggot-dict.db')
        self.storage = FileSack (storage_file, 'c', order = 32) # 4GB storage
        self.disposable += self.storage

        # open config
        self.config = SackConfig (self.storage, CELL_CONFIG, lambda: {
            'dict_path' : [path.join (xdg.xdg_data_home, 'maggot-dict')],
            'last_uid' : 0,
            'providers' : {}, # name -> uid, last_modified
        })

        # open index
        self.index = BPTree (SackProvider (self.storage, order = 256, type = 'PP', cell = CELL_INDEX))

        # discover providers
        self.providers = {}
        updated = False
        for provider_type in providers.All:
            for dict_path in self.config.dict_path:
                for provider in provider_type.Discover (dict_path):
                    self.disposable += provider
                    info = getattr (self.config.providers, provider.Name, None)
                    if info is None:
                        # allocate uid
                        uid, self.config.last_uid = self.config.last_uid, self.config.last_uid + 1
                        self.providers [uid] = provider

                        # build index
                        count = 0
                        with self.log.Progress (provider.Name) as progress:
                            progress ('0')
                            for word, desc in provider:
                                count += 1
                                if count % 100 == 0:
                                    progress (str (count))
                                record = self.index.get (word)
                                if record is None:
                                    record = []
                                record.append ((uid, desc))
                                self.index [word] = record
                            self.index.provider.Flush ()

                        # update config
                        setattr (self.config.providers, provider.Name, [uid, provider.LastModified])
                        updated = True
                    else:
                        uid, last_modified = info
                        if last_modified < provider.LastModified:
                            print (':: TODO: rebuild index')
                            pass
                        else:
                            self.providers [uid] = provider
        if updated:
            self.config.Flush ()

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
