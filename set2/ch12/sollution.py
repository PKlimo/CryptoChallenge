#!/usr/bin/env python3
from __future__ import print_function
import sys  # argv, stderr


class PlayGround:
    def __init__(self, fn):
        import base64
        from Crypto import Random
        self.__passwd = Random.new().read(16)
        with open(fn, "rb") as f:
            lines = f.read()
        self.__secret = base64.decodebytes(lines)
        # self.__secret = b"yellow submarine secret text"

    def append(self, input):
        msg = input + self.__secret
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
        self.__bs = self.__give_enc_block_size()  # Size of block - for AES 128 is 16 (128/8)
        self.bs = self.__bs  # temporary - delete later
        self.__num_block = len(self.__pg.encryption_oracle(b"")) // self.__bs

    def __give_enc_block_size(self):
        i = 0
        while True:
            diff = len(self.__pg.encryption_oracle(b"a"*(i+1))) - len(self.__pg.encryption_oracle(b"a"*i))
            if diff == 0:
                i += 1
            else:
                return diff

    def __check_ecb_mode(self):
        bs = self.__bs  # block size
        enc = self.__pg.encryption_oracle(b"a"*2*bs)
        return enc[0:bs] == enc[bs:bs*2]

    def print_info(self):
        print("Length of encrypted block: "+str(self.__bs), file=sys.stderr)
        print("Number of encrypted blocks: "+str(self.__num_block), file=sys.stderr)
        print("Checking ECB mode: "+str(self.__check_ecb_mode()), file=sys.stderr)


def print_debug(msg, data):
    print(msg)
    for i in range(len(data) // 16):
        print(data[i*16:(i+1)*16])
    print()


def get_guess_block(block_size, k, known, j):
    padding = bytes(b"a"*(block_size-k))  # block_size-k paddin of a (aa...aa)
    # work only for first block
    # guess = padding+bytes(known)+bytes([j])  # padding + k-1 known bytes + 1 byte guess
    guess = padding+bytes(known[max([k-16, 0]):])+bytes([j])  # padding + k-1 known bytes + 1 byte guess
    return guess


def enc_guess_block(pg, block_size, k, known, j):
    guess = get_guess_block(block_size, k, known, j)
    enc_g = pg.encryption_oracle(guess)
    return enc_g[0:block_size]


def get_oracle_block(block_size, k):
    vzor_blok = ((k-1) // 16)+1  # in which block in encryption_oracle I am comparing
    vzor_msg = bytes(b"a"*((block_size-1)-((k-1) % 16)))
    return (vzor_blok, vzor_msg)


def enc_oracle_block(pg, block_size, k):
    (vzor_blok, vzor_msg) = get_oracle_block(block_size, k)
    # work only for first block
    # vzor_enc = encryption_oracle(padding)[0:block_size]  # encrypted aa...aa + k bytes from secret
    vzor_enc = pg.encryption_oracle(vzor_msg)[(vzor_blok-1)*block_size:vzor_blok*block_size]  # encrypted aa...aa + k bytes from secret
    return vzor_enc


def print_not_found(pg, block_size, k, known, j):
    print("Byte not found")
    print("k = ", k)
    print("guess = ", get_guess_block(pg, block_size, k, known, j), "\n")
    (vzor_blok, vzor_msg) = get_oracle_block(block_size, k)
    print_debug("vzor_msg = ", pg.append(vzor_msg))
    print("vzor_blok = ", vzor_blok)


def find_bytes(pg, k, known):
    for j in range(256):
        if enc_oracle_block(pg, block_size, k) == enc_guess_block(pg, block_size, k, known, j):
            return j
    print_not_found(pg, block_size, k, known, j)
    exit(-1)


if __name__ == "__main__":
    debug = False
    fn = sys.argv[1] if len(sys.argv) > 1 else "input.b64"
    if debug:
        print("File name: ", fn, file=sys.stderr)
    pg = PlayGround(fn)
    enc_data = EncData(pg)
    block_size = enc_data.bs
    if debug:
        enc_data.print_info()

    known = []
    for b in range(1, 140):
        known += [find_bytes(pg, b, known)]
    if debug:
        print(known, file=sys.stderr)
    print("".join([chr(k) for k in known]))
