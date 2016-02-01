#!/usr/bin/env python3
from __future__ import print_function
from Crypto.Cipher import AES
from Crypto import Random
import random


def append(input):
    lpad = Random.new().read(5+random.randint(0, 5))
    rpad = Random.new().read(5+random.randint(0, 5))
    msg = lpad + input + rpad
    length = 16 - (len(msg) % 16)
    msg += bytes([length])*length
    return msg


def print_debug(msg, data):
    print(msg)
    for i in range(len(data) // 16):
        print(data[i*16:(i+1)*16])


def encryption_oracle(input):
    passwd = Random.new().read(16)
    if random.randint(0, 1):
        iv = Random.new().read(AES.block_size)
        obj = AES.new(passwd, AES.MODE_CBC, iv)
        mode = 'CBC'
    else:
        obj = AES.new(passwd, AES.MODE_ECB)
        mode = 'ECB'
    print("chosen mode:" + mode)
    msg = append(input)
    print_debug("message", msg)
    cip = obj.encrypt(msg)
    print_debug("encrypted", cip)
    return (mode, cip)


def detect(blob):
    return 'ECB' if blob[16:32] == blob[32:48] else 'CBC'

if __name__ == "__main__":
    mode, blob = encryption_oracle(bytes(11+16+16))
    print("OK" if mode == detect(blob) else "wrong")
