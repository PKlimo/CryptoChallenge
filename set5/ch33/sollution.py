#!/usr/bin/env python3
import random

p = 0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff
g = 2

a = random.randint(0, p)
print('private key for a:', a)

A = pow(g, a, p)  # A = (g**a) % p
print('public key for a:', A)

b = random.randint(0, p)
print('private key for b:', b)

B = pow(g, b, p)  # B = (g**b) % p
print('public key for b:', B)

sa = pow(B, a, p)  # sa = (B**a) % p
print('shared secreto for a:', sa)

sb = pow(A, b, p)  # sb = (A**b) % p
print('shared secreto for b:', sb)

assert(sa == sb)  # secret must be the same
