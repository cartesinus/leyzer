#!/bin/bash

LANG=$1
INPUT_FILE=$2

for slot in `ls -1 slots/${LANG}`; do
    if grep --quiet "$slot" $INPUT_FILE; then
        echo "expanding with phrases from $slot."
        while IFS= read -r text; do
            sed -ie "0,/$slot/ s/$slot/$text/" $INPUT_FILE
        done < slots/$LANG/$slot
    fi;
done
