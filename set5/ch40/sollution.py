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
    def generate_keys(self):
        len = 1024
        len = 16  # DEBUG
        e = 3
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


def crack(c1, c2, c3, A, B, C):
    # http://www.di-mgt.com.au/crt.html#crackingrsa
    n1 = A[1]
    n2 = B[1]
    n3 = C[1]
    print('n1:', n1, 'n2:', n2, 'n3:', n3)
    # check if n1, n2 and n3 are coprime
    N = n1 * n2 * n3
    X = c1 * n2 * n3 * invmod(n2 * n3, n1) + \
        c2 * n1 * n3 * invmod(n1 * n3, n2) + \
        c3 * n1 * n2 * invmod(n1 * n2, n3)
    X = X % N
    dec = X ** (1. / 3.)
    if round(dec)**3 == X:
        return round(dec)
    else:
        return dec


def main():
    msg = 42
    print("message:", msg)
    rsa = RSA()
    a, A = rsa.generate_keys()
    b, B = rsa.generate_keys()
    c, C = rsa.generate_keys()
    c1 = rsa.encrypt(msg, A)
    c2 = rsa.encrypt(msg, B)
    c3 = rsa.encrypt(msg, C)
    dec = crack(c1, c2, c3, A, B, C)
    # dec = crack(43, 80, 65, (87, 3), (115, 3), (187, 3))
    print("message after encoding / decoding:", dec)
    assert(msg == dec)

if __name__ == "__main__":
    main()
