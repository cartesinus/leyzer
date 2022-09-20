#!/bin/bash

for lang in en-US es-ES pl-PL
do
    domains=grammars/${lang}/[!console]*.gram
    for domain in ${domains}
    do
        domain=$(basename $domain .gram)
        python3 JSGFTools/DeterministicGenerator.py grammars/${lang}/${domain}.gram > patterns/${lang}/${domain}.tsv
        mkdir -p corpora/all_langs/${lang}
        ./scripts/expand-slots.sh ${lang} patterns/${lang}/${domain}.tsv corpora/all_langs/${lang}/${domain}.tsv true true
    done
done