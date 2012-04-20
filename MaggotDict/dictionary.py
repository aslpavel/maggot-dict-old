# -*- coding: utf-8 -*-
import sys
import json
import itertools
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

CELL_INDEX  = 0
CELL_LOG    = 1
CELL_CONFIG = 2

__all__ = ('Dictionary',)
#------------------------------------------------------------------------------#
# Dictionary                                                                   #
#------------------------------------------------------------------------------#
class Dictionary (Mapping):
    dict_path = [path.join (xdg.xdg_data_home, 'maggot-dict')]
    dict_path.extend (path.join (data_path, 'maggot-dict') for data_path in xdg.xdg_data_dirs)

    def __init__ (self, db_file = None, logger = None):
        self.log = Log ('dict')
        self.disposable = CompositeDisposable ()

        # attatch logger
        if logger is not None:
            self.log.Subscribe (logger)

        # open db
        if db_file is None:
            db_file = path.join (xdg.xdg_cache_home, 'maggot-dict.db')
        self.db = xDB (db_file, 'c')
        self.disposable += self.db

        # open config
        self.config = SackConfig (self.db.Sack, CELL_CONFIG, lambda: {
            'dict_path' : [],
            'providers' : {}, # name -> uid
        })

        # open index
        self.index = self.db.Table (CELL_INDEX, type = 'PP', flags = FLAG_COMPRESSION)

        # providers
        self.providers = {}
        updated = False
        for provider_type in providers.All:
            for dict_path in itertools.chain (self.dict_path, self.config.dict_path):
                if not path.isdir (path.realpath (dict_path)):
                    continue
                for provider in provider_type.Discover (dict_path):
                    self.disposable += provider

                    # get config
                    config = self.config.providers.Get (provider.Name, None)
                    if config is None:
                        config = self.bind (provider)
                        updated = True

                    # update mapping
                    self.providers [config.uid] = provider

        # clean index
        uids = []
        for name, config in self.config.providers.Items ():
            if config.uid not in self.providers:
                uids.append (config.uid)
        if uids:
            self.unbind (uids)
            updated = True

        # flush db
        if updated:
            self.index.Flush ()
            self.config.Flush ()

    #--------------------------------------------------------------------------#
    # Properties                                                               #
    #--------------------------------------------------------------------------#
    @property
    def Log (self):
        return self.log

    #--------------------------------------------------------------------------#
    # Mapping Interface                                                        #
    #--------------------------------------------------------------------------#
    def __len__ (self):
        return len (self.index)

    def __iter__ (self):
        for word, record in self.index.items ():
            yield Entry (self, word, record)

    def __getitem__ (self, word):
        if isinstance (word, slice):
            return (Entry (self, word, record) for word, record in self.index [word])
        else:
            return Entry (self, word, self.index [word])

    #--------------------------------------------------------------------------#
    # Private                                                                  #
    #--------------------------------------------------------------------------#
    def bind (self, provider):
        # allocate uid
        uid, uid_mask = 0, 0
        for name, config in self.config.providers.Items ():
            uid_mask |= 1 << config.uid
        for uid in itertools.count ():
            if not ((1 << uid) & uid_mask):
                break

        # update index
        count = 0
        with self.log.Progress (provider.Name) as progress:
            progress ('0')

            for word, desc in provider:
                record = self.index.get (word)
                if record is None:
                    record = {}
                record [uid] = desc
                self.index [word] = record

                # update progress
                count += 1
                if not count % 100:
                    progress (str (count))

        # update config
        self.config.providers [provider.Name] = {'uid' : uid}

        return self.config.providers [provider.Name]

    def unbind (self, uids):
        with self.log.Pending ('unbinding uids: {}'.format (list (uids))):
            # update index
            empty = []
            for entry in self:
                changed = False
                for uid in uids:
                    changed = True
                    entry.record.pop (uid, None)
                if changed:
                    if not entry.record:
                        empty.append (entry.Word)
                    else:
                        self.index [entry.Word] = entry.record

            import pdb; pdb.set_trace ()
            for word in empty:
                del self.index [word]

            # update config
            names = []
            for name, config in self.config.providers.Items ():
                if config.uid in uids:
                    names.append (name)
            for name in names:
                del self.config.providers [name]

    #--------------------------------------------------------------------------#
    # Dispose                                                                  #
    #--------------------------------------------------------------------------#
    def Dispose (self):
        self.disposable.Dispose ()

    def __enter__ (self):
        return self

    def __exit__ (self, et, eo, tb):
        self.Dispose ()
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
        for uid, desc in self.record.items ():
            provider = self.owner.providers [uid]
            yield provider.Name, provider [desc]

# vim: nu ft=python columns=120 :
