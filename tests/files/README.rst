Test files
==========

This directory contains test files to test various manually crafted cases. The
extension must be `.py` but can otherwise contain any name.

It must be formatted in such a way to define what issue is expected. The test
will then parse the file and verify that only the lines with the expected issues
are reported.

Error annotation
````````````````

To define that a certain line has an issue the following format must be used::

  # Error(+X): PAAA (B), PCCC (D),…

There variables are defined as follow:

* `X`: The number of lines below that line the error occurs, can be omitted and
  defaults to `1` then (the line below).
* After that a list of errors must follow separated by commas.
* `AAA`, `CCC`: The exact error codes that are expected.
* `B`, `D`: The indentation that is expected as well as a list of filters.
  If omitted it defaults to the location of the first occurrence of either `"`,
  `'` or `str.format` in the line the error belongs to.

The following filters are available:

* `raw`: It applies only when `check_raw` is `True`
* `>PY26`: It applies only when used on Python 2.7 or newer

Multiple filters can be chained together by separated them with commas.

Examples
````````
::

  # Error: P301
  print("Hello {0}".format("World", "you"))

  # Error(+2): P201

  print("Hello {0}".format())

  # Error: P201 (raw)
  print(r"Hello {0}".format())
