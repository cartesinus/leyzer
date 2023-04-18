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
            sed -ie -E "0,/$slot$|$slot / s/$slot$|$slot /{$short_slot:$text} /" $INPUT_FILE
        else
            sed -ie -E "0,/$slot$|$slot / s/$slot$|$slot /$text /" $INPUT_FILE
        fi
    done < ../slots/$LANG/$slot
}

sed -i 's/__ /__	/g' $INPUT_FILE

for slot in `ls -1 ../slots/${LANG}`; do
    if grep --quiet "$slot$\|$slot " $INPUT_FILE; then
        echo "expanding with phrases from $slot."
        if [ "$REPEAT" = "true" ]; then
            while grep --quiet "$slot$\|$slot " $INPUT_FILE; do
                substitute_slots $slot
            done
        else
            substitute_slots $slot
        fi;
    fi;
done

sed -i 's/ $//g' $INPUT_FILE

if [ "$ADD_BIO" = "true" ]; then
    echo "Saving patterns expanded with slot values to: $OUTPUT_FILE"
    paste <(cut -f1-4 $INPUT_FILE) <(cut -f5 $INPUT_FILE | ./convert_str_to_bio.py) > $OUTPUT_FILE
fi
