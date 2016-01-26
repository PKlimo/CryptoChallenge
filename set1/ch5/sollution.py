#!/usr/bin/env python3

from __future__ import print_function
import sys


def encode(text, key):
    ret = ""
    pos = 0
    for c in text:
        ret += "%.2x" % (c ^ key[pos])
        pos = (pos + 1) % len(key)
    return ret

if __name__ == "__main__":
    for line in sys.stdin.readlines():
        print(encode(bytearray(line.strip(), 'ascii'), bytearray('ICE', 'ascii')))
