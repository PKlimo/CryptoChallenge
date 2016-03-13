#!/usr/bin/env python3
from __future__ import print_function
import mt19937
import unittest
import numpy as np
import struct
import random


class mt19937_random_numbers_small(unittest.TestCase):
    """My implementation of mt19937 must return same numbers as numpy implementation of mt19937
    test for one number, seed is 42"""

    def setUp(self):
        self.rn = np.random.RandomState(42)

        self.mt = [0] * 624
        self.mt = mt19937.init(42)
        self.mt = mt19937.twist(self.mt)

    def test_random_numbers_small(self):
        np_r = struct.unpack("<L", self.rn.bytes(4))[0]
        mt_r = mt19937.extract_number(self.mt, 0)
        self.assertEqual(np_r, mt_r, "[ERROR]: seed=42 twist=1 i=0")


class mt19937_random_numbers_big(unittest.TestCase):
    """My implementation of mt19937 must return same numbers as numpy implementation of mt19937
    test for more numbers (20*624), seed is random"""
    def setUp(self):
        self.seed = random.getrandbits(32)
        self.rounds = 20

        self.rn = np.random.RandomState(self.seed)

        self.mt = [0] * 624
        self.mt = mt19937.init(self.seed)

    def test_random_numbers_big(self):
        for i in range(624*self.rounds):
            if i % 624 == 0:
                self.mt = mt19937.twist(self.mt)
            np_r = struct.unpack("<L", self.rn.bytes(4))[0]
            mt_r = mt19937.extract_number(self.mt, i % 624)
            self.assertEqual(np_r, mt_r, "[ERROR]: seed={}, twist={}, i={}".format(self.seed, i // 624, i))


class mt19937_untwist(unittest.TestCase):
    """Test my implementation of untwist function"""
    def do_test_state(self, mt):
        # States are the same except first part, which can not be recover
        self.assertListEqual(mt[1:],
                             mt19937.untwist(mt19937.twist(mt))[1:],
                             "test with state mt == untwist(twist(mt)), mt: {}".format(mt))  # mt[0] is not recoverable
        # if you twist untwisted state, also first part must be twisted correctly
        self.assertListEqual(mt19937.twist(mt),
                             mt19937.twist(mt19937.untwist(mt19937.twist(mt))),
                             "test with state twist(mt) == twist(untwist(twist(mt))), mt: {}".format(mt))

    def do_test_seed(self, seed):
        mt = mt19937.init(seed)
        # States are the same except first part, which can not be recover
        self.assertListEqual(mt[1:],
                             mt19937.untwist(mt19937.twist(mt))[1:],
                             "test with seed: mt == untwist(twist(mt)), seed: {}".format(seed))  # mt[0] is not recoverable
        # if you twist untwisted state, also first part must be twisted correctly
        self.assertListEqual(mt19937.twist(mt),
                             mt19937.twist(mt19937.untwist(mt19937.twist(mt))),
                             "test with seed: twist(mt) == twist(untwist(twist(mt))), seed: {}".format(seed))

    def test_untwist(self):
        # untwist state, that was created from seed by one run of twist
        for seed in [42, 4190403025, 1303704821] + [random.getrandbits(32) for _ in range(10)]:
            self.do_test_seed(seed)

        # untwist state, that was created from seed by two runs of twist
        for seed in [42, 4190403025, 1303704821] + [random.getrandbits(32) for _ in range(10)]:
            self.do_test_state(mt19937.twist(mt19937.twist(mt19937.init(seed))))

        # untwist randomly generated state
        mt = [0] * 624
        for _ in range(10):
            for i in range(624):
                mt[i] = random.getrandbits(32)
            self.do_test_state(mt)


class mt19937_is_init(unittest.TestCase):
    def test_is_init(self):
        testData = [42, 4190403025, 1303704821] + [random.getrandbits(32) for _ in range(10)]
        # function init generates initial state
        for seed in testData:
            self.assertTrue(mt19937.is_init(mt19937.init(seed)))
        # function twist generates state, that is not init
        for seed in testData:
            self.assertFalse(mt19937.is_init(mt19937.twist(mt19937.init(seed))))
        # function untwist applied on one time twisted state generates initial state
        for seed in testData:
            self.assertTrue(mt19937.is_init(mt19937.untwist(mt19937.twist(mt19937.init(seed)))))
        # two times applied function twist and untwist is not working because I am loosing information from mt[0]
        for seed in testData:
            mt = mt19937.init(seed)
            mt = mt19937.twist(mt)
            mt = mt19937.twist(mt)
            mt = mt19937.untwist(mt)
            mt = mt19937.untwist(mt)
            # self.assertTrue(mt19937.is_init(mt), "error for seed: {}".format(seed))


class mt19937_uninit(unittest.TestCase):
    def test_uninit(self):
        testData = [42, 4190403025, 1303704821] + [random.getrandbits(32) for _ in range(10)]
        for seed in testData:
            # extract seed from initial state
            self.assertEqual(mt19937.uninit(mt19937.init(seed)), seed)
            # perform twist, then untwist and then extract seed
            self.assertEqual(mt19937.uninit(mt19937.untwist(mt19937.twist(mt19937.init(seed)))), seed)
            # if state is not initial None is returned
            self.assertIsNone(mt19937.uninit(mt19937.twist(mt19937.init(seed))))


class mt19937_unextract(unittest.TestCase):
    def test_unextract(self):
        testData = [42, 4190403025, 1303704821] + [random.getrandbits(32) for _ in range(10)]
        for seed in testData:
            for i in range(624):
                mt = mt19937.init(seed)
                rn = mt19937.extract_number(mt, i)
                tm = mt19937.unextract_number(rn, i)
                self.assertEqual(mt[i], tm)


if __name__ == "__main__":
    unittest.main(verbosity=2)
