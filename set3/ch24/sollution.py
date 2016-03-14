#!/usr/bin/env python3
from __future__ import print_function
import struct  # pack
import random
import sys
import string
import numpy as np


class PlayGround:
    def __init__(self):
        self.__key = random.getrandbits(16)
        self.__msg = ''.join(random.choice(string.ascii_uppercase) for _ in range(random.randint(4, 18))) + "A"*14

    # Write the function that does this for MT19937 using a 16-bit seed
    def crypt(self, data, key):
        self.rn = np.random.RandomState(key)
        output = ""
        for i, c in enumerate(data):
            if i % 4 == 0:
                ks = struct.unpack("<BBBB", self.rn.bytes(4))
            j = 3 - (i % 4)
            output += chr(ks[j] ^ ord(c))
        return output

    def test_crypt(self):
        for _ in range(10):
            m = ''.join(random.choice(string.ascii_uppercase) for _ in range(random.randint(4, 18))) + "A"*14
            k = random.getrandbits(16)
            assert m == self.crypt(self.crypt(m, k), k), "Crypto function error for msg {} and key {}".format(m, k)

    def ciphertext(self):
        return self.crypt(self.__msg, self.__key)

    def check_key(self, k):
        sys.exit("Key is correct" if k == self.__key else "Key is incorrect")


if __name__ == "__main__":
    pg = PlayGround()
    pg.test_crypt()  # Verify that you can encrypt and decrypt properly

    # From the ciphertext, recover the "key" (the 16 bit seed)
    enc = pg.ciphertext()
    t = "X"*(len(enc)-14) + "A"*14
    for k in range(2**16):
        if pg.crypt(t, k)[-14:] == enc[-14:]:
            print("key:", k)
            pg.check_key(k)
