#!/usr/bin/env python3
# encoding: utf-8

import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import pandas as pd


def create_dict(df, i, t, s):
    """Crate dictionary for all columns in ATIS format."""
    for intent in df['intent'].tolist():
        if intent not in i:
            i.extend([intent])

    for line in df['bio'].tolist():
        for slot in line.split(' '):
            if slot.capitalize() not in s:
                s.extend([slot.capitalize()])

    for line in df['utterance'].tolist():
        for token in line.split(' '):
            if token not in t:
                t.extend([token])

    return i, t, s


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
            if capitalize:
                line += str(dictionary.index(token.capitalize())) + " "
            else:
                line += str(dictionary.index(token)) + " "
        train_.append(line.strip())

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
        parser.add_argument("-t", "--vocab_dict", dest="vocab_dict", action="store",
                            help="vocab dictionary files.")
        parser.add_argument("-o", "--output", dest="output_path", action="store",
                            help="output path where train files will be saved.")
        parser.add_argument("-p", "--part", dest="part", action="store",
                            help="name of dataset part (e.g. test, train).")

        # Process data
        args = parser.parse_args()
        if args.create_dictionary and args.output_path:
            print('Create dictionary files.')
            i, t, s = [], [], []

            for filename in args.file:
                df = pd.read_csv(filename, sep='\t', header=0)
                i, t, s = create_dict(df, i, t, s)

            save(i, args.output_path+'atis.dict.intent.csv')
            save(t, args.output_path+'atis.dict.vocab.csv')
            save(s, args.output_path+'atis.dict.slots.csv')

        if args.input and args.output_path:
            intent_dict = read_dict(args.intent_dict)
            slot_dict = read_dict(args.slot_dict)
            vocab_dict = read_dict(args.vocab_dict)
            df = pd.read_csv(args.input, sep='\t', header=0)
            intent_ = create_train(df['intent'], intent_dict)
            query_ = create_train(df['utterance'], vocab_dict)
            slot_ = create_train(df['bio'], slot_dict, True)
            save(intent_, args.output_path+'atis.'+args.part+'.intent.csv')
            save(query_, args.output_path+'atis.'+args.part+'.query.csv')
            save(slot_, args.output_path+'atis.'+args.part+'.slots.csv')

    except KeyboardInterrupt:
        # handle keyboard interrupt ###
        return 0

if __name__ == "__main__":
    sys.exit(main())
