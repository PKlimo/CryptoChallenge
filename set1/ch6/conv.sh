# binary file to text file in hex form
xxd -u -p data.bin | tr -d "\n"

# binary file display 10 bytes in binary representation, each line contains 5 bytes
xxd  -l 10 -g 1 -c 5 -b data.bin
