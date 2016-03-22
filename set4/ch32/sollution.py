#!/usr/bin/env python3
import timeit


def main():
    print('http://localhost:9000/test?file=foo&signature=9fc254126c2b1b7f106abacae0cb77e73411fad7')
    # f = urllib.request.urlopen('http://localhost:9000/test?file=foo&signature=9fc254126c2b1b7f106abacae0cb77e73411fad7')
    # print(f.read())
    # s = "import urllib.request\nurllib.request.urlopen('http://localhost:9000/test?file=foo&signature=9fc254126c2b1b7f106abacae0cb77e73411fad7')"

    sig_ok = "9fc254126c2b1b7f106abacae0cb77e73411fad7"
    sig = ""
    for j in range(40):
        tt = {}
        for i in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']:
            s = "import urllib.request\nurllib.request.urlopen('http://localhost:9000/test?file=foo&signature=" + sig + i + "')"
            t = timeit.Timer(s)
            tt[i] = t.timeit(number=10)
        sig += max(tt, key=tt.get)
        print(j, sig)

    if sig == sig_ok:
        print("Succes")

if __name__ == "__main__":
    main()
