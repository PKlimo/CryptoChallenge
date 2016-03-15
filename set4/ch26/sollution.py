#!/usr/bin/env python3
from __future__ import print_function
from Crypto.Cipher import AES
from Crypto.Util import Counter
import random


class PlayGround:
    def __init__(self):
        self.__key = bytes([random.getrandbits(8) for _ in range(16)])

    def __append(self, input):
        input = input.translate(str.maketrans("", "", ";="))
        msg = "comment1=cooking%20MCs;userdata=" + input + ";comment2=%20like%20a%20pound%20of%20bacon"
        msg = msg.encode('ascii')
        return msg

    def enc(self, input):
        ctr = Counter.new(64, prefix=b'\x00'*8, initial_value=0, little_endian=True)
        obj = AES.new(self.__key, AES.MODE_CTR, counter=ctr)
        msg = self.__append(input)
        cip = obj.encrypt(msg)
        return cip

    def dec(self, input):
        ctr = Counter.new(64, prefix=b'\x00'*8, initial_value=0, little_endian=True)
        obj = AES.new(self.__key, AES.MODE_CTR, counter=ctr)
        cip = obj.encrypt(input)
        return cip

    def check(self, input):
        data = self.dec(input)
        data = data.decode('ascii', errors='ignore')
        print(("Check: OK" if ";admin=true;" in data else "Check: Failed"))


if __name__ == "__main__":
    pg = PlayGround()
    data = pg.enc('X:admin<true:')

    dec = pg.dec(data)
    print(dec)

    # bit flipping attack start
    data = bytearray(data)
    data[33] = data[33] ^ 1
    data[39] = data[39] ^ 1
    data[44] = data[44] ^ 1
    data = bytes(data)
    # bit flipping attack end

    dec = pg.dec(data)
    print(dec)

    print("Checking ';admin=true;' substring in string")
    pg.check(data)
