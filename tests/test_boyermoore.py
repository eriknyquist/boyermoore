import os
import unittest

from boyermoore import search_string, search_string_pp, search_file, search_file_pp, preprocess

from tests.common import make_big_bytes, make_big_file


TEST_STRINGS = [
    "howdy ho",
    "Loprem Ipsum",
    "hello, world!",
    "Hello, World!",
    "IIJJIIJJKKKKKKKK",
    "hello this is a test string and I need to make it kinda long so",
    "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVv"
]

TEST_OFFSETS = [
    [0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000],
    [1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072]
]

TEST_DATA = {s: [o for o in TEST_OFFSETS] for s in TEST_STRINGS}


class TestBoyerMoore(unittest.TestCase):
    def test_search_string_greedy(self):
        for pattern in TEST_DATA:
            for expected_offsets in TEST_DATA[pattern]:
                test_string = make_big_bytes(pattern.encode(), expected_offsets)
                actual_offsets = search_string(pattern, test_string)
                self.assertEqual(actual_offsets, expected_offsets)

    def test_search_string_notgreedy(self):
        for pattern in TEST_DATA:
            for expected_offsets in TEST_DATA[pattern]:
                test_string = make_big_bytes(pattern.encode(), expected_offsets)
                actual_offsets = search_string(pattern, test_string, greedy=False)
                self.assertEqual(actual_offsets, [expected_offsets[0]])

    def test_search_string_pp_greedy(self):
        for pattern in TEST_DATA:
            pp_data = preprocess(pattern)
            for expected_offsets in TEST_DATA[pattern]:
                test_string = make_big_bytes(pattern.encode(), expected_offsets)
                actual_offsets = search_string_pp(pp_data, test_string)
                self.assertEqual(actual_offsets, expected_offsets)

    def test_search_string_pp_notgreedy(self):
        for pattern in TEST_DATA:
            pp_data = preprocess(pattern)
            for expected_offsets in TEST_DATA[pattern]:
                test_string = make_big_bytes(pattern.encode(), expected_offsets)
                actual_offsets = search_string_pp(pp_data, test_string, greedy=False)
                self.assertEqual(actual_offsets, [expected_offsets[0]])

    def test_search_file_greedy(self):
        count = 0

        for pattern in TEST_DATA:
            for expected_offsets in TEST_DATA[pattern]:
                filename = "file_greedy%d.txt" % count
                count += 1

                test_string = make_big_file(filename, pattern.encode(), expected_offsets)
                while not os.path.isfile(filename):
                    pass

                actual_offsets = search_file(pattern, filename)
                self.assertEqual(actual_offsets, expected_offsets)

                os.remove(filename)

    def test_search_file_notgreedy(self):
        count = 0

        for pattern in TEST_DATA:
            for expected_offsets in TEST_DATA[pattern]:
                filename = "file_notgreedy%d.txt" % count
                count += 1

                test_string = make_big_file(filename, pattern.encode(), expected_offsets)
                while not os.path.isfile(filename):
                    pass

                actual_offsets = search_file(pattern, filename, greedy=False)
                self.assertEqual(actual_offsets, [expected_offsets[0]])

                os.remove(filename)

    def test_search_file_pp_greedy(self):
        count = 0

        for pattern in TEST_DATA:
            pp_data = preprocess(pattern)
            for expected_offsets in TEST_DATA[pattern]:
                filename = "file_pp_greedy%d.txt" % count
                count += 1

                test_string = make_big_file(filename, pattern.encode(), expected_offsets)
                while not os.path.isfile(filename):
                    pass

                actual_offsets = search_file_pp(pp_data, filename)
                self.assertEqual(actual_offsets, expected_offsets)

                os.remove(filename)

    def test_search_file_pp_notgreedy(self):
        count = 0

        for pattern in TEST_DATA:
            pp_data = preprocess(pattern)
            for expected_offsets in TEST_DATA[pattern]:
                filename = "file_pp_notgreedy%d.txt" % count
                count += 1

                test_string = make_big_file(filename, pattern.encode(), expected_offsets)
                while not os.path.isfile(filename):
                    pass

                actual_offsets = search_file_pp(pp_data, filename, greedy=False)
                self.assertEqual(actual_offsets, [expected_offsets[0]])

                os.remove(filename)
