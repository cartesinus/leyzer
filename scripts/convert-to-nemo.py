#!/usr/bin/env python3
# encoding: utf-8

import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import pandas as pd


def create_dict(df, i, s):
    """Crate dictionary for all columns in ATIS format."""
    for intent in df['intent'].tolist():
        if intent not in i:
            i.extend([intent])

    for line in df['bio'].tolist():
        for slot in line.split(' '):
            slot = slot.capitalize() if slot == 'o' else slot
            slot_base = slot[2:] if slot.startswith('b-') or slot.startswith('i-') else slot
            if slot_base not in s:
                s.extend([slot_base])

    return i, s


def read_dict(filename):
    with open(filename) as f:
        lines = f.read().splitlines()

    return lines


def create_train(df, dictionary, capitalize=False):
    """Create file with each element replaced with dictionary index."""
    train_ = []
    for elem in df:
        line = ""
        for token in elem.split(' '):
            token = token.capitalize() if token == 'o' else token
            token = token[2:] if token.startswith('b-') or token.startswith('i-') else token
            if capitalize:
                line += str(dictionary.index(token.capitalize())) + " "
            else:
                line += str(dictionary.index(token)) + " "
        train_.append(line.strip())

    return train_


def create_utt_and_int(utterance, intent, intent_dict):
    """Create file with each element replaced with dictionary index."""
    train_ = []
    train_.append("sentence\tlabel")
    for utt, intent in zip(utterance, intent.tolist()):
        intent = intent[2:] if intent.startswith('B-') or intent.startswith('I-') else intent
        train_.append(str(utt)+"\t"+str(intent_dict.index(intent)))

    return train_


def save(data, filename):
    """Save each element of list to new line in file."""
    with open(filename, 'w') as f:
        for item in data:
            f.write("%s\n" % item)


def main(argv=None):  # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    try:
        # Setup argument parser
        parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)

        parser.add_argument("-c", "--create_dictionary", dest="create_dictionary",
                            action="store_true", help="create intent, slot and vocab dictionaries.")
        parser.add_argument('file', nargs='*')
        parser.add_argument("-i", "--input", dest="input", action="store",
                            help="input file (tsv with 4 columns: domain, intent, utterance, bio.")
        parser.add_argument("-n", "--intent_dict", dest="intent_dict", action="store",
                            help="intent dictionary files.")
        parser.add_argument("-s", "--slot_dict", dest="slot_dict", action="store",
                            help="slot dictionary files.")
        parser.add_argument("-o", "--output", dest="output_path", action="store",
                            help="output path where train files will be saved.")
        parser.add_argument("-p", "--part", dest="part", action="store",
                            help="name of dataset part (e.g. test, train).")

        # Process data
        args = parser.parse_args()
        if args.create_dictionary and args.output_path:
            print('Create dictionary files.')
            i, s = [], []

            for filename in args.file:
                df = pd.read_csv(filename, sep='\t', header=0)
                i, s = create_dict(df, i, s)

            save(i, args.output_path+'dict.intents.csv')
            save(s, args.output_path+'dict.slots.csv')

        if args.input and args.output_path:
            intent_dict = read_dict(args.intent_dict)
            slot_dict = read_dict(args.slot_dict)
            df = pd.read_csv(args.input, sep='\t', header=0)
            utt_intent_ = create_utt_and_int(df['utterance'], df['intent'], intent_dict)
            slot_ = create_train(df['bio'], slot_dict)
            save(utt_intent_, args.output_path+args.part+'.tsv')
            save(slot_, args.output_path+args.part+'_slots.tsv')

    except KeyboardInterrupt:
        # handle keyboard interrupt ###
        return 0

if __name__ == "__main__":
    sys.exit(main())
