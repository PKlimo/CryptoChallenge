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

    y ^= (y >> 11)
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    y ^= (y >> 18)

    return _int32(y)


def init(seed):
    _mt = [0] * 624
    _mt[0] = _int32(seed)
    for i in range(1, 624):
        _mt[i] = _int32(int(1812433253) * (_mt[i-1] ^ (_mt[i-1] >> 30)) + i)
    return _mt


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


def untwist_part(mt, i):
    cur = mt[i]
    next = mt[(i + 1) % 624]
    prev = mt[(i - 1) % 624]
    oposite = mt[(i+397) % 624]
    oposite_prev = mt[(i+396) % 624]

    g1, g2 = untwist_part_compute(cur, prev, next, oposite, oposite_prev)

    mt1 = list(mt)
    mt2 = list(mt)
    mt1[i] = g1
    mt2[i] = g2
    return [mt1, mt2]


def untwist(mt):
    # TODO refaktorizacia
    # untwist_part_check_guess - z dvoch hodnot predchadzajuceho vypoctu vrati spravnu
    # mtp a mtn - kompletne stavy sa nahradia iba parcialnymi castami stavov
    kon = 220
    mtp = list(mt)  # even
    mtn = list(mt)  # odd
    mtg = list(mt)  # good
    for i in range(623, kon, -1):
        mtp, _mtn = untwist_part(mtp, i)
        mtn[i] = _mtn[i]
        # print(i, ":", sep="")
        # print("old state ", " "*6, end="")
        # print_state_part(mt, i)
        # print("new state ", " "*6, end="")
        # print_state_part(mt, i)
        # print("guess even state ", end="")
        # print_state_part(mtp, i)
        # print("guess odd state  ", end="")
        # print_state_part(_mtn, i)
        if i < 623:
            if twist_part(mtp, i) == mt[i]:
                # print("even good")
                mtg[i+1] = mtp[i+1]
            if twist_part(mtn, i) == mt[i]:
                # print("odd good")
                mtg[i+1] = mtn[i+1]
    # print_states("mt/mtg", mt, mtg)
    return mtg


def compare_states(kon, mt1, mt2):
    for i in range(623, kon, -1):
        if mt1[i] != mt2[i]:
            print("differance in part ", i)


def print_states(nazov, st1, st2):
    for i in range(615, 624):
        print_state_part(st1, i)
        print_state_part(st2, i)


if __name__ == "__main__":
    mt = [0] * 624
    mt = init(42)
    mt_next = twist(mt)
    # sollution
    mt_next_prev = untwist(mt_next)
    kon = 220
    compare_states(kon, mt, mt_next_prev)

    index = 0
