import os
import unittest

from boyermoore import search_string, search_string_pp, search_file, search_file_pp, preprocess

from tests.common import make_big_bytes, make_big_file


TEST_STRINGS = [
    "howdy ho",
    "AbCdEfG",
    "aqaqaq",
    "zqxzqx",
    "Loprem Ipsum",
    "hello, world!",
    "1 ; 'D,>/?0}[_[@6&8Kd __=-=",
    "IIJJIIJJKKKKKKKK",
    "  ",
    "AAAAA",
    "AAAAAA",
    "AAAAAAA",
    "Hello World, This is a Typical string of words And Stuff!!..?u",
    "PPPPPPPPPPPPPPPpppppppppppp",
    "hello this is a test string and I need to make it kinda long so",
    "कखगघ ङचछजझञ टठडढणतथदधन",
    "ճմնշոչպ ջռսվ տրց",
    "dճմddնշgdtrhոչ9898պ seeջռսվ :;':տրց",
    "⅓ ⅔ ⅕ ⅖⅗ ⅘ ⅙⅚⅛ ⅜ ⅝⅞ ⅟ Ⅰ Ⅱ Ⅲ ⅣⅤⅥ Ⅶ Ⅷ Ⅸ Ⅹ ⅪⅫ Ⅼ ⅭⅮ Ⅿ ⅰⅱⅲ ⅳ ⅴ ⅵⅶⅷ ⅸ ⅹ ⅺⅻ"
]

TEST_OFFSETS = [
    [0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000],
    [1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072],
    [1000, 5000, 20000],
    [131072],
    [1, 221, 442, 663, 884, 1095, 1306, 1507, 1708],
    [0, 1024 * 1024],
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

    def test_search_string_empty_pattern(self):
        test_string = b'hhhhhhhhhh'
        offsets = search_string('', test_string)
        self.assertEqual(offsets, [])

    def test_search_string_perfectfit_pattern(self):
        test_string = b'abcdabcdabcdabcd'
        offsets = search_string('abcd', test_string)
        self.assertEqual(offsets, [0, 4, 8, 12])

    def test_search_string_partialmatch_pattern(self):
        test_string = b'abcqabcgabcdabdj'
        offsets = search_string('abcd', test_string)
        self.assertEqual(offsets, [8])

    def test_search_string_nonexistent_pattern(self):
        test_string = b'hhhhhhhhhh'
        offsets = search_string('y', test_string)
        self.assertEqual(offsets, [])

    def test_search_string_1byte_pattern(self):
        test_string = b'hhqhhhhhhh'
        offsets = search_string('q', test_string)
        self.assertEqual(offsets, [2])

    def test_search_file_empty_pattern(self):
        filename = "testfile.txt"
        with open(filename, 'wb') as fh:
            fh.write(b'hhhhhhhhhh')

        offsets = search_file('', filename)
        self.assertEqual(offsets, [])

    def test_search_file_nonexistent_pattern(self):
        filename = "testfile.txt"
        with open(filename, 'wb') as fh:
            fh.write(b'hhhhhhhhhh')

        offsets = search_file('p', filename)
        self.assertEqual(offsets, [])

    def test_search_file_1byte_pattern(self):
        filename = "testfile.txt"
        with open(filename, 'wb') as fh:
            fh.write(b'hhqhhhhhhh')

        offsets = search_file('q', filename)
        self.assertEqual(offsets, [2])

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

    def test_preprocess_invalid_type(self):
        self.assertRaises(ValueError, preprocess, 5.5)
        self.assertRaises(ValueError, preprocess, {})
        self.assertRaises(ValueError, preprocess, [])
        self.assertRaises(ValueError, preprocess, (1,1))
        self.assertRaises(ValueError, preprocess, True)
