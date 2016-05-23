#!/usr/bin/env python3
from __future__ import print_function
from Crypto.Hash import SHA
from Crypto.Util import number
from Crypto.Random import random
from collections import defaultdict
debug = True
p = number.bytes_to_long(b'\x80\x00\x00\x00\x00\x00\x00\x00\x89\xe1\x85\x52\x18\xa0\xe7\xda\xc3\x81\x36\xff\xaf\xa7\x2e\xda\x78\x59\xf2\x17\x1e\x25\xe6\x5e\xac\x69\x8c\x17\x02\x57\x8b\x07\xdc\x2a\x10\x76\xda\x24\x1c\x76\xc6\x2d\x37\x4d\x83\x89\xea\x5a\xef\xfd\x32\x26\xa0\x53\x0c\xc5\x65\xf3\xbf\x6b\x50\x92\x91\x39\xeb\xea\xc0\x4f\x48\xc3\xc8\x4a\xfb\x79\x6d\x61\xe5\xa4\xf9\xa8\xfd\xa8\x12\xab\x59\x49\x42\x32\xc7\xd2\xb4\xde\xb5\x0a\xa1\x8e\xe9\xe1\x32\xbf\xa8\x5a\xc4\x37\x4d\x7f\x90\x91\xab\xc3\xd0\x15\xef\xc8\x71\xa5\x84\x47\x1b\xb1')
q = number.bytes_to_long(b'\xf4\xf4\x7f\x05\x79\x4b\x25\x61\x74\xbb\xa6\xe9\xb3\x96\xa7\x70\x7e\x56\x3c\x5b')
g = number.bytes_to_long(b'\x59\x58\xc9\xd3\x89\x8b\x22\x4b\x12\x67\x2c\x0b\x98\xe0\x6c\x60\xdf\x92\x3c\xb8\xbc\x99\x9d\x11\x94\x58\xfe\xf5\x38\xb8\xfa\x40\x46\xc8\xdb\x53\x03\x9d\xb6\x20\xc0\x94\xc9\xfa\x07\x7e\xf3\x89\xb5\x32\x2a\x55\x99\x46\xa7\x19\x03\xf9\x90\xf1\xf7\xe0\xe0\x25\xe2\xd7\xf7\xcf\x49\x4a\xff\x1a\x04\x70\xf5\xb6\x4c\x36\xb6\x25\xa0\x97\xf1\x65\x1f\xe7\x75\x32\x35\x56\xfe\x00\xb3\x60\x8c\x88\x78\x92\x87\x84\x80\xe9\x90\x41\xbe\x60\x1a\x62\x16\x6c\xa6\x89\x4b\xdd\x41\xa7\x05\x4e\xc8\x9f\x75\x6b\xa9\xfc\x95\x30\x22\x91')


class MyDSASigner:
    def __init__(self):
        self.__x = 42
        self.y = pow(g, self.__x, p)

    def sign(self, h, priv_key=None, nonce=None):
        x = self.__x if priv_key is None else priv_key

        while True:
            k = random.StrongRandom().randint(1, q-1) if nonce is None else nonce
            r = pow(g, k, p) % q
            s2 = number.inverse(k, q) * (number.bytes_to_long(h) + x * r)
            s = pow(k, q-2, q) * (number.bytes_to_long(h) + x * r)
            assert(s2 == s)
            s = s % q
            if r != 0 and s != 0:
                self.k = k
                return (r, s)

    def verify(self, sig, h, pub_key=None):
        y = self.y if pub_key is None else pub_key
        r, s = sig
        if not 0 < r < q:
            return False
        if not 0 < s < q:
            return False
        w = number.inverse(s, q)
        u1 = (number.bytes_to_long(h) * w) % q
        u2 = (r * w) % q
        v = ((pow(g, u1, p) * pow(y, u2, p)) % p) % q
        return v == r


def extract_k(sig1, sig2, h1, h2):
    r1, s1 = sig1
    r2, s2 = sig2
    if r1 != r2:
        print("Different k was used")
        return None
    h1 = int.from_bytes(h1, byteorder='big')
    h2 = int.from_bytes(h2, byteorder='big')
    hdiff = (h1 - h2) % q
    sdiff = (s1 - s2) % q
    k = hdiff * number.inverse(sdiff, q)
    k = k % q
    if debug:
        print("k:", k)
    return k


def test_extract_k():
    print('=== Extract k from two signatures ===')
    myDSA = MyDSASigner()
    x = 42
    k = 57
    h1 = SHA.new(b'test message 1').digest()
    h2 = SHA.new(b'test message 2').digest()
    s1 = myDSA.sign(h1, x, k)
    s2 = myDSA.sign(h2, x, k)
    k1 = extract_k(s1, s2, h1, h2)
    k2 = extract_k(s2, s1, h2, h1)
    assert k1 == k2


def load_data():
    print('=== Load and check data from file ===')
    text = []
    import re
    d = defaultdict(list)
    with open("44.txt", "rt") as in_file:
        for line in in_file:
            text += [line.strip()]
    for i in range(0, len(text), 4):
        m = re.match('msg: (.*)$', text[i]).group(1) + " "
        s = re.match('s: (\d*)$', text[i+1]).group(1)
        r = re.match('r: (\d*)$', text[i+2]).group(1)
        h = re.match('m: ([0-9a-f]*)$', text[i+3]).group(1)
        if hex(int.from_bytes(SHA.new(m.encode('utf-8')).digest(), byteorder='big'))[2:] != h:
            print("Wrong SHA1 hash h:", h, 'for m:', m)
        d[int(r)].append((int(s), SHA.new(m.encode('utf-8')).digest()))
    return d


def main():
    x = None
    test_extract_k()
    d = load_data()
    print('=== Computing private key x ===')
    for r in d:
        if len(d[r]) > 1:
            s1, h1 = d[r][0]
            s2, h2 = d[r][1]
            k = extract_k((r, s1), (r, s2), h1, h2)
            hi1 = int.from_bytes(h1, byteorder='big')
            hi2 = int.from_bytes(h2, byteorder='big')
            x1 = ((s1*k - hi1) * number.inverse(r, q)) % q
            x2 = ((s2*k - hi2) * number.inverse(r, q)) % q
            assert x1 == x2
            if x is None:
                x = x1
            else:
                assert x == x1
    print('x:', x)
    print('=== Verifying SHA hash of private key x ===')
    xh = hex(x)[2:]
    ch = SHA.new(xh.encode('ascii')).digest()
    print('SHA-1 hash of x:', hex(int.from_bytes(ch, byteorder='big'))[2:])
    assert hex(int.from_bytes(ch, byteorder='big'))[2:] == "ca8f6f7c66fa362d40760d135b763eb8527d3d52"
    print('Hash is OK')


if __name__ == "__main__":
    main()
