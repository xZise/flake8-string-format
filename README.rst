String format parameter checker
===============================

.. image:: https://github.com/xZise/flake8-string-format/actions/workflows/main.yml/badge.svg?branch=master
   :alt: Build Status
   :target: https://github.com/xZise/flake8-string-format/actions

.. image:: http://codecov.io/github/xZise/flake8-string-format/coverage.svg?branch=master
   :alt: Coverage Status
   :target: http://codecov.io/github/xZise/flake8-string-format?branch=master

.. image:: https://badge.fury.io/py/flake8-string-format.svg
   :alt: Pypi Entry
   :target: https://pypi.python.org/pypi/flake8-string-format

An extension for `Flake8 <https://pypi.python.org/pypi/flake8>`_ to check the
strings and parameters using ``str.format``.

In all instances of ``'…'.format(…)`` it will also check whether there are
enough parameters given. If the format call uses variable arguments, it'll just
check whether the right types of arguments are present.


Plugin for Flake8
-----------------

When both Flake8 and ``flake8-string-format`` are installed, the plugin
is available in ``flake8``::

  $ flake8 --version
  3.0.2 (flake8-string-format: 0.2.3, […]

Via ``--ignore`` it's possible to ignore unindexed parameters::

  $ flake8 some_file.py
  ...
  some_file.py:1:1: FMT201 format call index too large (5

  $ flake8 --ignore FMT201 some_file.py
  ...


Parameters
----------

This module doesn't add any additional parameters to Flake8.


Error codes
-----------

This plugin is using the following error codes:

+--------+---------------------------------------------------------------------+
| Missing values in the parameters                                             |
+--------+---------------------------------------------------------------------+
| FMT201 | format call index too large (INDEX)                                 |
+--------+---------------------------------------------------------------------+
| FMT202 | format call uses missing keyword (KEYWORD)                          |
+--------+---------------------------------------------------------------------+
| FMT203 | format call uses keyword arguments but there are no keyword entries |
+--------+---------------------------------------------------------------------+
| FMT204 | format call uses indexed arguments but there are no indexed entries |
+--------+---------------------------------------------------------------------+
| FMT205 | format call uses implicit and explicit indexes together             |
+--------+---------------------------------------------------------------------+
| Unused values in the parameters                                              |
+--------+---------------------------------------------------------------------+
| FMT301 | format call provides unused index (INDEX)                           |
+--------+---------------------------------------------------------------------+
| FMT302 | format call provides unused keyword (KEYWORD)                       |
+--------+---------------------------------------------------------------------+


Operation
---------

The plugin will go through all ``bytes``, ``str``. If
it encounters ``bytes`` instances on Python 3, it'll decode them using ASCII and
if that fails it'll skip that entry.

Format strings
``````````````
Every string where either the ``format`` method is called or where it is the
first parameter of ``str.format``, is considered a format string and cause the
higher numbers.

If that call to ``format`` uses variable arguments, it cannot issue FMT201 and
FMT202 as missing entries might be hidden in those variable arguments.
FMT301 and FMT302 can still be checked for any argument which is defined
statically.


Changes
-------
0.4.0 - 2026-06-09
``````````````````
* Fix support for Python version 3.14
* Improve error message wording

0.3.0 - 2020-02-16
``````````````````
* Removed support for standalone version.
* Support multiple starargs and at any location.

0.2.3 - 2016-07-27
``````````````````
* Properly register with Flake8 so it will be selected on Flake8 3.x by default
  and it can be selected on Flake8 2.x.

0.2.2 - 2016-05-29
``````````````````
* Do not check simple expressions, except for docstrings, because they cannot be
  accessed anyway.
* Properly assert starred arguments in Python 3.5. Only the last element must be
  a vararg if varargs are present and not the complete list.
* Output correct column offset on Python 3.4.2, as that used the wrong offset
  inside calls.

0.2.1 - 2015-09-20
``````````````````
* Support ``str.format("…", …)`` calls and handle them like ``"…".format(…)``

0.2.0 - 2015-09-12
``````````````````
* Instead of using a regex it's trying to parse it using Python's parser
* This result can also be used now to verify that enough parameters are given
* Limited Python 2.6 support

0.1.0 - 2015-09-10
``````````````````
* Detect unindexed parameters in all strings
* Separate error code for docstrings
