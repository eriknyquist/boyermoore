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

offsets = [
    0,
    1024 * 1024 * 1024 * 4
]

#make_big_file("big_file.txt", "À Á Â Ã Ä Å".encode(), offsets)
make_big_file("big_file.txt", "Hello नमस्ते Привет こんにちは".encode(), offsets)
#make_big_file("big_file.txt", "hello, world".encode(), offsets)
