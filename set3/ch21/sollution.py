#!/usr/bin/env python3
from __future__ import print_function

mt = [0] * 624
index = 624


def print_state():
    from struct import pack
    from binascii import hexlify
    for i in range(0, 624):
        print(hexlify(pack(">I", mt[i])).decode("ascii"), end="")


def _int32(i):
    return int(0xFFFFFFFF & i)


def _high_mask(i):
    return int(0x80000000 & i)


def _low_mask(i):
    return int(0x7FFFFFFF & i)


def extract_number():
    global index
    if index >= 624:
        twist()
    y = mt[index]

    y ^= (y >> 11)
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    y ^= (y >> 18)

    index += 1
    return _int32(y)


def init(seed):
    mt[0] = _int32(seed)
    for i in range(1, 624):
        mt[i] = _int32(int(1812433253) * (mt[i-1] ^ (mt[i-1] >> 30)) + i)


def twist():
    global index
    for i in range(0, 624):
        x = _int32(_high_mask(mt[i]) + _low_mask(mt[(i+1) % 624]))
        xA = x >> 1
        if (x % 2) != 0:
            xA = xA ^ 0x9908B0DF
        mt[i] = mt[(i+397) % 624] ^ xA
    index = 0


if __name__ == "__main__":
    init(42)
    # twist()
    # print_state()
    # twist()
    print(extract_number())
