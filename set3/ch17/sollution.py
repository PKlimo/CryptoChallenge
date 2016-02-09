#!/usr/bin/env python3
from __future__ import print_function
from Crypto.Cipher import AES
from Crypto import Random

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
        if not (0 < pad <= self.__base):
            return False
        for i in range(len(data)-pad, len(data)):
            if data[i] != pad:
                return False
        data = data[:-pad]
        return True


class PlayGround:
    def __init__(self, fn):
        self.__pkcs = PKCS7(16)
        self.__passwd = Random.new().read(16)
        with open(fn, "rt") as f:
            lines = f.readlines()
        import random
        l = random.randint(0, len(lines)-1)
        import base64
        self.__secret = base64.decodebytes(lines[l].encode('ascii'))

    def enc(self):
        iv = Random.new().read(16)
        obj = AES.new(self.__passwd, AES.MODE_CBC, iv)
        msg = self.__pkcs.encode(self.__secret)
        cip = obj.encrypt(msg)
        return iv+cip

    def dec(self, input):
        obj = AES.new(self.__passwd, AES.MODE_CBC, input[0:16])
        cip = obj.decrypt(input[16:])
        # print_debug_block("msg: ", cip)
        return self.__pkcs.decode(cip)


def dec_byte(pblock, nblock, pos, known):
    ret = []
    for i in range(0, 256):
        g_block = bytearray(pblock)
        for p in range(1, pos):
            g_block[16-p] = pblock[16-p] ^ known[p-1] ^ pos
        g_block[16-pos] = pblock[16-pos] ^ i ^ pos
        g_block = bytes(g_block)
        if pg.dec(g_block+nblock):
            ret += [i]
    return ret


def dec_block(pblock, nblock):
    known = []
    for i in range(1, 17):
        found = dec_byte(pblock, nblock, i, known)
        if len(found) == 1:
            known += found
        elif len(found) == 2:  # if there are two possibility, e.g. \x02\x01 and \x02\x02 (both correct padding)
            if len(dec_byte(pblock, nblock, i+1, known+[found[0]])) == 0:  # try one more step with first one and if failed
                known += [found[1]]  # return second quess
            else:
                known += [found[0]]
    return "".join([chr(k) for k in reversed(known)])

if __name__ == "__main__":
    pg = PlayGround('data.b64')
    data = pg.enc()

    msg = ""
    for i in range(0, (len(data) // 16) - 1):
        msg += dec_block(data[i*16:(i+1)*16], data[(i+1)*16:(i+2)*16])
    print(msg)
