#!/usr/bin/env python3
from __future__ import print_function
import random
import hashlib
import hmac

p = 0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff
g = 2


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
        self.B = pow(g, self.__b, p)

    def compute_key(self):
        self.u = random.randint(0, 2**128-1)
        s = self.A * pow(self.verifier, self.u, p)
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

    def compute_key(self, B, u):
        self.B = B
        xH = hashlib.sha256(self.salt + self.__pass).hexdigest()
        x = int(xH, 16)
        s = pow(self.B, self.__a+u*x, p)
        self.__K = hashlib.sha256(str(s).encode('utf-8')).hexdigest().encode('utf-8')

    def compute_hmac(self):
        h = hmac.new(self.__K, self.salt, hashlib.sha256).digest()
        return h


class MaliciousServer:
    def login(self, email, A):
        self.A = A
        self.__b = 3
        self.B = pow(g, self.__b, p)

    def compute_key(self):
        self.u = 1

    def crack_pass(self, h, salt):
        print('cracking started')
        pwdict = (b'not good', b'passwd', b'wrong', b'error')
        for passwd in pwdict:
            xH = hashlib.sha256(salt + passwd).hexdigest()
            x = int(xH, 16)
            s = self.A * pow(g, x, p)
            s = pow(s, 3, p)
            K = hashlib.sha256(str(s).encode('utf-8')).hexdigest().encode('utf-8')
            hg = hmac.new(K, salt, hashlib.sha256).digest()
            if hg == h:
                print('cracked password is:', passwd)
                break


def main():
    server = Server()
    client = Client()
    server.register(client.email, client.get_pass(), client.salt)
    server.login(client.email, client.A)
    server.compute_key()
    client.compute_key(server.B, server.u)
    h = client.compute_hmac()
    server.check_hmac(h)

    # MITM Malicious server
    mc = MaliciousServer()
    mc.login(client.email, client.A)
    mc.compute_key()
    client.compute_key(mc.B, mc.u)
    h = client.compute_hmac()
    mc.crack_pass(h, client.salt)

if __name__ == "__main__":
    main()
