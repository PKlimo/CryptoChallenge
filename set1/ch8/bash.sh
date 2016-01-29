#!/bin/bash

for line in $(cat data.hex); do
        dupl=$( echo $line | tr -d "\n" | fold -b16 | sort | uniq -d )
        if [ -n "$dupl" ]; then # if string $dupl is not empty
                echo "Line with duplicite blocks:"
                echo $line
                echo "duplicite blocks:"
                echo $dupl
        fi
done

