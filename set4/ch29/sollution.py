#!/usr/bin/env python3
from __future__ import print_function
import hashlib


class PlayGround:
    def __init__(self):
        self.__key = b"key"

    def check_msg(self, msg, mac_c):
        data = self.__key + msg
        obj = hashlib.sha1(data)
        mac_ok = obj.hexdigest()
        print("=== Checking message and MAC ===")
        print("msg:", msg)
        print("provided MAC:", mac_c)
        print("computed MAC:", mac_ok)
        print(("MAC OK" if mac_c == mac_ok else "MAC ERROR"))

    def sign_msg(self, msg):
        data = self.__key + msg
        obj = hashlib.sha1(data)
        mac_ok = obj.hexdigest()
        return mac_ok


if __name__ == "__main__":
    msg = b"message"
    pg = PlayGround()
    mac = pg.sign_msg(msg)
    pg.check_msg(msg, mac)

    # length extension atack
    import sha1
    key_len = 3

    msg_new = b"new message"
    _, glue_padding = sha1.padding(b"X" * key_len + msg)
    gl = sha1.chunks(glue_padding, 8)
    glue_padding = bytes([int(i, 2) for i in gl])
    msg_fake = msg + glue_padding + msg_new

    _, msg_new_pad = sha1.padding(b"X" * key_len + msg + glue_padding + msg_new)
    h0, h1, h2, h3, h4 = sha1.sha2state(mac)
    m, _ = sha1.padding(msg_new + msg_new_pad.encode('ascii'))
    h0, h1, h2, h3, h4 = sha1.process(m, h0, h1, h2, h3, h4)
    mac_fake = '%08x%08x%08x%08x%08x' % (h0, h1, h2, h3, h4)
    pg.check_msg(msg_fake, mac_fake)
