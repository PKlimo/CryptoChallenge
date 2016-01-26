#!/usr/bin/env python3

"""Usage: sollution [-h | --help] [-v] [-f FILE] [-S HISNUM] [-s] [-k]

Options:
    -h --help       Show help screen
    -v              Print verbose output
    -f FILE         input file [default: data.hex]
    -s              Show histogram of 20 bytes
    -S HISNUM       Show histogram of HISNUM bytes
    -k              Print normalized Hammington distances for different key length <2,40>
"""

from __future__ import print_function
import bitstring
import docopt
import sys


def hamdist(str1, str2):
    diffs = 0
    assert len(str1) == len(str2), "length of arguments are different"
    for i in range(len(str1)):
        a = bitstring.pack('uint:8', str1[i])
        b = bitstring.pack('uint:8', str2[i])
        diffs += (a ^ b).count(True)
    return diffs


def histogram(data, num):
    from collections import Counter
    c = Counter(data)
    for value, frequency in c.most_common(num):
        print("0x{:02x}: {}".format(value, frequency))


def normham(data, keylen):
    global verb
    b1 = data[0*keylen:1*keylen]
    b2 = data[1*keylen:2*keylen]
    b3 = data[2*keylen:3*keylen]
    b4 = data[3*keylen:4*keylen]
    b5 = data[4*keylen:5*keylen]
    b6 = data[5*keylen:6*keylen]
    hd1 = hamdist(b1, b2)
    hd2 = hamdist(b3, b4)
    hd3 = hamdist(b5, b6)
    hd = (hd1 + hd2 + hd3) / 3
    hd = hd1
    ret = hd / keylen
    if verb:
        print("Normalized Hammington distance: "+str(ret)+" Hammingotn distance: "+str(hd)+" Key length: "+str(keylen))
    return ret

if __name__ == "__main__":
    assert hamdist("this is a test".encode('ascii'), "wokka wokka!!!".encode('ascii')) == 37, "error in hamdist function"
    assert hamdist(b'\x03\xfd', b'\x05\xfe') == 4, "error in hamdist function"
    assert hamdist(bytes(b'\xff'), bytes(b'\xfe')) == 1, "error in hamdist function"
    arguments = docopt.docopt(__doc__)

    # parse arguments
    fn = arguments['-f'] if arguments['-f'] is not None else "data.hex"
    verb = arguments['-v']
    if verb:
        print("Arguments:\n"+str(arguments), file=sys.stderr)
        print("\nOpening file: "+fn, file=sys.stderr)

    # open file
    with open(fn, "rt") as f:
        lines = f.readlines()
    data = bytearray.fromhex(lines[0].strip())

    # show histogram of bytes
    if arguments['-s'] or (arguments['-S'] is not None):
        hisnum = int(arguments['-S']) if arguments['-S'] is not None else 20
        if verb:
            print("Showing histogram for "+str(hisnum)+" bytes", file=sys.stderr)
        histogram(data, hisnum)

    # guess key length
    if arguments['-k']:
        for k in range(2, 41):
            n = str(k)+"  "+str(normham(data, k))
            if not verb:
                print(n)
