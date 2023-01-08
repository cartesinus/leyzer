# -*- coding: utf-8 -*-
"""
This script test grammar coverage agains templates.

Usage:
        ``python test_coverage.py -f /home/cartesinus/projects/leyzer/grammars/en-US/ \
                -t /home/cartesinus/projects/leyzer/grammars/template/``
"""

import sys
from JSGFToolsLeyzer import parser
import argparse
import json
import git
import os
from git import Repo


if __name__ == '__main__':
    argparse = argparse.ArgumentParser(description='Expand JSGF grammars.')
    argparse.add_argument('-f', '--test_path', help='Path with tested grammars.')
    argparse.add_argument('-t', '--template_path', help='Path with grammars templates.')
    args = argparse.parse_args()
    sys_exit_code = 0

    for template in os.listdir(args.template_path):
        print("Testing " + template + " grammar.", end=' ')
        templateFile = open(args.template_path + template)

        if template in os.listdir(args.test_path):
            testFile = open(args.test_path + template)
            test_grammar = parser.getGrammarObject(testFile)
            template_grammar = parser.getGrammarObject(templateFile)

            if str(template_grammar.publicRules) == str(test_grammar.publicRules):
                try:
                    for rule in template_grammar.publicRules[0].rhs[1].disjuncts:
                        for intentLevel in template_grammar.getRule(str(rule[1]))[0].disjuncts:
                            test_grammar.getRule(str(intentLevel))
                except ValueError:
                    print("ERROR:\nMissing rule implementation.")
                    print('===========================================')
                    print("Rule: " + str(intentLevel) + " was not implemented in " + template + " grammar.")
                    print('===========================================')
                    sys_exit_code = 1

                print("OK")
            else:
                print("ERROR:\nPublic rules are different than in template.")
                print('===========================================')
                print("template:\n" + str(template_grammar.publicRules))
                print("grammar:\n" + str(test_grammar.publicRules))
                print('===========================================')
                sys_exit_code = 1
        else:
            print('No ' + template + ' grammar in ' + args.test_path)

    sys.exit(sys_exit_code)
