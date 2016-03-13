#!/usr/bin/env python3
from __future__ import print_function
import mt19937
import numpy as np
import random
import struct


class PlayGround:
    def __init__(self):
        self.seed = random.getrandbits(32)
        self.rn = np.random.RandomState(self.seed)

    def getNumber(self):
        return struct.unpack("<L", self.rn.bytes(4))[0]


class Sollution:
    def findSeed(self, pg):
        rn = [0] * 624
        tm = [0] * 624
        for i in range(624):
            rn[i] = pg.getNumber()
            tm[i] = mt19937.unextract_number(rn[i], i)
        mt = mt19937.untwist(tm)
        seed = mt19937.uninit(mt)
        return seed

    def createState(self, seed):
        mt = mt19937.init(seed)
        mt = mt19937.twist(mt)
        return mt

    def check(self, pg, mt, rounds):
        ret = True
        for i in range(624*rounds):
            if i % 624 == 0:
                mt = mt19937.twist(mt)
            pg_r = pg.getNumber()
            mt_r = mt19937.extract_number(mt, i % 624)
            if pg_r != mt_r:
                print("[ERROR] round {} wrong prediction: pg_r= {}, mt_r= {}".format(i, pg_r, mt_r))
                ret = False
        return ret


if __name__ == "__main__":
    pg = PlayGround()
    sol = Sollution()
    seed = sol.findSeed(pg)
    mt = sol.createState(seed)
    print("Check:", sol.check(pg, mt, 3))
