import os
import time

from boyermoore import search_file_pp, search_file, preprocess


test_data = b"abcdefghijklmnopqrstuvwxyz" * 16384

def _write_rand_data(fh, num):
    ret = b""

    written = 0
    while written < num:
        remaining = num - written
        size = remaining if remaining < len(test_data) else len(test_data)
        fh.write(test_data[:size])
        written += size

    return ret

def make_big_file(filename, pattern, offsets):
    last_offset = 0

    with open(filename, 'wb') as fh:
        for offset in offsets:
            data_size = offset - last_offset
            _write_rand_data(fh, data_size)
            fh.write(pattern)

            last_offset += len(pattern) + data_size

def linear_search(filename, pattern):
    pos = 0
    last_start_pos = 0
    matches = 0
    curr_match = 0

    with open(filename, 'rb') as fh:
        while True:
            c = fh.read(1)
            if not c:
                break

            c = c[0]
            if pattern[pos] == c:
                pos += 1
                if pos == 1:
                    curr_match = fh.tell()

                if pos >= len(pattern):
                    matches += curr_match
                    pos = 0
            else:
                pos = 0

    return matches

def main():
    sizes = [
        1024 * 1024,
        1024 * 1024 * 2,
        1024 * 1024 * 32,
        1024 * 1024 * 64,
        1024 * 1024 * 128,
        1024 * 1024 * 256,
        1024 * 1024 * 512,
        1024 * 1024 * 1024,
        1024 * 1024 * 1024 * 2,
    ]

    pattern = "Hello नमस्ते Привет こんにちは".encode()
    pp_data = preprocess(pattern)

    count = 0
    for size in sizes:
        offsets = [0, size - len(pattern)]
        filename = "__big_testfile%d.txt" % count
        count += 1

        make_big_file(filename, pattern, offsets)

        start_time = time.time()
        search_file_pp(pp_data, filename)
        bm_time_secs = time.time() - start_time

        start_time = time.time()
        linear_search(filename, pattern)
        linear_time_secs = time.time() - start_time

        print(f"{size:,} bytes, linear={linear_time_secs:.2f}, bm=f{bm_time_secs:.2f}")

        os.remove(filename)

if __name__ == "__main__":
    main()
