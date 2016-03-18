#!/usr/bin/env python3
from __future__ import print_function


def padding(data):
    msg = ""
    for n in range(len(data)):
        msg += '{0:08b}'.format(data[n])
    pBits = "1"
    # pad until length equals 448 mod 512
    while len(msg + pBits) % 512 != 448:
        pBits += "0"
    # append the original length
    pBits += '{0:064b}'.format(len(msg))
    return msg, pBits


def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]


def rol(n, b):
    return ((n << b) | (n >> (32 - b))) & 0xffffffff


def process(chunk, h0, h1, h2, h3, h4):
    words = chunks(chunk, 32)
    w = [0]*80
    for n in range(0, 16):
        w[n] = int(words[n], 2)
    for i in range(16, 80):
        w[i] = rol((w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16]), 1)

    a = h0
    b = h1
    c = h2
    d = h3
    e = h4

    # Main loop
    for i in range(0, 80):
        if 0 <= i <= 19:
            f = (b & c) | ((~b) & d)
            k = 0x5A827999
        elif 20 <= i <= 39:
            f = b ^ c ^ d
            k = 0x6ED9EBA1
        elif 40 <= i <= 59:
            f = (b & c) | (b & d) | (c & d)
            k = 0x8F1BBCDC
        elif 60 <= i <= 79:
            f = b ^ c ^ d
            k = 0xCA62C1D6

        temp = rol(a, 5) + f + e + k + w[i] & 0xffffffff
        e = d
        d = c
        c = rol(b, 30)
        b = a
        a = temp

    h0 = h0 + a & 0xffffffff
    h1 = h1 + b & 0xffffffff
    h2 = h2 + c & 0xffffffff
    h3 = h3 + d & 0xffffffff
    h4 = h4 + e & 0xffffffff

    return h0, h1, h2, h3, h4


def sha2state(sha):
    import binascii
    import struct
    a = binascii.unhexlify(sha.encode('ascii'))
    h0 = struct.unpack('>I', a[:4])[0]
    h1 = struct.unpack('>I', a[4:8])[0]
    h2 = struct.unpack('>I', a[8:12])[0]
    h3 = struct.unpack('>I', a[12:16])[0]
    h4 = struct.unpack('>I', a[16:20])[0]

    return h0, h1, h2, h3, h4


def sha1(data):
    h0 = 0x67452301
    h1 = 0xEFCDAB89
    h2 = 0x98BADCFE
    h3 = 0x10325476
    h4 = 0xC3D2E1F0

    msg, pBits = padding(data)
    for chunk in chunks(msg + pBits, 512):
        h0, h1, h2, h3, h4 = process(chunk, h0, h1, h2, h3, h4)

    return '%08x%08x%08x%08x%08x' % (h0, h1, h2, h3, h4)
