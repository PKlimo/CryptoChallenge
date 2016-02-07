#!/usr/bin/env python3
from __future__ import print_function
from Crypto.Cipher import AES


class PlayGround:
    def __init__(self):
        from Crypto import Random
        self.__passwd = Random.new().read(16)

    def __enc(self, text):
        length = 16 - (len(text) % 16)
        msg = text.encode("utf-8") + bytes([length])*length
        obj = AES.new(self.__passwd, AES.MODE_ECB)
        cip = obj.encrypt(msg)
        return cip

    def __dec(self, text):
        obj = AES.new(self.__passwd, AES.MODE_ECB)
        cip = obj.decrypt(text)
        if cip[-1] < 32:  # remove padding
            cip = cip[:-cip[-1]]
        return cip.decode("utf-8")

    def profile_for(self, mail):
        mail = mail.translate(str.maketrans("", "", "&="))
        msg = "email="+mail+"&uid=10&role=user"
        return self.__enc(msg)

    def parse(self, cookie):
        msg = self.__dec(cookie)
        obj = msg.split("&")
        return obj

if __name__ == "__main__":
    pg = PlayGround()
    # 0123456789ABCDEF 0123456789ABCDEF 0123456789ABCDEF
    # email=0123456789 ABC&uid=10&role= user[\x12]*12
    #                                   admin[\x11]*11
    # email=0123456789 admin[\x11]*11   &uid=10&role=..
    # sollution:
    # s1="0123456789ABC" (use first and second block)
    # s2="0123456789admin[\x12]*11" (append second block)
    s1 = b'0123456789ABC'
    s2 = b'0123456789admin'+b"\x0b"*11
    d1 = pg.profile_for(s1.decode('ascii'))[0:32]
    d2 = pg.profile_for(s2.decode('ascii'))[16:32]
    print(pg.parse(d1+d2))
