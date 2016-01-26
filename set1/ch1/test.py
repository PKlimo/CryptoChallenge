#!/usr/bin/env python3

sh1 = 'cat input.txt | ./sollution.py'
sh2 = 'cat input.txt | ./sollution.py | cmp -lb output.txt | head -n 20'

import sarge
print(sarge.capture_stdout(sh1).stdout.text)
print(sarge.capture_stdout(sh2).stdout.text)
