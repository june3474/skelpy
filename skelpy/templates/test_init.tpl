# -*- coding: utf-8 -*-

import os
import sys

# python 2 & 3 compatibility
try:
    import mock  # First try python 2.7.x
except ImportError:
    from unittest import mock

sys.path.insert(0, os.path.join(${projectDir}, ${projectName}))
