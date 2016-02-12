#!/usr/bin/env python3
from __future__ import print_function
import binascii
import sys
from colorama import Fore, Style


def show(blok, keys):
    for i in range(0, len(blok)):
        for j, znak in enumerate(blok[i]):
            if j < len(keys):
                print("{}".format(chr(znak ^ keys[j])), end="")
            else:
                print(Fore.RED + "{:3} ".format(znak) + Style.RESET_ALL, end="")
        print()


def score_bytes(data):
    ret = 0
    for c in data:
        ret += 1 if ord('a') <= c <= ord('z') else 0
        ret += 1 if ord('A') <= c <= ord('Z') else 0
        ret += 1 if c == 32 else 0
    return ret


def score_block(blok):
    ret = {}
    for k in range(0, 256):
        dec = [(k ^ c) for c in blok]
        ret[k] = score_bytes(dec)
    return ret


def score_column(rows, i):
    blok = [r[i] for r in rows if i < len(r)]
    score = score_block(blok)
    from collections import Counter
    c = Counter(score)
    print(c.most_common(8))
    return c.most_common(1)[0][0]

if __name__ == "__main__":
    fn = sys.argv[1] if len(sys.argv) > 1 else "encoded_data.hex"
    with open(fn, "rt") as f:
        lines = f.readlines()

    rows = [None] * len(lines)
    data = []
    for i, line in enumerate(lines):
        rows[i] = binascii.unhexlify(line.rstrip().encode('utf-8'))

    keys = []
    for p in range(0, 30):
        keys += [score_column(rows, p)]
    keys += [174, 187, 249]  # added by hand because too little charctersto detct automatically
    keys += [145, 144, 141, 183, 111]  # used google to find poem - it is not possible to guess characters
    show(rows, keys)
