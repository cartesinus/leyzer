#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script validates the corpus generation for a language by checking:
1. All expected intents are present
2. Column count is correct
3. No missing domain/intent combinations
4. Basic data quality checks

Usage:
    python validate_corpus.py -l csb-PL -c corpora/0.2.0/ -r leyzer-0.3.0-csb_PL-expansion.conf
"""

import argparse
import json
import pandas as pd
import os
from collections import defaultdict, Counter
import sys


def load_reference_config(config_path):
    """Load the reference configuration to get expected intents."""
    with open(config_path, 'r') as f:
        config = json.load(f)

    expected_intents = defaultdict(set)
    for item in config['expand']:
        domain = item['domain']
        intent = item['intent']
        expected_intents[domain].add(intent)

    return expected_intents


def validate_corpus_file(file_path, expected_columns=None):
    """Validate a single corpus file."""
    errors = []
    warnings = []

    if not os.path.exists(file_path):
        errors.append(f"File does not exist: {file_path}")
        return errors, warnings, None

    try:
        df = pd.read_csv(file_path, sep='\t')
    except Exception as e:
        errors.append(f"Failed to read {file_path}: {str(e)}")
        return errors, warnings, None

    # Check if file is empty
    if len(df) == 0:
        errors.append(f"File is empty: {file_path}")
        return errors, warnings, None

    # Check column count
    if expected_columns and len(df.columns) != expected_columns:
        errors.append(f"Expected {expected_columns} columns, found {len(df.columns)} in {file_path}")

    # Check for required columns
    required_columns = ['domain', 'intent']
    for col in required_columns:
        if col not in df.columns:
            errors.append(f"Missing required column '{col}' in {file_path}")

    # Check for empty values in critical columns
    if 'domain' in df.columns and df['domain'].isnull().any():
        warnings.append(f"Found null values in 'domain' column in {file_path}")

    if 'intent' in df.columns and df['intent'].isnull().any():
        warnings.append(f"Found null values in 'intent' column in {file_path}")

    # Check for duplicates
    if 'utterance' in df.columns:
        duplicates = df['utterance'].duplicated().sum()
        if duplicates > 0:
            warnings.append(f"Found {duplicates} duplicate utterances in {file_path}")

    return errors, warnings, df


def validate_intent_coverage(df, expected_intents):
    """Validate that all expected intents are present."""
    errors = []
    warnings = []

    if df is None:
        return errors, warnings

    # Get actual intents grouped by domain
    actual_intents = defaultdict(set)
    if 'domain' in df.columns and 'intent' in df.columns:
        for _, row in df.iterrows():
            actual_intents[row['domain']].add(row['intent'])

    # Check coverage
    for domain, expected_intent_set in expected_intents.items():
        actual_intent_set = actual_intents.get(domain, set())

        missing_intents = expected_intent_set - actual_intent_set
        extra_intents = actual_intent_set - expected_intent_set

        if missing_intents:
            errors.append(f"Domain '{domain}' missing intents: {', '.join(missing_intents)}")

        if extra_intents:
            warnings.append(f"Domain '{domain}' has unexpected intents: {', '.join(extra_intents)}")

    return errors, warnings


def generate_statistics(df):
    """Generate basic statistics about the corpus."""
    if df is None:
        return {}

    stats = {}

    # Basic counts
    stats['total_samples'] = len(df)

    if 'domain' in df.columns:
        stats['domains'] = df['domain'].nunique()
        stats['domain_distribution'] = df['domain'].value_counts().to_dict()

    if 'intent' in df.columns:
        stats['intents'] = df['intent'].nunique()
        stats['intent_distribution'] = df['intent'].value_counts().to_dict()

    if 'utterance' in df.columns:
        # Average utterance length
        df['utterance_length'] = df['utterance'].str.len()
        stats['avg_utterance_length'] = df['utterance_length'].mean()
        stats['min_utterance_length'] = df['utterance_length'].min()
        stats['max_utterance_length'] = df['utterance_length'].max()

    # Domain-Intent combinations
    if 'domain' in df.columns and 'intent' in df.columns:
        domain_intent_counts = df.groupby(['domain', 'intent']).size().to_dict()
        stats['domain_intent_counts'] = domain_intent_counts

        # Find intents with very few examples
        low_sample_intents = {k: v for k, v in domain_intent_counts.items() if v < 3}
        if low_sample_intents:
            stats['low_sample_intents'] = low_sample_intents

    return stats


def main():
    parser = argparse.ArgumentParser(description='Validate corpus generation for a language')
    parser.add_argument('-l', '--language', required=True, help='Language code (e.g., cs-CZ)')
    parser.add_argument('-c', '--corpus_dir', required=True, help='Path to corpus directory')
    parser.add_argument('-r', '--reference_config', required=True, help='Path to reference configuration JSON')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--expected-columns', type=int, default=6,
                       help='Expected number of columns in corpus files (default: 6)')

    args = parser.parse_args()

    # Load expected intents from reference config
    try:
        expected_intents = load_reference_config(args.reference_config)
        print(f"Loaded expected intents for {len(expected_intents)} domains")
    except Exception as e:
        print(f"Error loading reference config: {e}")
        sys.exit(1)
