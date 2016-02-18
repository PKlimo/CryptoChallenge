#!/usr/bin/env python3
from __future__ import print_function

import mt19937 as rng
import random
import time


class PlayGround:
    def __init__(self):
        self.d = 40
        self.h = 1000
        self.__sleep(random.randint(self.d, self.h))
        self.__seed = int(time.time())
        self.__gn = rng.MT19937(self.__seed)

    def __sleep(self, cas):
        time.sleep(int(cas))

    def get_rand(self):
        self.__sleep(random.randint(self.d, self.h))
        return self.__gn.extract_number()

    def check(self, guess):
        return self.__seed == guess


def crack(rand):
    t = int(time.time())
    for i in range(2500, 0, -1):
        gn = rng.MT19937(t-i)
        if gn.extract_number() == rand:
            print("Seed is: ", t-i)
            print("Check: ", pg.check(t-i))
            return t-i
    print("Seek not found")
    return 0

if __name__ == "__main__":
    pg = PlayGround()
    rand = pg.get_rand()
    crack(rand)
