#!/usr/bin/env python2

import srp

# The salt and verifier returned from srp.create_salted_verification_key() should be
# stored on the server.
salt, vkey = srp.create_salted_verification_key('testuser', 'testpassword')


class AuthenticationFailed (Exception):
    pass


# ~~~ Begin Authentication ~~~

usr = srp.User('testuser', 'testpassword')
uname, A = usr.start_authentication()

# The authentication process can fail at each step from this
# point on. To comply with the SRP protocol, the authentication
# process should be aborted on the first failure.

# Client => Server: username, A
svr = srp.Verifier(uname, salt, vkey, A)
s, B = svr.get_challenge()

if s is None or B is None:
    raise AuthenticationFailed()

# Server => Client: s, B
M = usr.process_challenge(s, B)

if M is None:
    raise AuthenticationFailed()

# Client => Server: M
HAMK = svr.verify_session(M)

if HAMK is None:
    raise AuthenticationFailed()

# Server => Client: HAMK
usr.verify_session(HAMK)

# At this point the authentication process is complete.

assert usr.authenticated()
assert svr.authenticated()
#  malicious client without password


def long_to_bytes(n):
    l = list()
    x = 0
    off = 0
    while x != n:
        b = (n >> off) & 0xFF
        l.append(chr(b))
        x = x | (b << off)
        off += 8
    l.reverse()
    return ''.join(l)


A = long_to_bytes(0)
svr = srp.Verifier(uname, salt, vkey, A)
#  s, B = svr.get_challenge()
