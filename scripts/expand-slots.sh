#!/bin/bash

LANG=$1
INPUT_FILE=$2
REPEAT=${3:-"true"}

function substitute_slots {
    slot=$1
    while IFS= read -r text; do
        sed -ie "0,/$slot/ s/$slot/$text/" $INPUT_FILE
    done < slots/$LANG/$slot
}

for slot in `ls -1 slots/${LANG}`; do
    if grep --quiet "$slot" $INPUT_FILE; then
        echo "expanding with phrases from $slot."
        if [ "$REPEAT" = "true" ]; then
            while grep --quiet "$slot" $INPUT_FILE; do
                substitute_slots $slot
            done
        else
            substitute_slots $slot
        fi;
    fi;
done
