#!/usr/bin/env python3
from __future__ import print_function
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto import Random
import base64
import binascii

if __name__ == "__main__":
    passwd = Random.new().read(16)

    with open("data.b64", "rt") as f:
        lines = f.readlines()

    for line in lines:
        msg = base64.decodebytes(line.encode('ascii'))

        ctr = Counter.new(64, prefix=b'\x00'*8, initial_value=0, little_endian=True)
        obj = AES.new(passwd, AES.MODE_CTR, counter=ctr)
        enc = obj.encrypt(msg)

        hexd = binascii.hexlify(enc)
        print("".join([chr(d) for d in hexd]))
