#!/usr/bin/env python3
from __future__ import print_function
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Util import number
import binascii
debug = True
debug = False


def getKey():
    import os.path
    if not os.path.isfile('key.pem'):
        if debug:
            print('generating key')
        key = RSA.generate(3072, e=3)
        ex_key = key.exportKey()
        with open('key.pem', 'wb') as of:
            of.write(ex_key)
    else:
        if debug:
            print('loading key from file')
        with open('key.pem', 'rb') as f:
            key = RSA.importKey(f.read())
    return key


def get_signature_padding_len(signature, pub_key):
    dec = pub_key.encrypt(signature, '')[0]
    for pos, z in enumerate(dec[1:]):
        if z == 0x00:
            return pos
        if z != 0xff:
            return None


def debug_valid_signature(valid_signature, pub_key):
    # check verification - encrypt by publick key to get pagged hash
    dec = pub_key.encrypt(valid_signature, '')[0]
    print("Length of signature:", len(dec))
    print("Length of n:", len(number.long_to_bytes(pub_key.n)))
    print(binascii.hexlify(dec))
    # parse signature
    pad_len = get_signature_padding_len(valid_signature, pub_key)
    der_enc = binascii.hexlify(dec[pad_len+2:pad_len+17])
    hash_en = binascii.hexlify(dec[pad_len+17:])
    # print info
    print('=== ucrypted signature === ')
    print('documentation: rfc 3447 section 9.2. fnct name EMSA-PKCS1-v1_5-ENCODE(hash, len)')
    print('length of whole signature:', len(dec))
    print('bt (len: 1 ):', dec[0])
    print('ff padding (len:', pad_len, '): 0xff')
    print('zero byte (len: 1 ):', dec[pad_len+1])
    print('DER enc (len:', len(der_enc) // 2, '):', der_enc)
    print('hash (len:', len(hash_en) // 2, '):', hash_en)
    # print('=== Raw Data ===')
    # print(binascii.hexlify(dec))


def debug_msg_hash(message, h):
    print("msg:", message)
    print("SHA 1 hash of msg:", h.hexdigest())


def check_signature_correct(message, valid_signature, pub_key):
    dec = pub_key.encrypt(valid_signature, '')[0]
    # check block type
    if dec[0] != 1:
        return False
    # check padding 0xff
    pad_len = get_signature_padding_len(valid_signature, pub_key)
    # check DER encoding for SHA 1
    if dec[pad_len+2:pad_len+17] != b'0!0\t\x06\x05+\x0e\x03\x02\x1a\x05\x00\x04\x14':
        return False
    # check SHA 1 hash
    h_given = binascii.hexlify(dec[pad_len+17:]).decode('utf-8')
    h_computed = SHA.new(message).hexdigest()
    if h_given != h_computed:
        return False
    return True


def check_signature_bug(message, valid_signature, pub_key):
    assert(pub_key.e == 3)
    # decrypt verification
    enc = number.bytes_to_long(valid_signature)
    dec = number.long_to_bytes(pow(enc, 3, pub_key.n))
    # check signature
    check_str = b'\xff\x00' + \
        b'0!0\t\x06\x05+\x0e\x03\x02\x1a\x05\x00\x04\x14' + \
        binascii.unhexlify(SHA.new(message).hexdigest().encode('utf-8'))
    return (check_str in dec)


def dpl(n, x):
    print(n, binascii.hexlify(number.long_to_bytes(x)))


def create_forge_signature(msg, pub_key):
    # based on paper:
    # "Bleichenbacher's RSA-Signature Forgery" - Solving Prof. Stamp's Challenge Number 21
    # Steffen Rumpf
    assert pub_key.e == 3, "Works only for public key 3"
    # input parameters
    l = 384                                  # length of the signature EB in bytes
    nff = 50
    Data = b'\x30\x21\x30\x09\x06\x05\x2b\x0e\x03\x02\x1a\x05\x00\x04\x14'  # DER code
    Data += b'\x92\x5a\x89\xb4\x3f\x3c\xaf\xf5\x07\xdb\x0a\x86\xd2\x0a\x24\x28\x00\x7f\x10\xb6'  # hash of string 'hi mom'
    # derived values from input parameters
    D = number.bytes_to_long(Data)
    Dlen = len(Data)
    de = (l-2-nff)*8                         # position (in bytes) where the padding block (\xff) ens
    ds = (l-3-nff-Dlen)*8                     # position (in bytes) where the data block starts
    n = l * 8                               # length of the signature EB in bites
    x = n - 15
    assert(x % 3 == 0)
    assert(ds > 2*x//3)
    N = 2**(de-ds) - D
    assert (N % 3 == 0)
    # compute G
    A = 2**(x//3)
    B = N*2**(ds-2*x//3)//3
    LS7 = (A-B)**3                          # left side of equation 7 on page 8 from paper
    RS7 = A**3 - 3*A*A*B + 3*A*B*B - B**3   # right side of equation 7 on page 8 from paper
    assert(RS7 == LS7)
    G = 3*A*B*B-B**3                        # computed garbage
    # dpl('G:', G)
    EB4 = (2**x)-(2**de)+(D*2**ds)+G        # EB based on equation 4 on page 6
    # problem if G is too big and is mixed with data
    # pok = (2**x)-(2**de)
    # pok2 = (D*2**ds)
    # pok3 = pok + pok2
    # dpl('pok', pok)
    # dpl('pok2', pok2)
    # dpl('pok3', pok3)
    # dpl('pok3+G', pok3+G)
    # print('len(G):', len(number.long_to_bytes(G)))
    # print('n-Dlen-nff:', l - Dlen - nff)
    assert l - Dlen - nff > len(number.long_to_bytes(G))
    EB5 = 2**x - N*(2**ds) + G              # EB based on equation 5.3 on page 6
    assert(EB5 == EB4)
    assert(EB5**3 == RS7**3)
    assert(pow(EB5, 3, pub_key.n) == pow(RS7, 3, pub_key.n))
    assert(EB5 == RS7)
    S = A - B  # encrypted signature
    assert(EB4 == S**3)
    dpl('dec(S):', S**3)
    if debug:
        dpl('Sign. :', S)
    return number.long_to_bytes(S)


def main():
    message = b'hi mom'
    h = SHA.new(message)
    if debug:
        debug_msg_hash(message, h)
    key = getKey()
    pub_key = key.publickey()
    signer = PKCS1_v1_5.new(key)
    valid_signature = signer.sign(h)
    debug_valid_signature(valid_signature, pub_key)
    print("=== Checking signatures ===")
    print("Checking valid signature with valid function:", check_signature_correct(message, valid_signature, pub_key))
    print("Checking valid signature with invalid function:", check_signature_bug(message, valid_signature, pub_key))
    print("=== Creating forge signature ===")
    forge_signature = create_forge_signature(message, pub_key)
    if debug:
        debug_valid_signature(forge_signature, pub_key)
    print("=== Checking forge signature ===")
    print("Checking forged signature with valid function:", check_signature_correct(message, forge_signature, pub_key))
    print("Checking forged signature with invalid function:", check_signature_bug(message, forge_signature, pub_key))


if __name__ == "__main__":
    main()
