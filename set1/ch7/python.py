#!/usr/bin/env python3
from Crypto.Cipher import AES

obj = AES.new('YELLOW SUBMARINE', AES.MODE_ECB)

with open("data.bin", "rb") as f:
    data = f.read()
message = obj.decrypt(data)
print(message.decode())
