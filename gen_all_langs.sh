#!/bin/bash
TARGET_DIR=${1:-all_langs}

for lang in en-US es-ES pl-PL
do
    domains=grammars/${lang}/*.gram
    for domain in ${domains}
    do
        domain=$(basename $domain .gram)
        python3 JSGFTools/DeterministicGenerator.py grammars/${lang}/${domain}.gram > patterns/${lang}/${domain}.tsv
        mkdir -p corpora/${TARGET_DIR}/${lang}
        ./scripts/expand-slots.sh ${lang} patterns/${lang}/${domain}.tsv corpora/${TARGET_DIR}/${lang}/${domain}.tsv true true
    done
done