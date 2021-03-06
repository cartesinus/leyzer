#!/bin/bash -ex

LEYZER_PATH=$1
OUTPUT_PATH=$2

for lang in "en-US" "es-ES" "pl-PL"; do
    mkdir -p ${OUTPUT_PATH}/data/baseline/${lang}

    #create dictionary
    cut -f2 ${LEYZER_PATH}/corpora/0.1.0/leyzer-dev-${lang}-0.1.0.tsv \
        ${LEYZER_PATH}/corpora/0.1.0/leyzer-test-${lang}-0.1.0.tsv \
        ${LEYZER_PATH}/corpora/0.1.0/leyzer-train-${lang}-0.1.0.tsv | sort -u | \
        sed '/^intent$/d' > ${OUTPUT_PATH}/data/baseline/${lang}/dict.intents.csv

    cut -f4 ${LEYZER_PATH}/corpora/0.1.0/leyzer-dev-${lang}-0.1.0.tsv \
        ${LEYZER_PATH}/corpora/0.1.0/leyzer-test-${lang}-0.1.0.tsv \
        ${LEYZER_PATH}/corpora/0.1.0/leyzer-train-${lang}-0.1.0.tsv | tr ' ' '\n' | \
        sort -u | sed '/^bio$/d' | sed '/^o$/g' | sed 's/^i-/I-/g' | \
        sed 's/^b-/B-/g' | sed '1 i O' > ${OUTPUT_PATH}/data/baseline/${lang}/dict.slots.csv

    #reformat corpus
    for part in "train" "test" "dev"; do
        paste <(cut -f3 ${LEYZER_PATH}/corpora/0.1.0/leyzer-${part}-${lang}-0.1.0.tsv | tr '[A-Z]' '[a-z]') \
            <(cut -f2 ${LEYZER_PATH}/corpora/0.1.0/leyzer-${part}-${lang}-0.1.0.tsv) | \
            sed 's/utterance\tintent/sentence\tlabel/g' > ${OUTPUT_PATH}/data/baseline/${lang}/${part}.tsv

        cut -f4 ${LEYZER_PATH}/corpora/0.1.0/leyzer-${part}-${lang}-0.1.0.tsv | \
            sed 's/ o / O /g' | sed 's/ o / O /g' | sed 's/^o /O /g' | sed 's/ o$/ O/g' | \
            sed 's/b-/B-/g' | sed 's/i-/I-/g' | \
            sed '1d' > ${OUTPUT_PATH}/data/baseline/${lang}/${part}_slots.tsv
    done
done
