#!/usr/bin/env python3
import numpy as np
import struct

rn = np.random.RandomState(42)
for j in range(8):
    i = struct.unpack("<L", rn.bytes(4))[0]
    print(i)
