
def _rand_data(num):
    ret = b""
    data = b"abcdefghijklmnopqrstuvwxyz" * 500

    while len(ret) < num:
        remaining = num - len(ret)
        size = remaining if remaining < len(data) else len(data)
        ret += data[:size]

    return ret

def make_big_file(filename, pattern, offsets):
    last_offset = 0

    with open(filename, 'wb') as fh:
        for offset in offsets:
            data_size = offset - last_offset
            data_to_write = _rand_data(data_size) + pattern
            fh.write(data_to_write)
            last_offset += len(data_to_write)


make_big_file("big_file.txt", "À Á Â Ã Ä Å".encode(), [12, 100, 5000, 100000000, 100000200])
