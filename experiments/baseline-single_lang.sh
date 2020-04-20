#!/bin/bash -ex

for lang in "en-US" "es-ES" "pl-PL"; do
    mkdir -p data/baseline/${lang}

    #create dictionary
    cut -f2 ../corpora/0.1.0/leyzer-dev-${lang}-0.1.0.tsv \
        ../corpora/0.1.0/leyzer-test-${lang}-0.1.0.tsv \
        ../corpora/0.1.0/leyzer-train-${lang}-0.1.0.tsv | sort -u | \
        sed '/^intent$/d' > data/baseline/${lang}/dict.intents.csv

    cut -f4 ../corpora/0.1.0/leyzer-dev-${lang}-0.1.0.tsv \
        ../corpora/0.1.0/leyzer-test-${lang}-0.1.0.tsv \
        ../corpora/0.1.0/leyzer-train-${lang}-0.1.0.tsv | tr ' ' '\n' | \
        sort -u | sed '/^bio$/d' | sed '/^o$/g' | sed 's/^i-/I-/g' | \
        sed 's/^b-/B-/g' | sed '1 i O' > data/baseline/${lang}/dict.slots.csv

    #reformat corpus
    for part in "train" "test" "dev"; do
        paste <(cut -f3 ../corpora/0.1.0/leyzer-${part}-${lang}-0.1.0.tsv | tr '[A-Z]' '[a-z]') \
            <(cut -f2 ../corpora/0.1.0/leyzer-${part}-${lang}-0.1.0.tsv) | \
            sed 's/utterance\tintent/sentence\tlabel/g' > data/baseline/${lang}/${part}.tsv

        cut -f4 ../corpora/0.1.0/leyzer-${part}-${lang}-0.1.0.tsv | \
            sed 's/ o / O /g' | sed 's/ o / O /g' | sed 's/^o /O /g' | sed 's/ o$/ O/g' | \
            sed 's/b-/B-/g' | sed 's/i-/I-/g' | \
            sed '1d' > data/baseline/${lang}/${part}_slots.tsv
    done
done
