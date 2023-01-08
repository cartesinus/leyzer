# -*- coding: utf-8 -*-
"""
This script deterministically generates strings from a JSGF Grammar, whether there are \
weights defined in rules or not. It is based on DeterministicGenerator.py.

Usage:
        ``python generate_patterns.py -f ../grammars/en-US/News.gram``
        ``python generate_patterns.py -c ../experiments/massive_mapping/leyzer-expansion.conf``
"""

from JSGFToolsLeyzer import parser
from JSGFToolsLeyzer import processRHS
import argparse
import json
import os
from git import Repo


if __name__ == '__main__':
    argparse = argparse.ArgumentParser(description='Expand JSGF grammars.')
    argparse.add_argument('-f', '--filename',
                        help='grammar file to be expanded.')
    argparse.add_argument('-c', '--config',
                        help='config file that defines which files and how to expand them.')
    args = argparse.parse_args()

    if args.filename:
        fileStream = open(args.filename)
        grammar = parser.getGrammarObject(fileStream)
        for rule in grammar.publicRules:
            expansions = processRHS(rule.rhs, grammar)
            for expansion in expansions:
                print(expansion)
    elif args.config:
        with open(args.config) as f:
            data = json.load(f)

        #if repo ref is provided then git reset
        if 'lezer_repo_ref' in data:
            repo = Repo.init(data['project_dir'], bare=True)
            repo.head.reset(data['lezer_repo_ref'])

        #generate grammars from config list
        for conf_gram in data['expand']:
            gramFile = conf_gram['domain']
            fileName = os.path.join(data['project_dir'], data['grammar_dir'], gramFile.lower()) + '.gram'
            fileStream = open(fileName)
            gramCache = {}
            if gramFile not in gramCache:
                gramCache[gramFile] = parser.getGrammarObject(fileStream)
            grammar = gramCache[gramFile]
            for rule in grammar.publicRules:
                expansions = processRHS(rule.rhs, grammar)
                for expansion in expansions:
                    if conf_gram['intent'] in expansion:
                        print(expansion)
    else:
        print("No file or config was provided.")
