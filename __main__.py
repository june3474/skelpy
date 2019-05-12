#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module is for executable zip"""

import sys
import os

# add the package directory inside the zip file to the sys.path
# __file__: skelpy-1.0.0.zip/__main__.py
# zipfile: /path/to/skelpy-1.0.0.zip
# base_dir: skelpy-1.0.0
# pkg_dir: skelpy

zipfile = os.path.abspath(os.path.dirname(__file__))
base_dir, _ = os.path.splitext(os.path.basename(zipfile))
pkg_dir, _ = base_dir.split('-', 1)
sys.path.insert(0, os.path.join(zipfile, base_dir, pkg_dir))

import main

main.run()
