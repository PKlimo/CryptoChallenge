#!/usr/bin/env python3
from __future__ import print_function
from struct import pack
from binascii import hexlify


def print_state(mt):
    for i in range(0, 624):
        print(hexlify(pack(">I", mt[i])).decode("ascii"), end="")


def print_state_part(mt, i):
    if not 0 <= i <= 623:
        print("Index out of range <0,623>, i: ", i)
        return
    print("mt[", i, "]: ", hexlify(pack(">I", mt[i])).decode("ascii"), sep="")


def print_hex(msg, i):
    print(msg, "{0:x}".format(i))


def _int32(i):
    return int(0xFFFFFFFF & i)


def _high_mask(i):
    return int(0x80000000 & i)


def _low_mask(i):
    return int(0x7FFFFFFF & i)


def extract_number(mt, index):
    y = mt[index]

    # print_hex("1:", y)
    y ^= (y >> 11)
    # print_hex("2:", y)
    y ^= (y << 7) & 0x9D2C5680
    # print_hex("3:", y)
    y ^= (y << 15) & 0xEFC60000
    # print_hex("4:", y)
    y ^= (y >> 18)
    # print_hex("5:", y)

    return _int32(y)


def unextract_number(rnd, index):
    y = rnd
    y ^= (y >> 18)
    # print_hex("4:", y)
    y ^= (y << 15) & 0xEFC60000
    # print_hex("3:", y)
    y ^= ((y << 7) & 0x9D2C5680) ^ ((y << 14) & 0x94284000) ^ ((y << 21) & 337641472) ^ ((y << 28) & 268435456)
    # print_hex("2:", y)
    y ^= (y >> 11) ^ (y >> 22)
    # print_hex("1:", y)
    return y


def init(seed):
    _mt = [0] * 624
    _mt[0] = _int32(seed)
    for i in range(1, 624):
        _mt[i] = _int32(int(1812433253) * (_mt[i-1] ^ (_mt[i-1] >> 30)) + i)
    return _mt


def uninit(mt):
    # from init state return seed
    if not is_init(mt):
        print("state is not init state")
        return

    def egcd(a, b):
        if a == 0:
            return (b, 0, 1)
        else:
            g, y, x = egcd(b % a, a)
            return (g, x - (b // a) * y, y)

    def inverse():
        # https://en.wikipedia.org/wiki/Modular_multiplicative_inverse
        gcd, x, y = egcd(1812433253, 2**32)
        if gcd == 1:
            return (x % 2**32)

    pok = _int32(int(inverse())*int(mt[1]-1))
    seed = pok ^ (pok >> 30)
    return seed


def twist_part(mt, i):
    x = _int32(_high_mask(mt[i]) + _low_mask(mt[(i+1) % 624]))
    xA = x >> 1
    if (x % 2) != 0:
        xA = xA ^ 0x9908B0DF
    return mt[(i+397) % 624] ^ xA


def twist(mt):
    _mt = list(mt)
    for i in range(0, 624):
        _mt[i] = twist_part(_mt, i)
    return _mt


def untwist_part_compute(cur, prev, next, oposite, oposite_prev):
    xA = cur ^ oposite
    if (next % 2) != 0:
        xA = xA ^ 0x9908B0DF
    x = xA << 1
    if (next % 2) != 0:
        x += 1
    h = _int32(_high_mask(x))

    xA1 = prev ^ oposite_prev  # if last bit of untwisted mt[i] = 0
    xA2 = xA1 ^ 0x9908B0DF  # if last bit of untwisted mt[i] = 1
    x1 = xA1 << 1
    x2 = (xA2 << 1) + 1
    l1 = _int32(_low_mask(x1))
    l2 = _int32(_low_mask(x2))
    return [h + l1, h + l2]


def untwist_part(mt, mtg, i):
    cur = mt[i]
    next = mt[(i + 1) % 624]
    prev = mt[(i - 1) % 624]
    if i > 227:
        oposite = mt[(i+397) % 624]
        oposite_prev = mt[(i+396) % 624]
    elif i == 227:
        oposite = mtg[(i+397) % 624]
        oposite_prev = mt[(i+396) % 624]
    elif i < 227:
        oposite = mtg[(i+397) % 624]
        oposite_prev = mtg[(i+396) % 624]

    return untwist_part_compute(cur, prev, next, oposite, oposite_prev)


def debug_untwist(mt, mto, mtp, mtn, i, mt_00, mt_01, mt_10, mt_11):
    if -225 <= i <= 226:
        print(i, ":", sep="")
        print("old state ", " "*6, end="")
        print_state_part(mto, i)
        print("new state ", " "*6, end="")
        print_state_part(mt, i)
        print("guess even state ", end="")
        print_state_part(mtp, i)
        print("guess odd state  ", end="")
        print_state_part(mtn, i)
        print_hex("twist even state  ", twist_part(mtp, i))
        print_hex("twist odd state   ", twist_part(mtn, i))
        print_hex("twist state   ", twist_part(mt_00, i))
        print_hex("twist state   ", twist_part(mt_01, i))
        print_hex("twist state   ", twist_part(mt_10, i))
        print_hex("twist state   ", twist_part(mt_11, i))


def untwist(mt):
    mtp = list(mt)  # even
    mtn = list(mt)  # odd
    mtg = list(mt)  # good
    for i in range(623, -1, -1):
        guess_even, guess_odd = untwist_part(mtp, mtg, i)
        mtp[i] = guess_even
        mtn[i] = guess_odd
        if i < 623:
            mt_00 = list(mtg)
            mt_00[i+1] = mtp[i+1]
            mt_00[i] = guess_even
            mt_01 = list(mtg)
            mt_01[i+1] = mtp[i+1]
            mt_01[i] = guess_odd
            mt_10 = list(mtg)
            mt_10[i+1] = mtn[i+1]
            mt_10[i] = guess_even
            mt_11 = list(mtg)
            mt_11[i+1] = mtn[i+1]
            mt_11[i] = guess_odd
            # debug_untwist_1(mt, mto, mtp, mtn, i, mt_00, mt_01, mt_10, mt_11)
            if twist_part(mt_00, i) == mt[i]:
                mtg[i+1] = mtp[i+1]
            elif twist_part(mt_01, i) == mt[i]:
                mtg[i+1] = mtp[i+1]
            elif twist_part(mt_10, i) == mt[i]:
                mtg[i+1] = mtn[i+1]
            elif twist_part(mt_11, i) == mt[i]:
                mtg[i+1] = mtn[i+1]
            else:
                print("unknown good")
        if i == 0:
            if twist_part(mtp, 0) == mt[0]:
                mtg[0] = guess_even
            elif twist_part(mtn, 0) == mt[0]:
                mtg[0] = guess_odd
            else:
                print("unknown good")
            # debug_untwist(mt, mto, mtp, mtn, i, mt_00, mt_01, mt_10, mt_11)
    # print_states("mt/mtg", mt, mtg)
    return mtg


def compare_states(kon, mt1, mt2):
    ret = True
    for i in range(623, kon, -1):
        if mt1[i] != mt2[i]:
            print("differance in part ", i)
            ret = False
    return ret


def print_states(nazov, st1, st2):
    for i in range(615, 624):
        print_state_part(st1, i)
        print_state_part(st2, i)


def is_init(mt):
    for i in range(2, 624):
        if mt[i] != _int32(int(1812433253) * (mt[i-1] ^ (mt[i-1] >> 30)) + i):
            return False
    return True


if __name__ == "__main__":
    mt = [0] * 624
    mt = init(42)
    mt_next = twist(mt)

    for i in range(8):
        print(extract_number(mt_next, i))
    exit()

    # untwist() test coverage
    mt_next_prev = untwist(mt_next)
    compare_states(0, mt, mt_next_prev)  # mt[0] is not recoverable
    compare_states(-1, mt_next, twist(mt_next_prev))

    # is_init() test coverage
    print("is_init(mt):", is_init(mt))
    print("is_init(mt_next):", is_init(mt_next))
    print("is_init(mt_next_prev):", is_init(mt_next_prev))
    print()

    # uninit()
    print("seed:", uninit(mt))
    print("seed:", uninit(mt_next))
    print("seed:", uninit(mt_next_prev))
    print()

    # unextract_number()
    print_state_part(mt_next, 123)
    rn = extract_number(mt_next, 123)
    print_hex("rnd number from mt[123]:", rn)
    print_hex("recovered state from rnd:", unextract_number(rn, 123))
