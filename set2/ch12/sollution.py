#!/usr/bin/env python3
from __future__ import print_function


class PlayGround:
    def __init__(self, fn):
        import base64
        from Crypto import Random
        self.passwd = Random.new().read(16)
        self.fn = fn
        with open(fn, "rb") as f:
            lines = f.read()
        self.secret = base64.decodebytes(lines)

    def append(self, input):
        # secret = b"yellow submarine secret text"
        msg = input + self.secret
        length = 16 - (len(msg) % 16)
        msg += bytes([length])*length
        return msg

    def encryption_oracle(self, input):
        from Crypto.Cipher import AES
        obj = AES.new(self.passwd, AES.MODE_ECB)
        msg = self.append(input)
        cip = obj.encrypt(msg)
        return cip


def print_debug(msg, data):
    print(msg)
    for i in range(len(data) // 16):
        print(data[i*16:(i+1)*16])
    print()


def give_enc_block_size(pg):
    i = 0
    while True:
        diff = len(pg.encryption_oracle(b"a"*(i+1))) - len(pg.encryption_oracle(b"a"*i))
        if diff == 0:
            i += 1
        else:
            return diff


def check_ecb_mode(pg, block_size):
        enc = pg.encryption_oracle(b"a"*2*block_size)
        return enc[0:block_size] == enc[block_size:block_size*2]


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
    pg = PlayGround("input.b64")
    block_size = give_enc_block_size(pg)
    num_block = len(pg.encryption_oracle(b"")) // block_size
    print("Length of encrypted block: "+str(block_size))
    print("Number of encrypted blocks: "+str(num_block))
    print("Checking ECB mode: "+str(check_ecb_mode(pg, block_size)))

    known = []
    for b in range(1, 140):
        known += [find_bytes(pg, b, known)]
    print(known)
    print("".join([chr(k) for k in known]))
