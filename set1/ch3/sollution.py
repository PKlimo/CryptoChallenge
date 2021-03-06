#!/usr/bin/env python3

from __future__ import print_function
import sys


def xors(inp, c):
    ret = bytearray()
    for x in inp:
        ret.append(x ^ c)
    return ret


def score(inp):
    return inp.count(" ")


def decode(enc):
        best = ""
        maxs = 0
        for i in range(255):
            pok = str(xors(enc, i))
            if score(pok) > maxs:
                maxs = score(pok)
                best = pok
            # print(str(score(pok))+" "+str(i)+" "+pok)
        return best

if __name__ == "__main__":
    for line in sys.stdin.readlines():
        enc = bytearray.fromhex(line.strip())
        print(decode(enc))
