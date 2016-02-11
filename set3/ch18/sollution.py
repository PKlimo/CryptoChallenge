#!/usr/bin/env python3
from __future__ import print_function
from Crypto.Cipher import AES
import struct  # pack
import sys  # stderr

class CTR:
    def __init__(self, key, nonce):
        self.__key = key
        self.__nonce = nonce
        self.__count = 0

    def __xorstrings(self, txt, hes):
        if len(txt) != len(hes):
            print("Error xorstrings:\nlength of text:"+str(len(txt))+"\nlength of pass:"+str(len(hes)), file=sys.stderr)
            return ""
        else:
            ret = []
            for i in range(len(txt)):
                ret += [txt[i] ^ hes[i]]
            return ret

    def __counter(self):
        old_val = struct.pack('<Q', self.__count)
        self.__count += 1
        return old_val

    def crypt(self, data):
        obj = AES.new(self.__key, AES.MODE_ECB)
        cdata = []
        for i in range(0, len(data) // 16):  # crypt whole block
            pok = self.__nonce+self.__counter()
            keystream = obj.encrypt(pok)
            cdata += self.__xorstrings(data[i*16:(i+1)*16], keystream)
        # crypt incomplete last block
        pok = self.__nonce+self.__counter()
        keystream = obj.encrypt(pok)
        start = (len(data)//16)*16
        for i in range(start, len(data)):
            cdata += [data[i] ^ keystream[i-start]]
        return cdata

if __name__ == "__main__":
    ctr = CTR("YELLOW SUBMARINE", b'\x00'*8)

    with open("data.b64", "rt") as f:
        lines = f.readlines()
    import base64
    enc = base64.decodebytes(lines[0].encode('ascii'))
    dec = ctr.crypt(enc)
    print("".join([chr(d) for d in dec]))
