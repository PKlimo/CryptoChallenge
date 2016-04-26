#!/usr/bin/env python3
from __future__ import print_function


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
    def generate_keys(self):
        from Crypto.Util import number
        print("Finding first prime number")
        p = number.getPrime(1024)
        print("Finding second prime number")
        q = number.getPrime(1024)
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
        private_key = (d, n)
        public_key = (e, n)
        return (private_key, public_key)

    def encrypt(self, msg, pub_key):
        A, n = pub_key
        m = int.from_bytes(msg, byteorder='big')
        return pow(m, A, n)

    def decrypt(self, msg, priv_key):
        a, n = priv_key
        msg = pow(msg, a, n)
        m = msg.to_bytes((msg.bit_length() // 8) + 1, byteorder='big')
        return m


def main():
    msg = b'test'
    print("message:", msg)
    rsa = RSA()
    priv_key, pub_key = rsa.generate_keys()
    enc = rsa.encrypt(msg, pub_key)
    dec = rsa.decrypt(enc, priv_key)
    print("message after ancoding / decoding:", dec)
    assert(msg == dec)

if __name__ == "__main__":
    main()
