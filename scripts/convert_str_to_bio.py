#!/usr/bin/env python3
# encoding: utf-8

import sys

DATE_SLOTS = ['date_na', 'date_w0', 'date_we']
sentences = sys.stdin.readlines()
for sentence in sentences:
    bio = ""
    in_slot = False
    slot = ""
    raw_sentence = ""
    for word in sentence.split(' '):
        word = word.strip()
        if word.startswith('{') and word.endswith('}'):
            in_slot = False
            slot = word.split(':')[0][1:].lower()
            if slot in DATE_SLOTS:
                slot = 'date'
            bio += "b-" + slot + " "
            raw_sentence += word.split(':')[1][:-1] + " "
        elif word.startswith('{'):
            in_slot = True
            slot = word.split(':')[0][1:].lower()
            if slot in DATE_SLOTS:
                slot = 'date'
            bio += "b-" + slot + " "
            raw_sentence += word.split(':')[1] + " "
        elif word.endswith('}'):
            in_slot = False
            bio += "i-" + slot.lower() + " "
            raw_sentence += word[:-1] + " "
        elif in_slot:
            bio += "i-" + slot.lower() + " "
            raw_sentence += word + " "
        else:
            bio += "o "
            raw_sentence += word + " "

    print(raw_sentence.strip(), "\t", bio.strip())
