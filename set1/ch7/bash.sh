#!/bin/bash

openssl enc -d -aes-128-ecb -in data.bin -K $(echo -n "YELLOW SUBMARINE" | xxd -p)
