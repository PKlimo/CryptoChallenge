#!/bin/bash

#for i in {1..100}
#do
#        ./sollution.py >> output.txt
#done

cat output.txt | sort | uniq > tmp.txt
mv tmp.txt output.txt

