#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Collection of *Maker* modules

A *Maker* is a class that generates a template.
This package provides an attribute(dict) and a function on the package level:
``settings`` and ``get_maker()``.

Attributes:
    settings (dict): container for sharing data across *Makers*

"""

from __future__ import absolute_import, print_function

from importlib import import_module

settings = {}


def get_maker(mod_name):
    """Given the name of a module, returns the *Maker* class which is
    defined in that module.

    Args:
        mod_name (str): name of the module in which a *Maker* class is defined

    Returns:
        a *Maker* class or None: a *Maker* class--**NOT** an instance-- if successful, otherwise None

    """
    try:
        m = import_module('.' + mod_name, package='makers')
    except ImportError:
        return None

    return getattr(m, 'Maker', None)
