#!/usr/bin/env python3
from __future__ import print_function
from Crypto.Cipher import AES


def print_debug_block(msg, data):
    print(msg)
    for i in range(len(data) // 16):
        print(data[i*16:(i+1)*16])


class PlayGround:
    def __init__(self):
        from Crypto import Random
        self.__passwd = Random.new().read(16)
        self.__iv = Random.new().read(16)

    def __append(self, input):
        input = input.translate(str.maketrans("", "", ";="))
        msg = "comment1=cooking%20MCs;userdata=" + input + ";comment2=%20like%20a%20pound%20of%20bacon"
        msg = msg.encode('ascii')
        length = 16 - (len(msg) % 16)
        msg += bytes([length])*length
        return msg

    def enc(self, input):
        obj = AES.new(self.__passwd, AES.MODE_CBC, self.__iv)
        msg = self.__append(input)
        cip = obj.encrypt(msg)
        return cip

    def dec(self, input):
        obj = AES.new(self.__passwd, AES.MODE_CBC, self.__iv)
        cip = obj.decrypt(input)
        return cip

    def check(self, input):
        data = self.dec(input)
        data = data.decode('ascii', errors='ignore')
        print(data)
        if ";admin=true;" in data:
            print("Check: OK")
        else:
            print("Check: Failed")

if __name__ == "__main__":
    pg = PlayGround()
    data = pg.enc('XXXXXXXXXXXXXXXX:admin<true:XXXX')

    dec = pg.dec(data)
    print_debug_block("\nDecoded before change: ", dec)

    # bit flipping attack start
    print("\nAlterning encoded block (bitflipping atack)")
    data = bytearray(data)
    data[32] = data[32] ^ 1
    data[38] = data[38] ^ 1
    data[43] = data[43] ^ 1
    data = bytes(data)
    # bit flipping attack end

    dec = pg.dec(data)
    print_debug_block("\nDecoded after change: ", dec)

    print("\nChecking ';admin=true;' substring in string")
    pg.check(data)
