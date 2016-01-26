#!/bin/bash

wget http://cryptopals.com/static/challenge-data/6.txt -O data.b64
cat data.b64 | base64 -d >  data.bin
cat data.bin | hexdump -v -e '/1 "%02X "' | tr -d " " > data.hex
