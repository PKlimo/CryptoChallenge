#!/usr/bin/env python3
from __future__ import print_function
import sha1
import hashlib
import unittest


class shatest(unittest.TestCase):
    def test_sha(self):
        testData = [b"test string", b"string longer than 512 bits" + b"A" * 512, b"very long" + b"X" * 3000, bytes(range(256))]
        for msg in testData:
            h1 = sha1.sha1(msg)
            mac = hashlib.sha1(msg)
            h2 = mac.hexdigest()
            self.assertEqual(h1, h2, "[ERROR] for msg: {}".format(msg))


class sha2state(unittest.TestCase):
    def test_sha2state(self):
        h0 = 0x67452301
        h1 = 0xEFCDAB89
        h2 = 0x98BADCFE
        h3 = 0x10325476
        h4 = 0xC3D2E1F0

        st = '%08x%08x%08x%08x%08x' % (h0, h1, h2, h3, h4)
        a0, a1, a2, a3, a4 = sha1.sha2state(st)
        self.assertEqual(a0, h0)
        self.assertEqual(a1, h1)
        self.assertEqual(a2, h2)
        self.assertEqual(a3, h3)
        self.assertEqual(a4, h4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
