Boyer-Moore in pure python- search for unicode strings quickly in large files
-----------------------------------------------------------------------------


Performance / Speed test
------------------------

The following speed test was performed by searching for all occurrences of a unicode
string in a series of test files. The unicode string is "Hello नमस्ते Привет こんにちは".

Each test file has 2 occurrences of the unicode string, one at the very beginning (byte offset of 0)
and one at the very end (byte offset of [file_length - pattern_length]).

The following table shows the times taken to search for all occurences of the unicode
string inside test files of various sizes.

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
