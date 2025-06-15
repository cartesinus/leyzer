#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script deterministically generates strings from a JSGF Grammar, whether there are weights
defined in rules or not. It is based on DeterministicGenerator.py.

Usage:
    ``python generate_patterns.py -f ../grammars/en-US/News.gram``
    ``python generate_patterns.py -c ../experiments/massive_mapping/leyzer-expansion.conf``
    ``python generate_patterns.py -c config.conf --split-domains --output-dir patterns/``
"""

from JSGFToolsLeyzer import parser
from JSGFToolsLeyzer import processRHS
import argparse
import json
import os
from git import Repo


if __name__ == "__main__":
    argparse = argparse.ArgumentParser(description="Expand JSGF grammars.")
    argparse.add_argument("-f", "--filename", help="grammar file to be expanded.")
    argparse.add_argument(
        "-c",
        "--config",
        help="config file that defines which files and how to expand them.",
    )
    argparse.add_argument(
        "--split-domains",
        action="store_true",
        help="when using config, create separate files for each domain",
    )
    argparse.add_argument(
        "--output-dir",
        help="output directory for domain files (overrides config expand_output_dir)",
    )
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

        # if repo ref is provided then git reset
        if "lezer_repo_ref" in data:
            repo = Repo.init(data["project_dir"], bare=True)
            repo.head.reset(data["lezer_repo_ref"])

        # Determine output directory
        output_dir = None
        if args.split_domains:
            if args.output_dir:
                output_dir = args.output_dir
            elif "expand_output_dir" in data:
                output_dir = data["expand_output_dir"]
            else:
                output_dir = "patterns/"

            # Create output directory
            os.makedirs(output_dir, exist_ok=True)

        # Group expansions by domain if split-domains is enabled
        domain_patterns = {}

        # generate grammars from config list
        for conf_gram in data["expand"]:
            gramFile = conf_gram["domain"]
            fileName = (
                os.path.join(data["project_dir"], data["grammar_dir"], gramFile.lower())
                + ".gram"
            )
            fileStream = open(fileName)
            gramCache = {}
            if gramFile not in gramCache:
                gramCache[gramFile] = parser.getGrammarObject(fileStream)
            grammar = gramCache[gramFile]
            for rule in grammar.publicRules:
                expansions = processRHS(rule.rhs, grammar)
                for expansion in expansions:
                    if conf_gram["intent"] in expansion:
                        for x in range(int(conf_gram["expand-rate"])):
                            if args.split_domains:
                                # Collect patterns by domain
                                domain = conf_gram["domain"]
                                if domain not in domain_patterns:
                                    domain_patterns[domain] = []
                                domain_patterns[domain].append(expansion)
                            else:
                                # Print to stdout as before (default behavior)
                                print(expansion)

        # Write domain files if split-domains is enabled
        if args.split_domains and domain_patterns:
            for domain, patterns in domain_patterns.items():
                output_file = os.path.join(output_dir, f"{domain.lower()}.tsv")
                with open(output_file, "w") as f:
                    for pattern in patterns:
                        f.write(pattern + "\n")
                print(f"Created {output_file} with {len(patterns)} patterns")

    else:
        print("No file or config was provided.")
