#!/usr/bin/env python3

from __future__ import print_function
import sys


def convb64(i):
    if i < 26:
        return chr(ord('A') + i)
    elif i < 52:
        return chr(ord('a') + i-26)
    elif i < 62:
        return chr(ord('0') + i-52)
    elif i == 62:
        return '+'
    elif i == 63:
        return '/'


if __name__ == "__main__":
    for line in sys.stdin.readlines():
        binarr = bytearray.fromhex(line.strip())
        for i in range(len(binarr) // 3):
            con = binarr[3*i:3*(i+1)]
            # print(con)
            i1 = con[0] >> 2
            i2 = ((con[0] & 3) << 4) + (con[1] >> 4)
            i3 = ((con[1] & 15) << 2) + (con[2] >> 6)
            i4 = con[2] & 63
            print(convb64(i1), end='')
            print(convb64(i2), end='')
            print(convb64(i3), end='')
            print(convb64(i4), end='')
