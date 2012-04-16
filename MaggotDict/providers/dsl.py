# -*- coding: utf-8 -*-
import os
import re
import io
import array
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
    header_pattern  = re.compile (r'^#([^\s]*)\s*"([^"]*).*') # dictionary header
    word_pattern  = re.compile (r'^[^\s]')                    # beginning of word
    del_pattern   = re.compile (r'\{[^}]*\}')                 # delete part of word
    sub_pattern   = re.compile (r'\(([^)]*)\)')               # alternative part of word
    space_pattern = re.compile (r'(\s)\s+')                   # double space pattern
    
    buffer_size = 1 << 16

    def __init__ (self, file):
        # open stream
        self.file = file
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
        self.headers = {}
        for header, offset in self.lines (offset = 2):
            if not header.startswith ('#'):
                break
            self.offset = offset
            match = self.header_pattern.search (header)
            if match:
                header, value = match.groups ()
                self.headers [header.lower ()] = value

    #--------------------------------------------------------------------------#
    # Properties                                                               #
    #--------------------------------------------------------------------------#
    @property
    def Name (self):
        return self.headers.get ('name', self.file [:-len (self.file_suffix)])

    @property
    def LastModified (self):
        return os.stat (self.stream.name).st_mtime

    @property
    def Headers (self):
        return self.headers

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
    tag_pattern    = re.compile (r'(?<!\\)\[(/)?([^\]]+)\]') # tag
    indent_pattern = re.compile (r'\r?\n\s*', re.MULTILINE)  # new line with offset
    escape_pattern = re.compile (r'\\(.)')                   # escape

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
                node.children.append ((False, self.escape_pattern.sub (r'\1', data [offset:match.start ()])))
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
                stack [-1].children.append ((False,  self.escape_pattern.sub (r'\1', data [match.end ():])))
        else:
            stack [-1].children.append ((False,  self.escape_pattern.sub (r'\1', data)))

    #--------------------------------------------------------------------------#
    # Console                                                                  #
    #--------------------------------------------------------------------------#
    colors = {
        'trn' : (COLOR_WHITE,   COLOR_NONE, ATTR_BOLD),              # translation
        'ref' : (COLOR_MAGENTA, COLOR_NONE, ATTR_FORCE),             # reference
        'ex'  : (COLOR_DEFAULT, COLOR_NONE, ATTR_FORCE),             # example
        'p'   : (COLOR_GREEN,   COLOR_NONE, ATTR_FORCE),             # part
        '*'   : (COLOR_BLACK,   COLOR_NONE, ATTR_BOLD),              # secondary
        '\''  : (COLOR_NONE,    COLOR_NONE, ATTR_UNDERLINE),         # stress
        'b'   : (COLOR_MAGENTA, COLOR_NONE, ATTR_BOLD | ATTR_FORCE), # bold
        'i'   : (COLOR_NONE,    COLOR_NONE, ATTR_ITALIC),            # italic
        'u'   : (COLOR_NONE,    COLOR_NONE, ATTR_UNDERLINE),         # underline
    }
    translit_color = (COLOR_GREEN, COLOR_NONE, ATTR_BOLD | ATTR_FORCE)

    def ToConsole (self, console):
        #----------------------------------------------------------------------#
        # Walker                                                               #
        #----------------------------------------------------------------------#
        def node_walk (node):
            for is_node, child in node.children:
                if is_node:
                    name = child.name
                    # indentation
                    if name.startswith ('m'):
                        if len (name) > 1:
                            console.Write ('  ' * int (name [1:]))
                        node_walk (child)
                    # colored
                    elif name in self.colors:
                        with console.Scope (*self.colors [name]):
                            node_walk (child)
                    # transcription
                    elif name == 't' and len (child.children) == 1:
                        with console.Scope (*self.translit_color):
                            codes = array.array ('H')
                            codes.fromstring (child.children [0][1].encode ('utf-16le'))
                            for code in codes:
                                console.Write (transcription_map.get (code, b'?').decode ('utf-8'))
                    # sound
                    elif name == 's':
                        with console.Scope (COLOR_DEFAULT, COLOR_CYAN, ATTR_BOLD):
                            console.Write ('[sound]')
                    # ignore
                    elif name.startswith ('lang '): node_walk (child)
                    elif name.startswith ('c '): node_walk (child)
                    elif name in ('com', '!trs'): node_walk (child)
                    # unhandled
                    else:
                        console.Write ('[{}]'.format (child.name))
                        node_walk (child)
                        console.Write ('[/{}]'.format (child.name))
                else:
                    console.Write (child)
                    
        node_walk (self.root)
#------------------------------------------------------------------------------#
# Node                                                                         #
#------------------------------------------------------------------------------#
class DslNode (object):
    __slots__ = ('name', 'children')

    def __init__ (self, name):
        self.name = name
        self.children = []

#------------------------------------------------------------------------------#
# Transcription                                                                #
#------------------------------------------------------------------------------#
transcription_map = {
    0x0020: b" ",                        # space
    0x0027: b'\'',                       # '
    0x0028: b'(',                        # (
    0x0029: b')',                        # )
    0x002c: b',',                        # ,
    0x002d: b'-',                        # -
    0x002e: b'.',                        # .
    0x002f: b'/',                        # /
    0x0030: b'\xc3\x9f',                 # ß ?
    0x0031: b'e\xcc\x83',                # ẽ ?
    0x0032: b'\xc9\x9c',                 # ɜ
    0x0033: b'\xc4\xa9',                 # ĩ ?
    0x0034: b'\xc3\xb5',                 # õ ?
    0x0035: b'\xc5\xa9',                 # ũ ?
    0x0036: b'\xca\x8e',                 # ʎ ?
    0x0037: b'\xc9\xa3',                 # ɣ ?
    0x0038: b'\xe1\xb5\x8a',             # e
    0x003a: b':',                        # ː
    0x003b: b';',                        # ;
    0x0041: b'A',                        # A
    0x0047: b'G',                        # G
    0x0048: b'H',                        # H
    0x004d: b'M',                        # M
    0x004e: b'N',                        # N
    0x004f: b'O',                        # O
    0x0052: b'R',                        # R
    0x0053: b'S',                        # S
    0x0054: b'T',                        # T
    0x0061: b'a',                        # a
    0x0062: b'b',                        # b
    0x0063: b'c',                        # c
    0x0064: b'd',                        # d
    0x0065: b'e',                        # e
    0x0066: b'f',                        # f
    0x0067: b'g',                        # g
    0x0068: b'h',                        # h
    0x0069: b'i',                        # i
    0x006a: b'j',                        # j
    0x006b: b'k',                        # k
    0x006c: b'l',                        # l
    0x006d: b'm',                        # m
    0x006e: b'n',                        # n
    0x006f: b'o',                        # o
    0x0070: b'p',                        # p
    0x0071: b'q',                        # q
    0x0072: b'r',                        # r
    0x0073: b's',                        # s
    0x0074: b't',                        # t
    0x0075: b'u',                        # u
    0x0076: b'v',                        # v
    0x0077: b'w',                        # w
    0x007a: b'z',                        # z
    0x0078: b'x',                        # x
    0x0079: b'y',                        # y
    0x00a0: b'\xca\xa7',                 # ʧ
    0x00a4: b'b',                        # b
    0x00a6: b'w',                        # w
    0x00a7: b'f',                        # f
    0x00a9: b's',                        # s
    0x00ab: b't',                        # t
    0x00ac: b'd',                        # d
    0x00ad: b'n',                        # n
    0x00ae: b'l',                        # l
    0x00b0: b'k',                        # k
    0x00b1: b'g',                        # g
    0x00b5: b'a',                        # a
    0x00b6: b'\xca\x8a',                 # ʊ
    0x00b7: b'\xc3\xa3',                 # ã
    0x00bb: b'\xc9\x99',                 # ə
    0x00df: b'\xc3\x9f',                 # ß
    0x00e3: b'\xc3\xa3',                 # ã
    0x00e4: b'\xc3\xa4',                 # ä
    0x00e6: b'\xc3\xa6',                 # æ
    0x00e7: b'\xc3\xa7',                 # ç
    0x00eb: b'\xc3\xab',                 # ë
    0x00f0: b'\xc3\xb0',                 # ð
    0x00f4: b'\xc3\xb4',                 # ô
    0x00f8: b'\xc3\xb8',                 # ø
    0x0101: b'\xc4\x81',                 # ā
    0x0113: b'\xc4\x93',                 # ē
    0x012b: b'\xc4\xab',                 # ī
    0x014b: b'\xc5\x8b',                 # ŋ
    0x014d: b'\xc5\x8d',                 # ō
    0x014f: b'\xc5\x8f',                 # ŏ
    0x0153: b'\xc5\x93',                 # œ
    0x01d0: b'\xc7\x90',                 # ǐ
    0x01d4: b'\xc7\x94',                 # ǔ
    0x0250: b'\xc9\x90',                 # ɐ
    0x0251: b'\xc9\x91',                 # ɑ
    0x0252: b'\xc9\x92',                 # ɒ
    0x0254: b'\xc9\x94',                 # ɔ
    0x0259: b'\xc9\x99',                 # ə
    0x025b: b'\xc9\x9b',                 # ɛ
    0x025c: b'\xc9\x9c',                 # ɜ
    0x0265: b'\xc9\xa5',                 # ɥ
    0x0272: b'\xc9\xb2',                 # ɲ
    0x0280: b'\xca\x80',                 # ʀ
    0x0283: b'\xca\x83',                 # ʃ
    0x028a: b'\xca\x8a',                 # ʊ
    0x028c: b'\xca\x8c',                 # ʌ
    0x028f: b'\xca\x8f',                 # ʏ
    0x0292: b'\xca\x92',                 # ʒ
    0x02a4: b'\xca\xa4',                 # ʤ
    0x02a7: b'\xca\xa7',                 # ʧ
    0x026a: b'\xc9\xaa',                 # ɪ
    0x02cc: b'\xcb\x8c',                 # ˌ
    0x02d0: b'\xcb\x90',                 # ː
    0x0303: b'\xcc\x83',                 # combining tilde
    0x0331: b'\xcc\xb1',                 # combining macron below
    0x035c: b'\xcd\x9c',                 # combining double breve below
    0x035d: b'\xcd\x9d',                 # combining double breve
    0x035e: b'\xcd\x9e',                 # combining double macron
    0x035f: b'\xcd\x9f',                 # combining double macron below
    0x03b8: b'\xce\xb8',                 # θ
    0x0402: b'i\xcb\x90',                # iː
    0x0403: b'\xc9\x91\xcb\x90',         # ɑː
    0x0404: b'z',                        # z
    0x0405: b'\xc5\x93\xcc\x83',         # œ̃
    0x0406: b'h',                        # h
    0x0407: b'r',                        # r
    0x0408: b'p',                        # p
    0x0409: b'\xca\x92',                 # ʒ
    0x040a: b'\xc5\x8b',                 # ŋ
    0x040b: b'\xce\xb8',                 # θ
    0x040c: b'u',                        # u
    0x040e: b'\xc9\xaa',                 # ɪ
    0x040f: b'\xca\x83',                 # ʃ
    0x0428: b'a',                        # a
    0x0440: b'\xc5\x8f',                 # ŏ
    0x0441: b'\xc9\xb2',                 # ɲ
    0x0442: b'\xc9\x94\xcc\x83',         # ɔ̃
    0x0443: b'\xc3\xb8',                 # ø
    0x0444: b'\xc7\x94',                 # ǔ
    0x0446: b'\xc3\xa7',                 # ç
    0x0447: b'a\xcd\x9ce',               # a͜e
    0x044a: b'\xca\x8f',                 # ʏ
    0x044c: b'\xc9\x91\xcc\x83',         # ɑ̃
    0x044d: b'\xc9\xaa',                 # ɪ
    0x044e: b'\xc9\x9c\xcb\x90',         # ɜː
    0x044f: b'\xc9\x92',                 # ɒ
    0x0452: b'v',                        # v
    0x0453: b'u\xcb\x90',                # uː
    0x0454: b'\xc9\x94\xcd\x9c\xc3\xb8', # ɔ͜ø
    0x0455: b'\xc7\x90',                 # ǐ
    0x0456: b'j',                        # j
    0x0457: b'\xc9\xa5',                 # ɥ
    0x0458: b'\xc5\x93',                 # œ
    0x045e: b'e',                        # e
    0x0490: b'm',                        # m
    0x0491: b'\xc9\x9b',                 # ɛ
    0x2018: b'\xc9\x91',                 # ɑ
    0x201a: b'\xc9\x94\xcb\x90',         # ɔː
    0x201e: b'\xc9\x99\xcb\x90',         # əː ?
    0x2020: b'\xc9\x99',                 # ə
    0x2021: b'\xc3\xa6',                 # æ
    0x2026: b'\xca\x8c',                 # ʌ
    0x2030: b'\xc3\xb0',                 # ð
    0x2039: b'\xca\xa4',                 # ʤ
    0x20ac: b'\xc9\x94',                 # ɔ
    0x2116: b'a\xcd\x9co',               # a͜o
}
# vim: nu ft=python columns=120 :
