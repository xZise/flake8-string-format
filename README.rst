Unindexed parameter checker
===========================

.. image:: https://secure.travis-ci.org/xZise/flake8-indexed-format.png?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/xZise/flake8-indexed-format

.. image:: http://codecov.io/github/xZise/flake8-indexed-format/coverage.svg?branch=master
   :alt: Coverage Status
   :target: http://codecov.io/github/xZise/flake8-indexed-format?branch=master

.. image:: https://badge.fury.io/py/flake8-indexed-format.svg
   :alt: Pypi Entry
   :target: https://pypi.python.org/pypi/flake8-indexed-format

An extension for ``flake8`` to check if the code is using unindexed parameters
used in ``str.format`` as that isn't support in Python 2.6.


Standalone script
-----------------

The checker can be used directly::

  $ python -m flake8_indexed_format some_file.py
  some_file.py:1:1: P101 str does contain unindexed parameters

Even though ``flake8`` still uses ``optparse`` this script in standalone mode
is using ``argparse``.


Plugin for Flake8
-----------------

When both ``flake8 2.0`` and ``flake8-indexed-format`` are installed, the plugin
is available in ``flake8``::

  $ flake8 --version
  2.0 (pep8: 1.4.2, flake8-indexed-format: 0.1.0, pyflakes: 0.6.1)

Via ``--ignore`` it's possible to ignore unindxed parameters::

  $ flake8 some_file.py
  ...
  some_file.py:1:1: P101 str does contain unindexed parameters

  $ flake8 --ignore P101 some_file.py
  ...


Parameters
----------

This module doesn't add any additional parameters. The stand alone version also
mimics flake8's ignore parameter.


Error codes
-----------

This plugin is using the following error code:

+------+---------------------------------------------+
| P101 | str does contain unindexed parameters       |
+------+---------------------------------------------+
| P102 | docstring does contain unindexed parameters |
+------+---------------------------------------------+


Changes
-------

0.1.0 - 2015-09-10
``````````````````
* Detect unindexed parameters in all strings
* Separate error code for docstrings
