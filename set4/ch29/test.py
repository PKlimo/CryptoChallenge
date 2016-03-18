#!/usr/bin/env python3
from __future__ import print_function
import sha1
import hashlib
import unittest


class shatest(unittest.TestCase):
    def test_sha(self):
        testData = [b"test str", b"string longer than 512 bits" + b"A" * 512, b"very long" + b"X" * 3000, bytes(range(256))]
        for msg in testData:
            hash1 = sha1.sha1(msg)
            mac = hashlib.sha1(msg)
            hash2 = mac.hexdigest()
            self.assertEqual(hash1, hash2, "[ERROR] for msg: {}".format(msg))


class sha2state(unittest.TestCase):
    def test_sha2state(self):
        testData = [b"test str", b"string longer than 512 bits" + b"A" * 512, b"very long" + b"X" * 3000, bytes(range(256))]
        for msg in testData:
            hash1 = sha1.sha1(msg)
            h0, h1, h2, h3, h4 = sha1.process_all(msg)
            a0, a1, a2, a3, a4 = sha1.sha2state(hash1)
            self.assertEqual(a0, h0)
            self.assertEqual(a1, h1)
            self.assertEqual(a2, h2)
            self.assertEqual(a3, h3)
            self.assertEqual(a4, h4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
