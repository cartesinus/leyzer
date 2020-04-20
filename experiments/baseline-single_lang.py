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

!./leyzer/scripts/convert-to-nemo.sh leyzer ./
# convert corpora to atis format
!git clone https://github.com/cartesinus/leyzer

# train baseline
for lang in ["en-US", "es-ES", "pl-PL"]:
    !cd NeMo && python examples/nlp/intent_detection_slot_tagging/joint_intent_slot_with_bert.py \
        --data_dir ../data/baseline/"$lang"/ \
        --work_dir ../data/baseline/"$lang"/model \
        --max_seq_length 21 \
        --num_epochs 50 \
        --optimizer_kind adam

