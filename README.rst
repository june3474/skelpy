################
NOT RELEASED YET
################

``*skelpy*`` is a simple template tool to create the directory structure for a python project.
As this application was written for my personal use at first, it does neither offer
rich functionaries nor does strictly follow python coding standards such as snake-case naming
rules.
If you want a template tool with a broader selection of features, `Cookiecutter`_ ot `PyScaffold`_
would be a good choice for you.


Features
========

Pure Python, No Dependency
--------------------------
standard libraries
복잡한 옵션은 없애고 even zip-executable
For Python-only distributions, it *should* be straightforward to deploy on all
platforms where Python can run.

For distributions with binary extensions, deployment is major headache.  Not only
must the extensions be built on all the combinations of operating system and
hardware platform, but they must also be tested, preferably on continuous
integration platforms.  The issues are similar to the "multiple Python
versions" section above, not sure whether this should be a separate section.
Even on Windows x64, both the 32 bit and 64 bit versions of Python enjoy
significant usage.

Work well with Pycharm
----------------------
command-line tool but work well with pycharm, a popular IDE for python.

Cross platform, cross python version
------------------------------------


Quick Start
===========

To start a new project, say 'my_project', just type on the command shell::
  
  skel my_project

This will create a new folder ``my_project`` under the current directory and
fill the directory with subdirectories and configuration files like below::

    'basic' format(default)                   'src' format

    my_project/                               my_project/
    ├── docs/                                 ├── docs/
    │   ├── _build/                           │   ├── _build/
    │   ├── _static/                          │   ├── _static/
    │   ├── _templates/                       │   ├── _templates/
    │   ├── conf.py                           │   ├── conf.py
    │   ├── index.rst                         │   ├── index.rst
    │   ├── make.bat                          │   ├── make.bat
    │   └── Makefile                          │   └── Makefile
    ├── my_project/                           ├── src/
    │   ├── __init__.py                       │   └── my_project/
    │   └── main.py                           │       ├── __init__.py
    ├── tests/                                │       └── main.py
    │    └── test_main.py                     ├── tests/
    ├── LICENSE                               │    └── test_main.py
    ├── README.rst                            ├── LICENSE
    ├── setup.cfg                             ├── README.rst
    └── setup.py                              ├── setup.cfg
                                              └── setup.py

For more options, see ``skelpy -h``




License
=======

``skelpy`` is under `MIT`_ license.


Author
======

dks <june3474@gmail.com>


Change Log
==========

## [1.0.0] - 2018-04-13


.. _Pyscaffold: https://pyscaffold.org/en/latest/
.. _Cookiecutter: https://cookiecutter.readthedocs.org/
.. _MIT: https://choosealicense.com/licenses/mit/
