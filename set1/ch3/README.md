implementation in C:
name: `crypto_xor_find_one_byte_key`
description: find the best key (byte) for which the xored output has the biggest score (most likely english text)
input parameter: file in binary mode
output: one text line in form: score;key;decoded text
score: integer (for text file: space:5pt, 5 most common chars: 3pt, printable chars: 1pt
key: the best byte in ASCII form (see view output hint for printing non ASCII value via xxd)
decoded text: ASCII output decoded (xored) by key byte
hint: use xxd to work with input/output binary datas
# convert binary file to text file in hex form
xxd -u -p data.bin | tr -d "\n"
# binary file display 10 bytes in binary representation, each line contains 5 bytes
xxd  -l 10 -g 1 -c 5 -b data.bin
# convert text hex file into binary
xxd -p -r input.txt > input.bin
#viev output:
`./crypto_xor_byte file.bin | xxd`
