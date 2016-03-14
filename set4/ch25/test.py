#!/usr/bin/env python3
from __future__ import print_function
import sollution
import unittest


class crypt(unittest.TestCase):
    def setUp(self):
        self.pg = sollution.PlayGround()
        self.key = b"YELLOW SUBMARINE"

    def test_crypt(self):
        testData = [b"test string", b"much longer test string, 12345 67890, asdfghjkl"]
        for msg in testData:
            self.assertEqual(msg,
                             self.pg.crypt(self.pg.crypt(msg, self.key), self.key),
                             "[ERROR] in fnc crypt for input: {}".format(msg))

    def test_edit(self):
        msg = b"aaa bbb ccc"
        enc = self.pg.crypt(msg, self.key)
        edt = self.pg.edit(enc, self.key, 4, b"xxx")
        dec = self.pg.crypt(edt, self.key)
        self.assertEqual(dec, b"aaa xxx ccc", "[ERROR] in fnc edit for input: {}".format(msg))

if __name__ == "__main__":
    unittest.main(verbosity=2)
