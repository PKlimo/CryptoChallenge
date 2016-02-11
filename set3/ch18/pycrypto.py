#!/usr/bin/env python3
from __future__ import print_function
from Crypto.Cipher import AES
from Crypto.Util import Counter

if __name__ == "__main__":
    ctr = Counter.new(64, prefix=b'\x00'*8, initial_value=0, little_endian=True)
    obj = AES.new(b"YELLOW SUBMARINE", AES.MODE_CTR, counter=ctr)

    with open("data.b64", "rt") as f:
        lines = f.readlines()
    import base64
    enc = base64.decodebytes(lines[0].encode('ascii'))
    dec = obj.encrypt(enc)
    print("".join([chr(d) for d in dec]))
