#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import urllib
import hmac
import hashlib

hostName = "localhost"
hostPort = 9000


class PlayGround:
    def __init__(self):
        self.__key = b"key"
        self.__sleep = 0.05

    def check(self, msg, mac_prov):
        return self.__compare(mac_prov, hmac.new(self.__key, msg, hashlib.sha1).hexdigest())

    def __compare(self, a, b):
        for i in range(40):
            if a[i] != b[i]:
                return False
            time.sleep(self.__sleep)
        return True


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        arg = urllib.parse.parse_qs(parsed_path[4])
        fn = arg['file'][0]
        sig = arg['signature'][0]
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if pg.check(fn.encode('ascii'), sig):
            self.wfile.write(bytes("OK", "utf-8"))
        else:
            self.wfile.write(bytes("invalid", "utf-8"))


def main():
    myServer = HTTPServer((hostName, hostPort), MyServer)
    print('http://localhost:9000/test?file=foo&signature=9fc254126c2b1b7f106abacae0cb77e73411fad7')
    try:
        myServer.serve_forever()
    except KeyboardInterrupt:
        pass
    myServer.server_close()


if __name__ == "__main__":
    pg = PlayGround()
    main()
