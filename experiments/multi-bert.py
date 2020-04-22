# -*- coding: utf-8 -*-
"""Replicate multilang models for en, es and pl.

This script, designed to be run on colab, will convert leyzer corpora to atis format and train
3 multilang models.

To convert this script to ipynb you can use https://pypi.org/project/ipynb-py-convert/.
"""

!pip install nemo-nlp
!git clone https://github.com/NVIDIA/NeMo
!pip install -r NeMo/requirements/requirements_nlp.txt
!cd NeMo && git reset --hard ac4a765 && ./reinstall.sh
!git clone https://github.com/cartesinus/leyzer

# train multilang
!mkdir -p /content/data/multilang/

!cat /content/leyzer/corpora/0.1.0/leyzer-*-*-*-0.1.0.tsv > /content/data/multilang/all-data.tsv
!sed -i '1b;/^domain\tintent/d' /content/data/multilang/all-data.tsv

!./leyzer/scripts/convert-to-atis.py --create_dictionary \
    /content/data/multilang/all-data.tsv \
    --output /content/data/multilang/

!mkdir -p /content/data/multilang/data/
for mode in ["train", "test", "dev"]:
    !cat /content/leyzer/corpora/0.1.0/leyzer-"$mode"-*-*-0.1.0.tsv | sed '1b;/^domain\tintent/d' \
        > /content/data/multilang/data/leyzer-"$mode"-all-0.1.0.tsv

    !./leyzer/scripts/convert-to-atis.py --input \
        /content/data/multilang/data/leyzer-"$mode"-all-0.1.0.tsv \
        --output /content/data/multilang/ \
        -n /content/data/multilang/atis.dict.intent.csv \
        -t /content/data/multilang/atis.dict.vocab.csv \
        -s /content/data/multilang/atis.dict.slots.csv --part "$mode"

!mkdir -p data/multilang/nemo/
!cd NeMo/examples/nlp/intent_detection_slot_tagging/data/ && python import_datasets.py \
    --dataset_name atis \
    --source_data_dir /content/data/multilang/ \
    --target_data_dir /content/data/multilang/nemo/

!cd NeMo && python examples/nlp/intent_detection_slot_tagging/joint_intent_slot_with_bert.py \
    --data_dir ../data/multilang/nemo/ \
    --work_dir ../data/multilang/nemo/model \
    --max_seq_length 40 \
    --num_epochs 100 \
    --optimizer_kind adam \
    --pretrained_model_name bert-base-multilingual-uncased

for lang in ["en-US", "es-ES", "pl-PL"]:
    !mkdir -p /content/data/multilang/"$lang"/

    !./leyzer/scripts/convert-to-atis.py --input \
        /content/leyzer/corpora/0.1.0/leyzer-test-"$lang"-0.1.0.tsv \
        --output /content/data/multilang/"$lang"/ \
        -n /content/data/multilang/atis.dict.intent.csv \
        -t /content/data/multilang/atis.dict.vocab.csv \
        -s /content/data/multilang/atis.dict.slots.csv --part test

    !mkdir -p data/multilang/"$lang"/nemo/
    !cd NeMo/examples/nlp/intent_detection_slot_tagging/data/ && python import_datasets.py \
        --dataset_name atis \
        --source_data_dir /content/data/multilang/"$lang"/ \
        --target_data_dir /content/data/multilang/"$lang"/nemo/

    !cd NeMo && python examples/nlp/intent_detection_slot_tagging/joint_intent_slot_infer.py \
        --data_dir ../data/multilang/"$lang"/nemo/ \
        --checkpoint_dir ../data/multilang/"$lang"/nemo/model/*/checkpoints/ \
        --pretrained_model_name bert-base-multilingual-uncased \
        --eval_file_prefix test
