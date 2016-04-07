#!/usr/bin/env python3
from __future__ import print_function
import random
import hashlib
from Crypto.Cipher import AES

p_nist = 0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff


class Alice:
    def __init__(self):
        self.p = 0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff
        self.g = 2
        self.a = random.randint(0, self.p)
        self.A = pow(self.g, self.a, self.p)
        self.msg = random.randint(33, 100).to_bytes(16, byteorder='big')

    def send_param(self):
        return self.p, self.g, self.A

    def receive_key(self, B):
        self.B = B
        self.s = pow(self.B, self.a, self.p)
        self.key = hashlib.sha1(str(self.s).encode('utf8')).hexdigest()[0:16].encode('utf8')

    def send_msg(self):
        iv = random.getrandbits(16*8).to_bytes(16, byteorder='big')
        obj = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + obj.encrypt(self.msg)

    def check_response(self, m):
        # decrypt message
        iv = m[0:16]
        obj = AES.new(self.key, AES.MODE_CBC, iv)
        msg = obj.decrypt(m[16:])
        num = int.from_bytes(msg, byteorder='big')
        # check if number in message in incrementd self.msg
        num -= 1
        if self.msg == num.to_bytes(16, byteorder='big'):
            print("Check OK")
            return True
        else:
            print("Check error")
            print("got:     ", msg)
            print("shoud be:", num.to_bytes(16, byteorder='big'))
            return False


class Bob:
    def receive_param(self, p, g, A):
        self.p = p
        self.g = g
        self.A = A
        self.b = random.randint(0, self.p)
        self.B = pow(self.g, self.b, self.p)
        self.s = pow(self.A, self.b, self.p)
        self.key = hashlib.sha1(str(self.s).encode('utf8')).hexdigest()[0:16].encode('utf8')

    def send_key(self):
        return self.B

    def send_response(self, m):
        # decrypt message
        iv = m[0:16]
        obj = AES.new(self.key, AES.MODE_CBC, iv)
        msg = obj.decrypt(m[16:])
        num = int.from_bytes(msg, byteorder='big')
        # increment number from message
        num += 1
        # encrypt message
        obj2 = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + obj2.encrypt(num.to_bytes(16, byteorder='big'))


def decode_msg(p, g, msg):
    def decrypt(s, msg):
        iv = msg[0:16]
        key = hashlib.sha1(str(s).encode('utf8')).hexdigest()[0:16].encode('utf8')
        obj = AES.new(key, AES.MODE_CBC, iv)
        m = obj.decrypt(msg[16:])
        return m

    if g == 1:
        m = decrypt(1, msg)
    elif g == p:
        m = decrypt(0, msg)
    elif g == p-1:
        m1 = decrypt(1, msg)
        m2 = decrypt(p-1, msg)
        m = m1 if m1[0] == 0 else m2

    print("decoded message:", m)


def mitm(g):
    m = True  # MITM
    if g == 1:
        print("MITM for g:1")
    elif g == p_nist:
        print("MITM for g:p")
    elif g == p_nist-1:
        print("MITM for g:p-1")
    elif g == 0:
        print("normal run")
        m = False

    alice = Alice()
    if m:
        alice.g = g  # MITM
        alice.A = g  # MITM
    bob = Bob()
    p, g, A = alice.send_param()
    bob.receive_param(p, g, A)
    B = bob.send_key()
    alice.receive_key(B)
    m1 = alice.send_msg()
    if m:
        decode_msg(p, g, m1)  # decode msg
    m2 = bob.send_response(m1)
    if m:
        decode_msg(p, g, m2)  # decode msg
    alice.check_response(m2)
    del alice
    del bob


def main():
    # normal protocol for echo bot
    mitm(0)

    # MITM
    mitm(1)
    mitm(p_nist)
    mitm(p_nist-1)

if __name__ == "__main__":
    main()
