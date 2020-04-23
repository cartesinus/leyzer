# -*- coding: utf-8 -*-
"""Replicate zeroshot models for en, es and pl.

This script, designed to be run on colab, will convert leyzer corpora to atis format and train
3 zeroshot models.

To convert this script to ipynb you can use https://pypi.org/project/ipynb-py-convert/.
"""
corpus_version = "0.1.0"

!pip install nemo-nlp
!git clone https://github.com/NVIDIA/NeMo
!pip install -r NeMo/requirements/requirements_nlp.txt
!cd NeMo && git reset --hard ac4a765 && ./reinstall.sh
!git clone https://github.com/cartesinus/leyzer

# train zeroshot
!mkdir -p /content/data/zeroshot/

# we need same dictionary for all languages
!cat /content/leyzer/corpora/"$corpus_version"/leyzer-*-*-*-"$corpus_version".tsv \
    > /content/data/zeroshot/all-data.tsv
!sed -i '1b;/^domain\tintent/d' /content/data/zeroshot/all-data.tsv

!./leyzer/scripts/convert-to-atis.py --create_dictionary \
    /content/data/zeroshot/all-data.tsv \
    --output /content/data/zeroshot/

!mkdir -p /content/data/zeroshot/data/
for mode in ["train", "test", "dev"]:
    !./leyzer/scripts/convert-to-atis.py --input \
        /content/leyzer/corpora/"$corpus_version"/leyzer-"$mode"-en-US-"$corpus_version".tsv \
        --output /content/data/zeroshot/ \
        -n /content/data/zeroshot/atis.dict.intent.csv \
        -t /content/data/zeroshot/atis.dict.vocab.csv \
        -s /content/data/zeroshot/atis.dict.slots.csv --part "$mode"

!mkdir -p data/zeroshot/nemo/
!cd NeMo/examples/nlp/intent_detection_slot_tagging/data/ && python import_datasets.py \
    --dataset_name atis \
    --source_data_dir /content/data/zeroshot/ \
    --target_data_dir /content/data/zeroshot/nemo/

!cd NeMo && python examples/nlp/intent_detection_slot_tagging/joint_intent_slot_with_bert.py \
    --data_dir ../data/zeroshot/nemo/ \
    --work_dir ../data/zeroshot/nemo/model \
    --max_seq_length 40 \
    --num_epochs 100 \
    --optimizer_kind adam \
    --pretrained_model_name bert-base-multilingual-uncased

for lang in ["es-ES", "pl-PL"]:
    !mkdir -p /content/data/zeroshot/"$lang"/
    !cp /content/data/zeroshot/atis.dict.intent.csv \
        /content/data/zeroshot/atis.dict.vocab.csv \
        /content/data/zeroshot/atis.dict.slots.csv \
        /content/data/zeroshot/"$lang"/

    for mode in ["train", "test", "dev"]:
        !./leyzer/scripts/convert-to-atis.py --input \
            /content/leyzer/corpora/"$corpus_version"/leyzer-"$mode"-"$lang"-"$corpus_version".tsv \
            --output /content/data/zeroshot/"$lang"/ \
            -n /content/data/zeroshot/atis.dict.intent.csv \
            -t /content/data/zeroshot/atis.dict.vocab.csv \
            -s /content/data/zeroshot/atis.dict.slots.csv --part "$mode"

    !mkdir -p data/zeroshot/"$lang"/nemo/
    !cd NeMo/examples/nlp/intent_detection_slot_tagging/data/ && python import_datasets.py \
        --dataset_name atis \
        --source_data_dir /content/data/zeroshot/"$lang"/ \
        --target_data_dir /content/data/zeroshot/"$lang"/nemo/

    !cd NeMo && python examples/nlp/intent_detection_slot_tagging/joint_intent_slot_infer.py \
        --data_dir ../data/zeroshot/"$lang"/nemo/ \
        --checkpoint_dir ../data/zeroshot/nemo/model/*/checkpoints/ \
        --pretrained_model_name bert-base-multilingual-uncased \
        --eval_file_prefix test
