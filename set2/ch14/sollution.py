#!/usr/bin/env python3
from __future__ import print_function
import sys  # argv, stderr
from Crypto import Random


def print_debug_block(msg, data):
    print(msg)
    for i in range(len(data) // 16):
        print(data[i*16:(i+1)*16])


def ext_block(data, i):  # extract i-th block (16 bytes) from data, i=1,2,.. len(data)/16
        return data[(i-1)*16:i*16]


class PlayGround:
    def __init__(self, fn):
        import base64
        self.__passwd = Random.new().read(16)
        with open(fn, "rb") as f:
            lines = f.read()
        self.__secret = base64.decodebytes(lines)
        # self.__secret = b"yellow submarine secret text"

    def append(self, input):
        import random
        rnd_num = random.randint(0, 50)  # number of rand bytes
        # rnd_num = 16
        rnd_bytes = Random.new().read(rnd_num)
        msg = rnd_bytes + input + self.__secret
        length = 16 - (len(msg) % 16)
        msg += bytes([length])*length
        return msg

    def encryption_oracle(self, input):
        from Crypto.Cipher import AES
        obj = AES.new(self.__passwd, AES.MODE_ECB)
        msg = self.append(input)
        cip = obj.encrypt(msg)
        return cip


class EncData:
    def __init__(self, pg):
        self.__pg = pg  # instance of PlayGround
        self.bs = 16  # Size of block - for AES 128 is 16 (128/8)
        self.canary = b"0123456789ABCDEF"
        self.ecanary = self.__enc_canary()
        self.num_block = len(self.oracle(b"")) // self.bs

    def __enc_canary(self):
        while True:
            guess = self.__pg.encryption_oracle((b"A"*16) + (b"B"*16) + self.canary + (b"A"*16) + (b"B"*16))
            for i in range(1, (len(guess) // 16)-4):
                if (ext_block(guess, i) == ext_block(guess, i+3)) and (ext_block(guess, i+1) == ext_block(guess, i+4)):
                    return ext_block(guess, i+2)

    def oracle(self, input):
        # import pdb
        # pdb.set_trace()
        while True:
            guess = self.__pg.encryption_oracle(self.canary+input)
            for i in range(1, len(guess) // 16):
                if ext_block(guess, i) == self.ecanary:
                    return guess[i*16:]

    def __check_ecb_mode(self):
        bs = self.bs  # block size
        enc = self.oracle(b"a"*2*bs)
        return enc[0:bs] == enc[bs:bs*2]

    def print_info(self):
        print("Length of encrypted block: "+str(self.bs), file=sys.stderr)
        print("Number of encrypted blocks: "+str(self.num_block), file=sys.stderr)
        print("Checking ECB mode: "+str(self.__check_ecb_mode()), file=sys.stderr)


class Message:
    def __init__(self, enc_data):
        self.bs = enc_data.bs
        self.enc_data = enc_data

    def __iblock(self):  # return important block from varialbe self.enc
        return self.enc[(self.iblok-1)*self.bs:self.iblok*self.bs]

    def encode(self):  # encode message and return important block
        return self.__iblock()

    def print_debug(self):
        print(self)
        print("padding: ", str(self.padding))
        print("msg:     ", str(self.msg))
        print_debug_block("enc: ", self.enc)
        print("iblock: ", str(self.iblok))
        print_debug_block("important block: ", self.__iblock())


class CompareMessage(Message):
    def __init__(self, enc_data):
        super(). __init__(enc_data)

    def create(self, k):
        # input: k - last byte of encoded message is k-th byte of secret
        # return: set the variable self.enc
        self.iblok = ((k-1) // 16)+1  # important block that will contain k-th byte of secreet (on last possition)
        self.padding = bytes(b"a"*((self.bs-1)-((k-1) % 16)))
        self.msg = self.padding
        self.enc = self.enc_data.oracle(self.msg)


class GuessMessage(Message):
    def __init__(self, enc_data):
        super(). __init__(enc_data)

    def create(self, k, known, j):
        # input: k - next byte of secret that will be compared to guessed byte j
        # input: known - known part of secret
        # return: set the variable self.enc
        self.iblok = 1
        self.padding = bytes(b"a"*(self.bs-k))  # block_size-k paddin of a (aa...aa)
        self.msg = self.padding+bytes(known[max([k-16, 0]):])+bytes([j])  # padding + k-1 known bytes + 1 byte guess
        self.enc = self.enc_data.oracle(self.msg)


if __name__ == "__main__":
    fn = sys.argv[1] if len(sys.argv) > 1 else "input.b64"
    pg = PlayGround(fn)
    enc_data = EncData(pg)
    # enc_data.print_info()

    known = []
    cmsg = CompareMessage(enc_data)
    gmsg = GuessMessage(enc_data)

    for k in range(1, enc_data.bs*enc_data.num_block):
        cmsg.create(k)
        for j in range(256):
            gmsg.create(k, known, j)
            if cmsg.encode() == gmsg.encode():
                known += [j]
                break
    print("".join([chr(k) for k in known]))
