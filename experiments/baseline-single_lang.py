# -*- coding: utf-8 -*-
"""Replicate baseline models for en, es and pl.

This script, designed to be run on colab, will convert leyzer corpora to atis format and train
3 baseline models.

To convert this script to ipynb you can use https://pypi.org/project/ipynb-py-convert/.
"""

!pip install nemo-nlp
!git clone https://github.com/NVIDIA/NeMo
!pip install -r NeMo/requirements/requirements_nlp.txt
!cd NeMo && ./reinstall.sh

# convert corpora to atis format
!git clone https://github.com/cartesinus/leyzer

for lang in ["en-US", "es-ES", "pl-PL"]:
    lang_under = lang.replace('-', '_')
    !mkdir -p data/baseline/"$lang"
    # create dictionary
    !./leyzer/scripts/convert-to-nemo.py --create_dictionary \
        ./leyzer/corpora/leyzer_test-"$lang_under"-0.1.0.tsv \
        ./leyzer/corpora/leyzer_train-"$lang_under"-0.1.0.tsv --output data/baseline/"$lang"/

    # create trainset in atis format
    !./leyzer/scripts/convert-to-nemo.py --input ./leyzer/corpora/leyzer_train-"$lang_under"-0.1.0.tsv \
        -n data/baseline/"$lang"/leyzer.dict.intent.csv \
        -t data/baseline/"$lang"/leyzer.dict.vocab.csv \
        -s data/baseline/"$lang"/leyzer.dict.slots.csv \
        --part train \
        --output data/baseline/"$lang"/

    # create testset in atis format
    !./leyzer/scripts/convert-to-nemo.py --input ./leyzer/corpora/leyzer_test-"$lang_under"-0.1.0.tsv \
        -n data/baseline/"$lang"/leyzer.dict.intent.csv \
        -t data/baseline/"$lang"/leyzer.dict.vocab.csv \
        -s data/baseline/"$lang"/leyzer.dict.slots.csv \
        --part test \
        --output data/baseline/"$lang"/

    # train baseline
    !cd NeMo && python examples/nlp/intent_detection_slot_tagging/joint_intent_slot_with_bert.py \
        --data_dir ../data/baseline/"$lang"/ \
        --work_dir ../data/baseline/"$lang"/model \
        --max_seq_length 21 \
        --num_epochs 50 \
        --optimizer_kind adam

