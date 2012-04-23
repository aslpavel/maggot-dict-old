#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
from itertools import chain
from distutils.core import setup

#------------------------------------------------------------------------------#
# Helpers                                                                      #
#------------------------------------------------------------------------------#
def find_packages (prefix):
    root_name = os.path.basename (prefix.strip (os.path.sep))
    packages = []
    for root, dirs, files in os.walk (prefix):
        root = os.path.join (root [len (prefix):])
        for file in files:
            if file != '__init__.py':
                continue
            packages.append ('.'.join (chain ((root_name,), filter (None, root.split (os.path.sep)))))
    return packages

#------------------------------------------------------------------------------#
# Setup                                                                        #
#------------------------------------------------------------------------------#
setup (
    # info
    name         = 'maggot-dict',
    version      = '1.0',
    description  = 'Pure python (for now console based) dictionary',
    author       = 'Pavel Aslanov',
    author_email = 'asl.pavel@gmail.com',
    url          = 'https://github.com/aslpavel/maggot-dict',
    # install
    packages     = find_packages (os.path.join (os.path.dirname (__file__), 'MaggotDict')),
    data_files   = [
        ('bin', ['maggot-dict-cli']),
        ('/etc/bash_completion.d', ['scripts/maggot-dict-cli']),
    ]
)
# vim: nu ft=python columns=120 :
