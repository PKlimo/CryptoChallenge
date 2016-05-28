#!/usr/bin/env python3
from __future__ import print_function
debug = True


def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)


def invmod(a, b):
    # https://en.wikipedia.org/wiki/Modular_multiplicative_inverse
    gcd, x, y = egcd(a, b)
    if gcd == 1:
        return (x % b)
#  invmod(17, 3120) is 2753
assert(invmod(17, 3120) == 2753)


class RSA:
    def generate_keys(self, len):
        from Crypto.Util import number
        print("Finding first prime number")
        p = number.getPrime(len)
        # p = 7
        print("Finding second prime number")
        q = number.getPrime(len)
        # q = 11
        n = p * q
        et = (p-1)*(q-1)
        e = 3
        print("Finding private/public key")
        while True:
            d = invmod(e, et)
            if d is not None:
                break
            else:
                e += 1
        print('e:', e)
        print('d:', d)
        private_key = (d, n)
        public_key = (e, n)
        return (private_key, public_key)

    def encrypt(self, msg, pub_key):
        A, n = pub_key
        m = int.from_bytes(msg, byteorder='big')
        if m > n:
            print("Message too long")
            return None
        else:
            return pow(m, A, n)

    def decrypt(self, msg, priv_key):
        a, n = priv_key
        msg = pow(msg, a, n)
        m = msg.to_bytes((msg.bit_length() // 8) + 1, byteorder='big')
        return m


class PlayGround:
    def __init__(self):
        msg = b'dGVzdA=='  # test
        msg = b'VGhhdCdzIHdoeSBJIGZvdW5kIHlvdSBkb24ndCBwbGF5IGFyb3VuZCB3aXRoIHRoZSBGdW5reSBDb2xkIE1lZGluYQ=='
        import base64
        self.__msg = base64.b64decode(msg)
        self.__rsa = RSA()
        self.__priv_key, self.pub_key = self.__rsa.generate_keys(1024)
        self.enc = self.__rsa.encrypt(self.__msg, self.pub_key)

    def oraculum_is_even(self, msg):
            a, n = self.__priv_key
            m = pow(msg, a, n)
            return m % 2 == 0


def kolo(i, pg, min, max):
    e, n = pg.pub_key
    cip = pg.enc * ((2**(e*i)) % n)
    bit = pg.oraculum_is_even(cip)
    if bit:
        max = max - (n // 2**i)
    else:
        min = min + (n // 2**i)
    if debug:
        print('round:', i, 'min:', min, 'max:', max)
    return min, max


def main():
    pg = PlayGround()
    e, n = pg.pub_key
    l = n.bit_length() + 1
    min = 0
    max = n
    for i in range(1, l):
        min, max = kolo(i, pg, min, max)
    print("finding plaintext from interval:", min, max)
    for i in range(min, max):
        if pow(i, e, n) == pg.enc:
            print('Decoded number found:', i)
            break
    import math
    dec = i.to_bytes(math.ceil(i.bit_length()/8), byteorder='big')
    print("Decoded string:", dec.decode('ascii'))


if __name__ == "__main__":
    main()
