#!/usr/bin/env python3
from __future__ import print_function
from Crypto.Cipher import AES
from Crypto import Random
import base64

passwd = Random.new().read(16)


class PlayGround:
    def __init__(self, fn):
        self.fn = fn
        self.passwd = Random.new().read(16)
        with open(fn, "rb") as f:
            lines = f.read()
        self.secret = base64.decodebytes(lines)


def print_debug(msg, data):
    print(msg)
    for i in range(len(data) // 16):
        print(data[i*16:(i+1)*16])
    print()


def append(input):
    fn = "input.b64"
    with open(fn, "rb") as f:
        lines = f.read()
    secret = base64.decodebytes(lines)
    # secret = b"yellow submarine secret text"
    msg = input + secret
    length = 16 - (len(msg) % 16)
    msg += bytes([length])*length
    return msg


def encryption_oracle(input):
    global passwd
    obj = AES.new(passwd, AES.MODE_ECB)
    msg = append(input)
    cip = obj.encrypt(msg)
    return cip


def give_enc_block_size():
    i = 0
    while True:
        diff = len(encryption_oracle(b"a"*(i+1))) - len(encryption_oracle(b"a"*i))
        if diff == 0:
            i += 1
        else:
            return diff


def check_ecb_mode(passwd, block_size):
        enc = encryption_oracle(b"a"*2*block_size)
        return enc[0:block_size] == enc[block_size:block_size*2]


def find_bytes(k, known):
    padding = bytes(b"a"*(block_size-k))  # block_size-k paddin of a (aa...aa)
    # work only for first block # vzor_enc = encryption_oracle(padding)[0:block_size]  # encrypted aa...aa + k bytes from secret
    vzor_blok = ((k-1) // 16)+1  # in which block in encryption_oracle I am comparing
    vzor_msg = bytes(b"a"*((block_size-1)-((k-1) % 16)))
    vzor_enc = encryption_oracle(vzor_msg)[(vzor_blok-1)*block_size:vzor_blok*block_size]  # encrypted aa...aa + k bytes from secret
    # print(padding+bytes(known[max([k-16, 0]):]))
    for j in range(256):
        # work only for first block # guess = padding+bytes(known)+bytes([j])  # padding + k-1 known bytes + 1 byte guess
        guess = padding+bytes(known[max([k-16, 0]):])+bytes([j])  # padding + k-1 known bytes + 1 byte guess
        enc_g = encryption_oracle(guess)
        if vzor_enc == enc_g[0:block_size]:
            return j
    print("Byte not found")
    print("k = ", k)
    print("guess = ", guess, "\n")
    print_debug("vzor_msg = ", append(vzor_msg))
    print("vzor_blok = ", vzor_blok)
    exit(-1)


if __name__ == "__main__":
    pg = PlayGround("input.b64")
    block_size = give_enc_block_size()
    num_block = len(encryption_oracle(b"")) // block_size
    print("Length of encrypted block: "+str(block_size))
    print("Number of encrypted blocks: "+str(num_block))
    print("Checking ECB mode: "+str(check_ecb_mode(passwd, block_size)))

    known = []
    for b in range(1, 30):
        known += [find_bytes(b, known)]
    print(known)
    print("".join([chr(k) for k in known]))
