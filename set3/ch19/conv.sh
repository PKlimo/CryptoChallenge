#!/bin/bash
 for line in $(cat data.b64)
 do
         echo "$line" | base64 -d
         echo
 done
