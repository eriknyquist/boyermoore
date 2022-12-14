test_data = b"abcdefghijklmnop" * 4096

def _rand_data(num):
    ret = b""
    while len(ret) < num:
        remaining = num - len(ret)
        size = remaining if remaining < len(test_data) else len(test_data)
        ret += test_data[:size]

    return ret


def make_big_bytes(pattern, offsets):
    """
    Make a bytes object of size (offsets[-1] + len(pattern)), with an instance of
    the bytes object 'pattern' at each byte offset in 'offsets'
    """
    last_offset = 0
    ret = b''

    for offset in offsets:
        data_size = offset - last_offset
        data_to_write = _rand_data(data_size) + pattern
        ret += data_to_write
        last_offset += len(data_to_write)

    return ret


def make_big_file(filename, pattern, offsets):
    """
    Make a bytes object via make_big_bytes(pattern, offsets), and write it to
    new file 'filename'
    """
    with open(filename, 'wb') as fh:
        fh.write(make_big_bytes(pattern, offsets))
