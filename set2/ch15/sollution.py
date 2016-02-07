#!/usr/bin/env python3
from __future__ import print_function


class PKCS7:
    def __init__(self, base):
        self.__base = base

    def encode(self, data):
        length = self.__base - (len(data) % self.__base)
        data += bytes([length])*length
        return data

    def decode(self, data):
        pad = data[-1]
        if pad >= self.__base:
            raise ValueError("Last byte of padding (\\x{0:02x}) is bigger then base ({1})".format(pad, self.__base))
        for i in range(len(data)-pad, len(data)):
            if data[i] != pad:
                raise ValueError("Padding error on position {0} is byte \\x{1:02x} should be \\x{2:02x}".format(i, data[i], pad))
        data = data[:-pad]
        return data

if __name__ == "__main__":
    pkcs7 = PKCS7(16)
    print(pkcs7.decode(b'ICE ICE BABY\x04\x04\x04\x04'))
    try:
        print(pkcs7.decode(b'ICE ICE BABY\x04\x04\x04\x24'))
    except ValueError as e:
        print(e)
    try:
        print(pkcs7.decode(b'ICE ICE BABY\x05\x05\x05\x05'))
    except ValueError as e:
        print(e)
    try:
        print(pkcs7.decode(b'ICE ICE BABY\x01\x02\x03\x04'))
    except ValueError as e:
        print(e)
