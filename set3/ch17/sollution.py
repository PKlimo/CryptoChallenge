#!/usr/bin/env python3
from __future__ import print_function
from Crypto.Cipher import AES

debug = True


def print_debug_block(msg, data):
    print(msg)
    for i in range(len(data) // 16):
        print(data[i*16:(i+1)*16])


class PKCS7:
    def __init__(self, base):
        self.__base = base

    def encode(self, data):
        p_len = self.__base - (len(data) % self.__base)
        if p_len == 0:
            p_len = self.__base
        data += bytes([p_len])*p_len
        return data

    def decode(self, data):
        pad = data[-1]
        if pad > self.__base:
            return False
        for i in range(len(data)-pad, len(data)):
            if data[i] != pad:
                return False
        data = data[:-pad]
        return True


class PlayGround:
    def __init__(self, fn):
        self.__pkcs = PKCS7(16)
        from Crypto import Random
        self.__passwd = Random.new().read(16)
        self.__iv = Random.new().read(16)
        with open(fn, "rt") as f:
            lines = f.readlines()
        import random
        l = random.randint(0, len(lines)-1)
        import base64
        self.__secret = base64.decodebytes(lines[l].encode('ascii'))

    def enc(self):
        obj = AES.new(self.__passwd, AES.MODE_CBC, self.__iv)
        msg = self.__pkcs.encode(self.__secret)
        cip = obj.encrypt(msg)
        return cip

    def dec(self, input):
        obj = AES.new(self.__passwd, AES.MODE_CBC, self.__iv)
        cip = obj.decrypt(input)
        return self.__pkcs.decode(cip)

    def check(self, input):
        data = self.dec(input)
        data = data.decode('ascii', errors='ignore')
        print(data)
        if ";admin=true;" in data:
            print("Check: OK")
        else:
            print("Check: Failed")

if __name__ == "__main__":
    pg = PlayGround('data.b64')
    data = pg.enc()
    valid = pg.dec(data)
    print(valid)
