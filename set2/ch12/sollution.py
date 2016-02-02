#!/usr/bin/env python3
from __future__ import print_function
from Crypto.Cipher import AES
from Crypto import Random

passwd = Random.new().read(16)


def print_debug(msg, data):
    print(msg)
    for i in range(len(data) // 16):
        print(data[i*16:(i+1)*16])


def append(input):
    secret = b"yellow submarine secret text"
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


def give_enc_block_size(passwd):
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
    vzor = encryption_oracle(padding)  # encrypted aa...aa + k bytes from secret
    for j in range(255):
        guess = padding+bytes(known)+bytes([j])  # padding + k-1 known bytes + 1 byte guess
        enc_g = encryption_oracle(guess)
        if vzor[0:block_size] == enc_g[0:block_size]:
            return j
    print("not found")


if __name__ == "__main__":
    block_size = give_enc_block_size(passwd)
    num_block = len(encryption_oracle(b"")) // block_size
    print("Length of encrypted block: "+str(block_size))
    print("Number of encrypted blocks: "+str(num_block))
    print("Checking ECB mode: "+str(check_ecb_mode(passwd, block_size)))

    known = []
    for b in range(1, 19):
        known += [find_bytes(b, known)]
    print(known)
    print("".join([chr(k) for k in known]))
