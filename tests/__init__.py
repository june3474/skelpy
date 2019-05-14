# -*- coding: utf-8 -*-

import os
import sys

# python 2 & 3 compatibility
try:
    import mock  # First try python 2.7.x
except ImportError:
    from unittest import mock

#: add the package directory to the sys.path
#: tests_dir: /path/to/skelpy/tests
#: project_dir: /path/to/skelpy
#: project_name: skelpy
#: package_dir: /path/to/skelpy/skelpy
tests_dir = os.path.abspath(os.path.dirname(__file__))
project_dir = os.path.dirname(tests_dir)
project_name = os.path.basename(project_dir)
package_dir = os.path.join(project_dir, project_name)

sys.path.insert(0, package_dir)

