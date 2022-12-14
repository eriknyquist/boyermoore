Boyer-Moore in pure python: search for unicode strings quickly in large files
-----------------------------------------------------------------------------

.. contents:: **Table Of Contents**


This is an implementation of the Boyer-Moore substring search algorithm in pure python.

It is a shameless copy-paste of the python reference code provided `here <https://en.wikipedia.org/wiki/Boyer%E2%80%93Moore_string-search_algorithm>`_,
with modifications to support the following additional features:

* Searching in files without reading the whole file into memory, allowing handling of large files
* Full unicode support

Searching for all occurences of a substring in a file
-----------------------------------------------------

::

    >>> from boyer_moore import search_file
    >>>
    >>> offsets = search_file("pattern!", "file.txt")                 # Find all occurrences of "pattern!" in file "file.txt"
    >>> offsets                                                       # Display found occurrences
    [12, 456, 10422]                                                  # Pattern occurs at byte offsets 12, 456, and 104222

Searching for athe first occurence of a substring in a file
-----------------------------------------------------------

::

    >>> from boyer_moore import search_file
    >>>
    >>> offsets = search_file("pattern!", "file.txt", greedy=False)   # Find the first occurrence of "pattern!" in file "file.txt"
    >>> offsets                                                       # Display found occurrences
    [12]                                                              # First occurrence of pattern is at byte offset 12

Performance / Speed test
------------------------

The following section illustrates the average speed of the ``boyermoore.search_file``
function when searching for a unicode string in files of sizes ranging from 32MB to 1GB.

Test environment
=================

The test was executed using Python 3.7.6 on a Windows 10 system with an Intel(R) Core(TM) i7-8700K CPU @ 3.70GHz
and 32 GB of RAM.

Test methodology
================

The test searches for all occurrences of a fixed unicode string in a series of test files.
The unicode string is:

::

    Hello नमस्ते Привет こんにちは

("Hello" in English, followed by the Hindi translation, followed by the Russian translation,
followed by the Japanese translation)

Each test file has 2 occurrences of the unicode string, one at the very beginning (byte offset of 0)
and one at the very end (byte offset of [file_length - pattern_length]).

Test results
============

The following table shows the times taken to search for all occurences of the unicode
string "Hello नमस्ते Привет こんにちは" inside test files of various sizes.

+-----------+----------------+
| File size | Time (seconds) |
+===========+================+
| 32 MB     | 0.54           |
+-----------+----------------+
| 64 MB     | 1.04           |
+-----------+----------------+
| 128 MB    | 2.02           |
+-----------+----------------+
| 256 MB    | 3.97           |
+-----------+----------------+
| 512 MB    | 7.71           |
+-----------+----------------+
| 1 GB      | 16.48          |
+-----------+----------------+
