#!/bin/bash

rm -f tmp.txt
for line in $(cat data.b64)
do
        echo "$line" | base64 -d >> tmp.txt
        echo >> tmp.txt
done

cat tmp.txt | sort | uniq > data.txt
