#!/usr/bin/env python3
from __future__ import print_function
from Crypto.Cipher import AES
from Crypto.Util import Counter
import random


class PlayGround:
    def __init__(self):
        self.__key = bytes([random.getrandbits(8) for _ in range(16)])
        with open("25.txt", "rb") as f:
            self.__data = f.read()

    def crypt(self, data, key):
        ctr = Counter.new(64, prefix=b'\x00'*8, initial_value=0, little_endian=True)
        obj = AES.new(key, AES.MODE_CTR, counter=ctr)
        return obj.encrypt(data)

    def ciphertext(self):
        return self.crypt(self.__data, self.__key)

    def edit(self, data, key, offset, newtext):
        if key is None:
            key = self.__key

        tmp = bytearray(self.crypt(data, key))
        for i in range(len(newtext)):
            tmp[offset+i] = newtext[i]
        return self.crypt(bytes(tmp), key)


if __name__ == "__main__":
    pg = PlayGround()

    enc = pg.ciphertext()

    for i in range(len(enc)):
        for c in range(256):
            if enc == pg.edit(enc, None, i, [c]):
                print(chr(c), end="")
