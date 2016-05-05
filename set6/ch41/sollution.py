#!/usr/bin/env python3
from __future__ import print_function
debug = True


def invmod(a, b):
    from Crypto.Util import number
    return number.inverse(a, b)


class RSA:
    def generate_keys(self, e):
        len = 1024
        if debug:
            len = 16  # DEBUG
        from Crypto.Util import number
        while True:
            p = number.getPrime(len)
            q = number.getPrime(len)
            n = p * q
            et = (p-1)*(q-1)
            d = invmod(e, et)
            if d != 1:
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


class PlayGround:
    def __init__(self, priv_key, pub_key):
        self.__priv_key = priv_key
        self.pub_key = pub_key
        self.__rsa = RSA()
        self.decrypted = []

    def decrypt(self, msg):
        if msg in self.decrypted:
            return None
        else:
            self.decrypted += [msg]
            return self.__rsa.decrypt(msg, self.__priv_key)


class Player:
    def __init__(self, pg):
        self.pg = pg
        self.__msg = 42
        self.__rsa = RSA()

    def encrypt(self):
        return self.__rsa.encrypt(self.__msg, self.pg.pub_key)

    def test_1_dec(self, cip):
        dec = self.pg.decrypt(cip)
        d = int.from_bytes(dec, byteorder='big')
        if d == self.__msg:
            print('Decryption test passed, msg:', d)
        else:
            print('Decryption failed, msg:', self.__msg, 'decrypted:', d)

    def test_2_dec(self, cip):
        dec = self.pg.decrypt(cip)
        if dec is None:
            print("Test OK, second decryption shouldn't be allowed")
        else:
            print("Test Failed, second decryption shouldn't be allowed")


class Atacker:
    def __init__(self, pg):
        self.pg = pg
        self.__rsa = RSA()

    def crack(self, cip):
        e = self.pg.pub_key[0]
        N = self.pg.pub_key[1]
        dec = self.pg.decrypt(pow(2, e, N) * cip)
        dec = int.from_bytes(dec, byteorder='big')
        dec = (dec * invmod(2, N)) % N  # dec = dec // 2
        print('Cracked message:', dec)


def main():
    rsa = RSA()
    priv_key, pub_key = rsa.generate_keys(7)
    pg = PlayGround(priv_key, pub_key)
    player = Player(pg)
    cip = player.encrypt()
    player.test_1_dec(cip)
    player.test_2_dec(cip)
    atacker = Atacker(pg)
    atacker.crack(cip)


if __name__ == "__main__":
    main()
