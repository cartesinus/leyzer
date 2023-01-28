# -*- coding: utf-8 -*-
"""
This script split leyzer (both in pattern format and fully expanded) into train and test.
Spliting criteria are:
1) For test select ceil of 20% of total available patterns. minimum 1 pattern is selected
   even if there are 2 patterns in total,
2) For test select first patterns from all available patterns.

Usage:
        ``python split_dataset.py -f ../corpus/0.2.0/en-US/patterns.tsv --test 0.2.0_test.tsv --train 0.2.0_train.tsv``
"""

import argparse
import csv
import os
import math


def save_file(dataset, filename):
    """ Writte csv to file. """
    with open(filename, 'w', newline='') as file:
        corpus_out = csv.writer(file, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        for t in dataset:
            corpus_out.writerow(t)

    return True


if __name__ == '__main__':
    argparse = argparse.ArgumentParser(description='Split corpus to train and test subparts.')
    argparse.add_argument('-f', '--filename',
                        help='Input file that will be splitted into train and test.')
    argparse.add_argument('-t', '--train',
                        help='Output file for train part of corpus.')
    argparse.add_argument('-e', '--test',
                        help='Output file for test part of corpus.')
    argparse.add_argument('--stats', dest='stats', action='store_true')
    argparse.add_argument('--no-stats', dest='stats', action='store_false')
    argparse.set_defaults(stats=True)

    args = argparse.parse_args()

    if args.filename:
        corpus = {}
        test_corpus = []
        train_corpus = []
        with open(args.filename, newline='') as dataset:
            reader = csv.reader(dataset, delimiter="\t")

            for domain, intent, level, pattern, utterance in reader:
                uniq_pattern_idx = "#".join([domain, intent, level, pattern])
                if uniq_pattern_idx in corpus:
                    corpus[uniq_pattern_idx].append(utterance)
                else:
                    corpus[uniq_pattern_idx] = [utterance]

            if args.stats:
                print("Domain\tIntent\tLevel\tVerbPattern\tTotalPatterns\tTrainPatterns\tTestPatterns")

            for pattern in corpus:
                total_patterns = len(corpus[pattern])
                test_size = math.ceil(total_patterns * 0.2)
                train_size = total_patterns - test_size

                test = corpus[pattern][:test_size]
                train = corpus[pattern][-train_size:]

                for t in test:
                    test_corpus.append(pattern.split("#") + [t])
                for t in train:
                    train_corpus.append(pattern.split("#") + [t])

                if args.stats:
                    print("\t".join(pattern.split("#") + [str(total_patterns), str(train_size), str(test_size)]))

        save_file(test_corpus, args.test)
        save_file(train_corpus, args.train)
    else:
        print("No file was provided.")
