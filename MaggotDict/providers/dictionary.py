# -*- coding: utf-8 -*-
import io
import os
import struct
from os import path

__all__ = ('DictProvider',)
#------------------------------------------------------------------------------#
# Dict Provider                                                                #
#------------------------------------------------------------------------------#
class DictProvider (object):
    data_suffix  = '.dict'
    index_suffix = '.idx'
    buffer_size  = 1 << 16 # 64KB

    def __init__ (self, data_file, index_file):
        self.data_file, self.index_file = data_file, index_file
        self.name = path.basename (self.data_file [:-len (self.data_suffix)])
        self.data_stream = open (data_file, 'rb', self.buffer_size)

    @property
    def Name (self):
        return self.name

    @property
    def LastModified (self):
        return os.stat (self.index_file).st_mtime

    def DescEnumerate (self):
        """Enumerate over all available word, descriptor pairs"""
        desc_struct = struct.Struct ('!2I')
        with open (self.index_file, 'rb', self.buffer_size) as index_stream:
            data = b''
            while True:
                # read chunk
                chunk = index_stream.read (self.buffer_size)
                if not chunk:
                    break
                data += chunk

                # parse
                start = 0
                while True:
                    end = data.find (b'\x00', start)
                    if end < 0:
                        break
                    word = data [start:end]
                    start = end + desc_struct.size + 1
                    if start > len (data):
                        break
                    desc = desc_struct.unpack (data [end + 1:start])
                    yield word, desc

                # copy tail
                data = data [start:]
                    
    def __getitem__ (self, desc):
        """Get data by it's descriptor"""
        offset, size = desc
        self.data_stream.seek (offset)
        return self.data_stream.read (size)

    #--------------------------------------------------------------------------#
    # Context                                                                  #
    #--------------------------------------------------------------------------#
    def Close (self):
        self.data_stream.close ()

    def __enter__ (self):
        return self

    def __exit__ (self, et, eo, tb):
        self.Close ()
        return False

    #--------------------------------------------------------------------------#
    # Discover                                                                 # 
    #--------------------------------------------------------------------------#
    @classmethod
    def Discover (cls, root, recursive = False):
        def find_dict (root, files):
            for data_name in files:
                if not data_name.lower ().endswith (cls.data_suffix):
                    continue
                data_file = path.join (root, data_name)
                index_file = path.join (root, data_name [:-len (cls.data_suffix)] + cls.index_suffix)
                if not path.isfile (data_file) or not path.isfile (index_file):
                    continue
                yield data_file, index_file

        if recursive:
            for root, dirs, files in os.walk (root):
                for data, index in find_dict (root, files):
                    yield cls (data, index)
        else:
            for data, index in find_dict (root, os.listdir (root)):
                yield cls (data, index)
                   
# vim: nu ft=python columns=120 :
