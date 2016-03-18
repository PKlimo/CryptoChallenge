#!/usr/bin/env python3
from __future__ import print_function
import hashlib
import sha1

max_key_len = 1000


class PlayGround:
    def __init__(self):
        import random
        self.__key = bytes([random.randint(0, 255) for _ in range(random.randint(0, max_key_len))])
        # self.__key = b""  # also working

    def check_msg(self, msg, mac_c, debug=True):
        data = self.__key + msg
        obj = hashlib.sha1(data)
        mac_ok = obj.hexdigest()
        if debug:
            print("\n=== Checking message and MAC ===")
            print("msg:", msg)
            print("provided MAC:", mac_c)
            print("computed MAC:", mac_ok)
            print(("MAC OK" if mac_c == mac_ok else "MAC ERROR"))
        return (mac_c == mac_ok)

    def sign_msg(self, msg):
        data = self.__key + msg
        obj = hashlib.sha1(data)
        mac_ok = obj.hexdigest()
        return mac_ok


def atack(key_len, msg, mac_msg, msg_new):
    # compute glue padding and convert to bytes
    _, glue_padding = sha1.padding(b"X" * key_len + msg)
    gl = sha1.chunks(glue_padding, 8)
    glue_padding = bytes([int(i, 2) for i in gl])
    msg_fake = msg + glue_padding + msg_new

    _, msg_new_pad = sha1.padding(b"X" * key_len + msg + glue_padding + msg_new)
    mnp = sha1.chunks(msg_new_pad, 8)
    msg_new_pad = bytes([int(i, 2) for i in mnp])
    h0, h1, h2, h3, h4 = sha1.sha2state(mac_msg)
    m, _ = sha1.padding(msg_new + msg_new_pad)
    h0, h1, h2, h3, h4 = sha1.process(m, h0, h1, h2, h3, h4)
    mac_fake = '%08x%08x%08x%08x%08x' % (h0, h1, h2, h3, h4)

    return msg_fake, mac_fake


def find_key_len(pg):
    for i in range(max_key_len + 1):
        msg_fake, mac_fake = atack(i, b"msg", pg.sign_msg(b"msg"), b"msg_new")
        if pg.check_msg(msg_fake, mac_fake, debug=False):
            print("found key length:", i)
            return i
    exit("cannot find key length")

if __name__ == "__main__":
    msg = b"comment1=cooking%20MCs;userdata=foo;comment2=%20like%20a%20pound%20of%20bacon"
    pg = PlayGround()
    mac = pg.sign_msg(msg)
    pg.check_msg(msg, mac)

    # length extension atack
    print("\n=== length extension atack ===")
    key_len = find_key_len(pg)
    msg_new = b";admin=true"
    msg_fake, mac_fake = atack(key_len, msg, mac, msg_new)

    pg.check_msg(msg_fake, mac_fake)
