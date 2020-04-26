# -*- coding: utf-8 -*-
"""Replicate train-on-target models for en, es and pl.

This script, designed to be run on colab, will convert leyzer corpora to atis format and train
3 train-on-target models.

To convert this script to ipynb you can use https://pypi.org/project/ipynb-py-convert/.
"""
corpus_version = "0.1.0"

!pip install nemo-nlp
!git clone https://github.com/NVIDIA/NeMo
!pip install -r NeMo/requirements/requirements_nlp.txt
!cd NeMo && git reset --hard ac4a765 && ./reinstall.sh
!git clone https://github.com/cartesinus/leyzer

# train train-on-target
for lang in ["es-ES", "pl-PL"]:
    lang_short = lang.split('-')[0]
    !mkdir -p /content/data/train-on-target/"$lang"/
    !./leyzer/scripts/convert-to-atis.py --create_dictionary \
        /content/leyzer/corpora/"$corpus_version"/leyzer-dev-"$lang"-"$corpus_version".tsv \
        /content/leyzer/corpora/"$corpus_version"/leyzer-test-"$lang"-"$corpus_version".tsv \
        /content/leyzer/corpora/"$corpus_version"/train-on-target/leyzer-train-en2"$lang_short"-"$corpus_version".tsv \
        --output /content/data/train-on-target/"$lang"/

    for mode in ["test", "dev"]:
        !./leyzer/scripts/convert-to-atis.py --input \
            /content/leyzer/corpora/"$corpus_version"/leyzer-"$mode"-"$lang"-"$corpus_version".tsv \
            --output /content/data/train-on-target/"$lang"/ \
            -n /content/data/train-on-target/"$lang"/atis.dict.intent.csv \
            -t /content/data/train-on-target/"$lang"/atis.dict.vocab.csv \
            -s /content/data/train-on-target/"$lang"/atis.dict.slots.csv --part "$mode"

    !./leyzer/scripts/convert-to-atis.py --input \
        /content/leyzer/corpora/"$corpus_version"/train-on-target/leyzer-train-en2"$lang_short"-"$corpus_version".tsv \
        --output /content/data/train-on-target/"$lang"/ \
        -n /content/data/train-on-target/"$lang"/atis.dict.intent.csv \
        -t /content/data/train-on-target/"$lang"/atis.dict.vocab.csv \
        -s /content/data/train-on-target/"$lang"/atis.dict.slots.csv --part train

    !mkdir -p data/train-on-target/"$lang"/nemo/
    !cd NeMo/examples/nlp/intent_detection_slot_tagging/data/ && python import_datasets.py \
        --dataset_name atis \
        --source_data_dir /content/data/train-on-target/"$lang"/ \
        --target_data_dir /content/data/train-on-target/"$lang"/nemo/

    !cd NeMo && python examples/nlp/intent_detection_slot_tagging/joint_intent_slot_with_bert.py \
        --data_dir ../data/train-on-target/"$lang"/nemo/ \
        --work_dir ../data/train-on-target/"$lang"/nemo/model \
        --max_seq_length 35 \
        --num_epochs 100 \
        --optimizer_kind adam \
        --pretrained_model_name bert-base-multilingual-uncased

    !cd NeMo && python examples/nlp/intent_detection_slot_tagging/joint_intent_slot_infer.py \
        --data_dir ../data/train-on-target/"$lang"/nemo/ \
        --checkpoint_dir ../data/train-on-target/"$lang"/nemo/model/*/checkpoints/ \
        --pretrained_model_name bert-base-multilingual-uncased \
        --eval_file_prefix test
