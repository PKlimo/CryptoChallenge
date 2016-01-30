#!/usr/bin/env python3
from __future__ import print_function
from Crypto.Cipher import AES


def decodeCBC(data, passwd):
    obj = AES.new(passwd, AES.MODE_ECB)
    print(obj.decrypt(data[0:16]).decode(), end="")  # decode first block with IV
    for bn in range(1, len(data)//16):  # decode next blocks
        print("".join([chr(a ^ b) for (a, b) in zip(obj.decrypt(data[bn*16:(bn+1)*16]), data[(bn-1)*16:bn*16])]), end="")

if __name__ == "__main__":
    with open("data.bin", "rb") as f:
        data = f.read()
    decodeCBC(data, 'YELLOW SUBMARINE')
