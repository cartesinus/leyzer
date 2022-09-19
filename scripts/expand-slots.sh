#!/bin/bash

LANG=$1
INPUT_FILE=$2
OUTPUT_FILE=$3
ADD_BIO=${4:-"false"}
REPEAT=${5:-"true"}

function substitute_slots {
    slot=$1
    while IFS= read -r text; do
        if [ "$ADD_BIO" = "true" ]; then
            short_slot=`echo $slot | sed 's/.*\.SLOT\.//g'`
            sed -ie "0,/$slot/ s/$slot/{$short_slot:$text}/" $INPUT_FILE
        else
            sed -ie "0,/$slot/ s/$slot/$text/" $INPUT_FILE
        fi
    done < slots/$LANG/$slot
}

sed -i 's/__ /__	/g' $INPUT_FILE

for slot in slots/${LANG}; do
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

if [ "$ADD_BIO" = "true" ]; then
    paste <(cut -f1-2 $INPUT_FILE) <(cut -f3 $INPUT_FILE | $PWD/scripts/convert_str_to_bio.py) > $OUTPUT_FILE
fi
