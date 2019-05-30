# -*- coding: utf-8 -*-
"""Collection of template files

This package also provides a package-level function ``get_template()``.

"""

from __future__ import absolute_import, print_function

import string
from pkgutil import get_data


def get_template(tpl_name):
    """Retrieve the template by name

    copied from `pyscaffold project <http://pyscaffold.org>`_.

    Args:
        tpl_name (str): template name

    Returns:
        :class:`string.Template` or None: an instance of :class:`string.Template`
        class if successful, otherwise None.

    Raises:
        IOError(python2.7): if *tpl_name.tpl* file is not found
        FileNotFoundError(python3.x): if *tpl_name.tpl* file is not found
        TypeError: if *tpl_name* is not given

    """
    file = "{name}.tpl".format(name=tpl_name)
    #: for python 2.7
    try:
        FileNotFoundError
    except NameError:
        FileNotFoundError = IOError

    try:
        data = get_data(__name__, file)
    except FileNotFoundError:
        return

    return string.Template(data.decode(encoding='utf8'))
