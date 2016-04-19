#!/usr/bin/env python3
from __future__ import print_function
import random
import hashlib
import hmac

p = 0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff
g = 2
k = 3


class Server:
    def register(self, email, password, salt):
        self.email = email.encode('utf-8') if type(email) == str else email
        self.salt = salt.encode('utf-8') if type(salt) == str else salt
        passwd = password.encode('utf-8') if type(password) == str else password
        xH = hashlib.sha256(self.salt + passwd).hexdigest()
        x = int(xH, 16)
        self.verifier = pow(g, x, p)

    def login(self, email, A):
        self.A = A
        self.__b = random.randint(1, p)
        self.B = k*self.verifier+pow(g, self.__b, p)

    def compute_key(self):
        u = hashlib.sha256(str(self.A+self.B).encode('utf-8')).hexdigest().encode('utf-8')
        u = int.from_bytes(u, byteorder='big')
        s = self.A * pow(self.verifier, u, p)
        s = pow(s, self.__b, p)
        self.__K = hashlib.sha256(str(s).encode('utf-8')).hexdigest().encode('utf-8')

    def check_hmac(self, h2):
        h1 = hmac.new(self.__K, self.salt, hashlib.sha256).digest()
        if h1 == h2:
            print('HMAC is the same, login OK')
        else:
            print('HMAC is different, login FAILED')


class Client:
    def __init__(self):
        self.__a = random.randint(1, p)
        self.A = pow(g, self.__a, p)
        self.email = b'user@mail.com'
        self.__pass = b'passwd'
        self.salt = b'saltuseratmaildotcom'

    def get_pass(self):
        return self.__pass

    def compute_key(self, B):
        self.B = B
        u = hashlib.sha256(str(self.A+self.B).encode('utf-8')).hexdigest().encode('utf-8')
        u = int.from_bytes(u, byteorder='big')
        xH = hashlib.sha256(self.salt + self.__pass).hexdigest()
        x = int(xH, 16)
        s = self.B - k*pow(g, x, p)
        s = pow(s, self.__a+u*x, p)
        self.__K = hashlib.sha256(str(s).encode('utf-8')).hexdigest().encode('utf-8')

    def compute_hmac(self):
        h = hmac.new(self.__K, self.salt, hashlib.sha256).digest()
        return h


class MalClient:
    def __init__(self):
        self.email = b'user@mail.com'

    def compute_key(self):
        self.__K = hashlib.sha256(str(0).encode('utf-8')).hexdigest().encode('utf-8')

    def compute_hmac(self, salt):
        h = hmac.new(self.__K, salt, hashlib.sha256).digest()
        return h


def main():
    server = Server()
    client = Client()
    server.register(client.email, client.get_pass(), client.salt)
    server.login(client.email, client.A)
    client.compute_key(server.B)
    server.compute_key()
    h = client.compute_hmac()
    server.check_hmac(h)

    # malicious client (without password)
    mc = MalClient()
    server.login(mc.email, 0)
    mc.compute_key()
    server.compute_key()
    h = mc.compute_hmac(server.salt)
    server.check_hmac(h)

if __name__ == "__main__":
    main()
