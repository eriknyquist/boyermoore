test_data = b"abcdefghijklmnop" * 4096

def _rand_data(num):
    ret = b""
    while len(ret) < num:
        remaining = num - len(ret)
        size = remaining if remaining < len(test_data) else len(test_data)
        ret += test_data[:size]

    return ret

def make_big_file(filename, pattern, offsets):
    last_offset = 0

    with open(filename, 'wb') as fh:
        for offset in offsets:
            data_size = offset - last_offset
            data_to_write = _rand_data(data_size) + pattern
            fh.write(data_to_write)
            last_offset += len(data_to_write)

offsets = [
    1024 * 1024 * 10,
    1024 * 1024 * 50,
    1024 * 1024 * 100,
    1024 * 1024 * 200,
    1024 * 1024 * 300
]

make_big_file("big_file.txt", "À Á Â Ã Ä Å".encode(), offsets)
