#!/usr/bin/env python3
from __future__ import print_function
from Crypto.Hash import SHA
from Crypto.PublicKey import DSA
from Crypto.Util import number
from Crypto.Random import random
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


def test_MyDSASigner():
    msg = b"Hello"
    h = SHA.new(msg).digest()

    myDSA = MyDSASigner()
    sig_my = myDSA.sign(h)
    sig_my2 = myDSA.sign(h, 42, myDSA.k)
    assert sig_my == sig_my2
    print('My signature      :', sig_my)

    key = DSA.construct((myDSA.y, g, p, q, 42))
    sig_py = key.sign(h, myDSA.k)
    print('PyCrypto signature:', sig_py)

    assert(sig_my == sig_py)
    print("Verification my:", myDSA.verify(sig_my, h))
    print("Verification py:", key.verify(h, sig_py))
    assert myDSA.verify(sig_my, h)
    assert key.verify(h, sig_py)


def find_k(r):
    return 16575
    for k in range(2**16):
        if r == pow(g, k, p) % q:
            return k


def main():
    print('=== Test of my implementation of DSA signer/verifyier ===')
    test_MyDSASigner()
    print('=== Verifying signature ===')
    msg = b"""For those that envy a MC it can be hazardous to your health\nSo be friendly, a matter of life and death, just like a etch-a-sketch\n"""
    hb = SHA.new(msg).digest()
    hi = int.from_bytes(hb, byteorder='big')
    assert hi == 0xd2d0714f014a9784047eaeccf956520045c45265  # check from website
    y = number.bytes_to_long(b'\x08\x4a\xd4\x71\x9d\x04\x44\x95\x49\x6a\x32\x01\xc8\xff\x48\x4f\xeb\x45\xb9\x62\xe7\x30\x2e\x56\xa3\x92\xae\xe4\xab\xab\x3e\x4b\xde\xbf\x29\x55\xb4\x73\x60\x12\xf2\x1a\x08\x08\x40\x56\xb1\x9b\xcd\x7f\xee\x56\x04\x8e\x00\x4e\x44\x98\x4e\x2f\x41\x17\x88\xef\xdc\x83\x7a\x0d\x2e\x5a\xbb\x7b\x55\x50\x39\xfd\x24\x3a\xc0\x1f\x0f\xb2\xed\x1d\xec\x56\x82\x80\xce\x67\x8e\x93\x18\x68\xd2\x3e\xb0\x95\xfd\xe9\xd3\x77\x91\x91\xb8\xc0\x29\x9d\x6e\x07\xbb\xb2\x83\xe6\x63\x34\x51\xe5\x35\xc4\x55\x13\xb2\xd3\x3c\x99\xea\x17')
    r = 548099063082341131477253921760299949438196259240
    s = 857042759984254168557880549501802188789837994940
    myDSA = MyDSASigner()
    print("Verification:", myDSA.verify((r, s), hb, y))
    print('=== Breaking x from k ===')
    k = find_k(r)
    x = (s*k - hi) * number.inverse(r, q)
    x = x % q
    print('x:', x)
    print('=== Verifying x by signer ===')
    sig = myDSA.sign(hb, x, k)
    assert (r, s) == sig
    print('OK')
    print('=== Verifying x by hash ===')
    xh = hex(x)[2:]
    print("encoded x:", xh)
    ch = SHA.new(xh.encode('ascii')).digest()
    print('SHA-1 hash of x:', hex(int.from_bytes(ch, byteorder='big'))[2:])
    assert hex(int.from_bytes(ch, byteorder='big'))[2:] == "954edd5e0afe5542a4adf012611a91912a3ec16"


if __name__ == "__main__":
    main()
