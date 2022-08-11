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
strings and parameters using ``str.format``. It checks all strings whether they
use numbered parameters with an implicit index which isn't support in
Python 2.6.

In all instances of ``'…'.format(…)`` it will also check whether there are
enough parameters given. If the format call uses variable arguments, it'll just
check whether the right types of arguments are present.


Plugin for Flake8
-----------------

When both Flake8 and ``flake8-string-format`` are installed, the plugin
is available in ``flake8``::

  $ flake8 --version
  3.0.2 (flake8-string-format: 0.2.3, […]

This plugin supports Flake8 2.6 as well as Flake8 3.0. Older or newer versions
may be supported too but they weren't tested.

Via ``--ignore`` it's possible to ignore unindexed parameters::

  $ flake8 some_file.py
  ...
  some_file.py:1:1: FMT101 format string does contain unindexed parameters

  $ flake8 --ignore FMT101 some_file.py
  ...


Parameters
----------

This module doesn't add any additional parameters to Flake8.


Error codes
-----------

This plugin is using the following error codes:

+----------------------------------------------------------------------+
| Presence of implicit parameters                                      |
+--------+-------------------------------------------------------------+
| FMT101 | format string does contain unindexed parameters             |
+--------+-------------------------------------------------------------+
| FMT102 | docstring does contain unindexed parameters                 |
+--------+-------------------------------------------------------------+
| FMT103 | other string does contain unindexed parameters              |
+--------+-------------------------------------------------------------+
| Missing values in the parameters                                     |
+--------+-------------------------------------------------------------+
| FMT201 | format call uses too large index (INDEX)                    |
+--------+-------------------------------------------------------------+
| FMT202 | format call uses missing keyword (KEYWORD)                  |
+--------+-------------------------------------------------------------+
| FMT203 | format call uses keyword arguments but no named entries     |
+--------+-------------------------------------------------------------+
| FMT204 | format call uses variable arguments but no numbered entries |
+--------+-------------------------------------------------------------+
| FMT205 | format call uses implicit and explicit indexes together     |
+--------+-------------------------------------------------------------+
| Unused values in the parameters                                      |
+--------+-------------------------------------------------------------+
| FMT301 | format call provides unused index (INDEX)                   |
+--------+-------------------------------------------------------------+
| FMT302 | format call provides unused keyword (KEYWORD)               |
+--------+-------------------------------------------------------------+


Operation
---------

The plugin will go through all ``bytes``, ``str`` and ``unicode`` instances. If
it encounters ``bytes`` instances on Python 3, it'll decode them using ASCII and
if that fails it'll skip that entry.

Depending on the usage the string is handled differently. When it is not being
formatted, it can only cause ``FMT102`` and ``FMT103``. For this plugin all
strings which are the first expression of the module or after a function or
class definition are considered docstrings.

Both ``FMT102`` and ``FMT103`` issue many false positives and should only be
used with Python 2.6 which does not support `unindexed parameters
<https://docs.python.org/3/whatsnew/2.7.html#other-language-changes>`_.

Format strings
``````````````
Every string where either the ``format`` method is called or where it is the
first parameter of ``str.format``, is considered a format string and cause the
higher numbers.

If that call to ``format`` uses variable arguments, it cannot issue FMT201 and
FMT202 as missing entries might be hidden in those variable arguments.
FMT301 and FMT302 can still be checked for any argument which is defined
statically.


Python 2.6 support
``````````````````

Python 2.6 is only partially supported as it's using Python's capability to
format a string. So if a string contains implicit parameters, it won't be
detected as a parameter on Python 2.6 and thus it won't cause any FMT1XX errors.
But it might still cause an error FMT301 when variable arguments aren't used.

So if Python 2.6 compatibility is wished and thus implicit parameters aren't
allowed, this plugin won't cause false positives.


Changes
-------
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
