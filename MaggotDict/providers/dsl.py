# -*- coding: utf-8 -*-
import os
import re
import io
import codecs
import itertools
from os import path

from ..console import *

__all__ = ('DslProvider',)
#------------------------------------------------------------------------------#
# Lingvo DSL Provider                                                          #
#------------------------------------------------------------------------------#
class DslProvider (object):
    file_suffix = '.dsl'
    name_pattern  = re.compile (r'^#NAME\s*"([^"]*).*') # dictionary name
    word_pattern  = re.compile (r'^[^\s]')              # beginning of word
    del_pattern   = re.compile (r'\{[^}]*\}')           # delete part of word
    sub_pattern   = re.compile (r'\(([^)]*)\)')         # alternative part of word
    space_pattern = re.compile (r'(\s)\s+')             # double space pattern
    
    buffer_size = 1 << 16

    def __init__ (self, file):
        # open stream
        self.name = file [:-len (self.file_suffix)]
        self.stream = open (file, 'rb', buffering = self.buffer_size)

        # determine encoding
        bom = self.stream.read (2)
        if bom == codecs.BOM_UTF16_BE:
            self.decode = codecs.getdecoder ('utf-16be')
            self.newline = '\r\n'.encode ('utf-16be')
        elif bom == codecs.BOM_UTF16_LE:
            self.decode = codecs.getdecoder ('utf-16le')
            self.newline = '\r\n'.encode ('utf-16le')
        else:
            self.stream.seek (0)
            self.decode = codecs.getdecoder ('utf-16')
            self.newline = '\r\n'.encode ('utf-16')
        self.offset = self.stream.tell ()

        # parse headers
        for header, offset in self.lines (offset = 2):
            if not header.startswith ('#'):
                break
            self.offset = offset
            match = self.name_pattern.search (header)
            if match:
                self.name = match.group (1)

    #--------------------------------------------------------------------------#
    # Properties                                                               #
    #--------------------------------------------------------------------------#
    @property
    def Name (self):
        return self.name

    @property
    def LastModified (self):
        return os.stat (self.stream.name).st_mtime

    #--------------------------------------------------------------------------#
    # Provider                                                                 #
    #--------------------------------------------------------------------------#
    def __iter__ (self):
        words, card_begin, card_end = set (), 0, 0
        for line, offset in self.lines (self.offset):
            word_match = self.word_pattern.search (line)
            if word_match:
                # yield words
                for word in words:
                    yield word, (card_begin, card_end - card_begin)
                words.clear ()

                # update words
                card_begin = offset
                words.update (self.line_to_words (line))
            else:
                card_end = offset

        for word in words:
            yield word, (card_begin, card_end - card_begin)

    def __getitem__ (self, desc):
        offset, size = desc
        self.stream.seek (offset)
        return DslEntry (self.decode (self.stream.read (size)) [0].strip ())

    #--------------------------------------------------------------------------#
    # Discover                                                                 #
    #--------------------------------------------------------------------------#
    @classmethod
    def Discover (cls, root, recursive = False):
        def find_dsl (root, files):
            for file in files:
                if not file.lower ().endswith (cls.file_suffix):
                    continue
                yield path.join (root, file)

        if recursive:
            for root, dirs, files in os.walk (root):
                for file in find_dsl (root, files):
                    yield cls (file)
        else:
            for file in find_dsl (root, os.listdir (root)):
                yield cls (file)

    #--------------------------------------------------------------------------#
    # Dispose                                                                  #
    #--------------------------------------------------------------------------#
    def Dispose (self):
        self.stream.close ()

    def __enter__ (self):
        return self

    def __exit__ (self, et, eo, tb):
        self.Dispose ()
        return False

    #--------------------------------------------------------------------------#
    # Private                                                                  #
    #--------------------------------------------------------------------------#
    def lines (self, offset):
        tail, eof = b'', False
        self.stream.seek (offset)
        while not eof:
            chunk = self.stream.read (self.buffer_size)
            lines = (tail + chunk).split (self.newline)
            if chunk:
                tail = lines.pop ()
            else:
                eof = True
                
            for line in lines:
                string, size = self.decode (line)
                offset += size + len (self.newline)
                yield string, offset

    def line_to_words (self, line):
        subs, pattern = self.sub_pattern.findall (line), self.sub_pattern.sub ('%s', line)
        for mask in itertools.product ((True, False), repeat = len (subs)):
            yield self.space_pattern.sub (r'\1', self.del_pattern.sub ('',
                pattern % tuple ((subs [i] if y else '') for i, y in enumerate (mask))).strip ())

#------------------------------------------------------------------------------#
# Entry                                                                        #
#------------------------------------------------------------------------------#
class DslEntry (object):
    __slots__ = ('root',)
    tag_pattern    = re.compile (r'(?<!\\)\[(/)?([^\]]+)\]')   # tag
    indent_pattern = re.compile (r'\r?\n\s*', re.MULTILINE) # new line with offset

    def __init__ (self, data):
        self.root = DslNode (None)
        data = self.indent_pattern.sub ('\n', data)

        # build AST
        offset, stack, match = 0, [self.root], None
        for match in self.tag_pattern.finditer (data):
            # state
            close, name = match.groups ()
            node = stack [-1]

            # text
            if offset < match.start ():
                node.children.append ((False, data [offset:match.start ()]))
            offset = match.end ()

            # node
            if close:
                node = stack.pop ()
                # nodes are not nested
                if not node.name.startswith (name):
                    # restore stack
                    stack.append (node)
                    # find matching name
                    names = [name]
                    for index, node in enumerate (reversed (stack)):
                        if node.name.startswith (name):
                            # shift names
                            for node in stack [- index - 1:]:
                                node.name = names.pop ()
                            break
                        else:
                            names.append (node.name)
                    # unwind stack
                    stack.pop ()
            else:
                stack.append (DslNode (name))
                node.children.append ((True, stack [-1]))

        # tail
        if match:
            if match.end () < len (data):
                stack [-1].children.append ((False, data [match.end ():]))
        else:
            stack [-1].children.append ((False, data))

    #--------------------------------------------------------------------------#
    # Console                                                                  #
    #--------------------------------------------------------------------------#
    colors = {
        'trn' : (COLOR_DEFAULT, COLOR_NONE, ATTR_NONE),              # translation
        '*'   : (COLOR_BLACK,   COLOR_NONE, ATTR_BOLD),              # secondary
        'b'   : (COLOR_MAGENTA, COLOR_NONE, ATTR_BOLD | ATTR_FORCE), # bold
        'p'   : (COLOR_GREEN,   COLOR_NONE, ATTR_FORCE),             # part
        'i'   : (COLOR_NONE,    COLOR_NONE, ATTR_ITALIC),            # italic
        'ref' : (COLOR_MAGENTA, COLOR_NONE, ATTR_FORCE),             # reference
    }

    def ToConsole (self, console):
        #----------------------------------------------------------------------#
        # Walker                                                               #
        #----------------------------------------------------------------------#
        def node_walk (node):
            console.Write ('[{}]'.format (node.name))
            for is_node, child in node.children:
                if is_node:
                    name = child.name
                    # indentation
                    if name.startswith ('m'):
                        if len (name) > 1:
                            console.Write (' ' * int (name [1:]))
                        node_walk (child)
                    # colored
                    elif name in self.colors:
                        with console.Scope (*self.colors [name]):
                            node_walk (child)
                    # transcription
                    elif name == 't' and len (child.children) == 1:
                        console.Write (str (child.children [0][1].encode ('utf-16le')))
                    # skip
                    elif name in ('s',): pass
                    # default
                    else:
                        node_walk (child)
                else:
                    console.Write (child)
            # console.Write ('[/{}]'.format (node.name))
                    
        node_walk (self.root)
#------------------------------------------------------------------------------#
# Node                                                                         #
#------------------------------------------------------------------------------#
class DslNode (object):
    __slots__ = ('name', 'children')

    def __init__ (self, name):
        self.name = name
        self.children = []

# vim: nu ft=python columns=120 :
