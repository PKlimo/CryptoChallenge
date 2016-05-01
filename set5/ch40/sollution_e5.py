#!/usr/bin/env python3
from __future__ import print_function
debug = False


def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)


def invmod(a, b):
    from Crypto.Util import number
    return number.inverse(a, b)
    # https://en.wikipedia.org/wiki/Modular_multiplicative_inverse
    gcd, x, y = egcd(a, b)
    if gcd == 1:
        return (x % b)
    else:
        if debug:
            print('invmod', a, b)
#  invmod(17, 3120) is 2753
# assert(invmod(17, 3120) == 2753)


class RSA:
    def generate_keys(self, e):
        len = 1024
        # len = 16  # DEBUG
        from Crypto.Util import number
        while True:
            p = number.getPrime(len)
            q = number.getPrime(len)
            n = p * q
            et = (p-1)*(q-1)
            d = invmod(e, et)
            if d is not None:
                break
        print("Finding private/public key")
        if debug:
            print('n:', n, 'p:', p, 'q:', q, 'd:', d, 'e:', e)
        private_key = (d, n)
        public_key = (e, n)
        return (private_key, public_key)

    def encrypt(self, msg, pub_key):
        A, n = pub_key
        if type(msg) == int:
            m = msg
        else:
            m = int.from_bytes(msg, byteorder='big')
        return pow(m, A, n)

    def decrypt(self, msg, priv_key):
        a, n = priv_key
        msg = pow(msg, a, n)
        m = msg.to_bytes((msg.bit_length() // 8) + 1, byteorder='big')
        return m


def crack(cip, key):
    assert(len(key) == len(cip))
    e = key[0][0]
    assert(e == len(key))
    # http://www.di-mgt.com.au/crt.html#crackingrsa
    # TODO check if n (key[1]) are coprimes
    N = 1
    for k in key:
        N *= k[1]
    X = 0
    for i, k in enumerate(key):
        n = k[1]
        X += cip[i] * (N // n) * invmod((N // n), n)
    X = X % N
    dec = X ** (1. / e)
    if round(dec)**e == X:
        return round(dec)
    else:
        return dec


def main():
    msg = 42
    e = 7  # public key
    print("message:", msg)
    rsa = RSA()
    key = []
    cip = []
    for i in range(e):
        _, k = rsa.generate_keys(e)
        key += [k]
        cip += [rsa.encrypt(msg, k)]  # encrypted cipher text
    dec = crack(cip, key)
    print("message after encoding / decoding:", dec)
    assert(msg == dec)


if __name__ == "__main__":
    main()
