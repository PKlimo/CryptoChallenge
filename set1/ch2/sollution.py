#!/usr/bin/env python3

from __future__ import print_function
import sys


def xorstrings(txt, hes):
    if len(txt) != len(hes):
        print("length of text:"+str(len(txt))+"\nlength of pass:"+str(len(hes)), file=sys.stderr)
        return ""
    else:
        ret = ""
        for i in range(len(txt)):
            ret += "%x" % (txt[i] ^ hes[i])
        return ret

if __name__ == "__main__":
    lines = sys.stdin.readlines()
    txt = bytearray.fromhex(lines[0].strip())
    hes = bytearray.fromhex(lines[1].strip())
    print(xorstrings(txt, hes))
