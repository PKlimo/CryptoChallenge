#!/usr/bin/env python3
from __future__ import print_function
from Crypto.Cipher import AES
import sys


class PlayGround:
    def __init__(self):
        from Crypto import Random
        self.__passwd = Random.new().read(16)
        self.__iv = self.__passwd

    def send_enc_url(self):
        obj = AES.new(self.__passwd, AES.MODE_CBC, self.__iv)
        msg = "http://www.safeurls.edu/absolutely/innocent/url/"
        return obj.encrypt(msg)

    def recv_validate(self, input):
        obj = AES.new(self.__passwd, AES.MODE_CBC, self.__iv)
        cip = obj.decrypt(input)
        return (cip if not cip.decode('ascii', errors='replace').isprintable() else b"OK")

    def check(self, k):
        sys.exit("Key is correct" if k == self.__passwd else "Key is incorrect")


if __name__ == "__main__":
    pg = PlayGround()
    data = pg.send_enc_url()
    if pg.recv_validate(data) == b"OK":
        print("url is OK")

    mod_data = data[:16] + bytes([0]*16) + data[:16]
    err = pg.recv_validate(mod_data)
    key = []
    for i in range(16):
        key += [int(err[i])^int(err[32+i])]
    key = bytes(key)
    print("IV/key is:", key)
    pg.check(key)

