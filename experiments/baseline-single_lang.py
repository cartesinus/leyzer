# -*- coding: utf-8 -*-
"""Replicate baseline models for en, es and pl.

This script, designed to be run on colab, will convert leyzer corpora to atis format and train
3 baseline models.

To convert this script to ipynb you can use https://pypi.org/project/ipynb-py-convert/.
"""

!pip install nemo-nlp
!git clone https://github.com/NVIDIA/NeMo
!pip install -r NeMo/requirements/requirements_nlp.txt
!cd NeMo && git reset --hard ac4a765 && ./reinstall.sh
!git clone https://github.com/cartesinus/leyzer

# train baseline
for lang in ["en-US", "es-ES", "pl-PL"]:
    !mkdir -p /content/data/baseline/"$lang"/
    !./leyzer/scripts/convert-to-atis.py --create_dictionary \
        /content/leyzer/corpora/0.1.0/leyzer-dev-"$lang"-0.1.0.tsv \
        /content/leyzer/corpora/0.1.0/leyzer-test-"$lang"-0.1.0.tsv \
        /content/leyzer/corpora/0.1.0/leyzer-train-"$lang"-0.1.0.tsv \
        --output /content/data/baseline/"$lang"/

    for mode in ["train", "test", "dev"]:
    !./leyzer/scripts/convert-to-atis.py --input \
        /content/leyzer/corpora/0.1.0/leyzer-"$mode"-"$lang"-0.1.0.tsv \
        --output /content/data/baseline/"$lang"/ \
        -n /content/data/baseline/"$lang"/atis.dict.intent.csv \
        -t /content/data/baseline/"$lang"/atis.dict.vocab.csv \
        -s /content/data/baseline/en-US/atis.dict.slots.csv --part "$mode"

    !mkdir -p data/baseline/"$lang"/nemo/
    !cd NeMo/examples/nlp/intent_detection_slot_tagging/data/ && python import_datasets.py \
        --dataset_name atis \
        --source_data_dir /content/data/baseline/"$lang"/ \
        --target_data_dir /content/data/baseline/"$lang"/nemo/

    !cd NeMo && python examples/nlp/intent_detection_slot_tagging/joint_intent_slot_with_bert.py \
        --data_dir ../data/baseline/"$lang"/nemo/ \
        --work_dir ../data/baseline/"$lang"/nemo/model \
        --max_seq_length 21 \
        --num_epochs 50 \
        --optimizer_kind adam

