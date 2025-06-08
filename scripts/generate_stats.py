#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate corpus statistics for GitHub Actions workflow.

Usage:
    python scripts/generate_stats.py <corpus_file> <output_dir>
"""

import sys
import os
import pandas as pd
import json
from pathlib import Path


def generate_statistics(corpus_file, output_dir):
    """Generate comprehensive statistics for the corpus."""

    if not os.path.exists(corpus_file):
        print(f"Error: Corpus file not found: {corpus_file}")
        return 0

    try:
        df = pd.read_csv(corpus_file, sep='\t')

        # Basic statistics
        stats = {
            'total_samples': len(df),
            'file_path': corpus_file,
            'generated_at': pd.Timestamp.now().isoformat()
        }

        # Domain statistics
        if 'domain' in df.columns:
            stats['domains'] = int(df['domain'].nunique())
            stats['domain_distribution'] = df['domain'].value_counts().to_dict()

        # Intent statistics
        if 'intent' in df.columns:
            stats['intents'] = int(df['intent'].nunique())
            stats['intent_distribution'] = df['intent'].value_counts().to_dict()

        # Utterance statistics
        if 'utterance' in df.columns:
            # Clean utterance data - convert to string and handle NaN values
            df['utterance'] = df['utterance'].astype(str)
            df = df[df['utterance'].notna() & (df['utterance'] != 'nan')]

            if len(df) > 0:
                df['utterance_length'] = df['utterance'].str.len()
                df['word_count'] = df['utterance'].str.split().str.len()

                stats['utterance_stats'] = {
                    'avg_length': float(df['utterance_length'].mean()),
                    'min_length': int(df['utterance_length'].min()),
                    'max_length': int(df['utterance_length'].max()),
                    'avg_words': float(df['word_count'].mean()),
                    'min_words': int(df['word_count'].min()),
                    'max_words': int(df['word_count'].max())
                }
            else:
                stats['utterance_stats'] = {
                    'avg_length': 0.0,
                    'min_length': 0,
                    'max_length': 0,
                    'avg_words': 0.0,
                    'min_words': 0,
                    'max_words': 0
                }

        # BIO tag statistics
        if 'bio' in df.columns:
            entity_count = 0
            slot_types = set()

            for bio_seq in df['bio'].dropna():
                bio_str = str(bio_seq).strip()
                if bio_str and bio_str != 'nan':
                    for tag in bio_str.split():
                        tag = tag.strip()
                        if tag.startswith('B-'):
                            entity_count += 1
                            slot_types.add(tag[2:])

            stats['slot_stats'] = {
                'total_entities': entity_count,
                'unique_slot_types': len(slot_types),
                'slot_types': sorted(list(slot_types))
            }

        # Domain-Intent combinations
        if 'domain' in df.columns and 'intent' in df.columns:
            domain_intent_counts = df.groupby(['domain', 'intent']).size()
            stats['domain_intent_pairs'] = len(domain_intent_counts)

            # Find low-sample intents
            low_sample_threshold = 3
            low_sample_intents = domain_intent_counts[domain_intent_counts < low_sample_threshold]
            if len(low_sample_intents) > 0:
                stats['low_sample_intents'] = {
                    f"{idx[0]}.{idx[1]}": int(count)
                    for idx, count in low_sample_intents.items()
                }
                print(f"Warning: {len(low_sample_intents)} domain-intent pairs have < {low_sample_threshold} samples")

        # Save statistics
        os.makedirs(output_dir, exist_ok=True)
        stats_file = os.path.join(output_dir, 'corpus_stats.json')

        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        # Create summary file for GitHub
        summary_file = os.path.join(output_dir, 'build_summary.txt')
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Total samples: {stats['total_samples']}\n")
            f.write(f"Domains: {stats.get('domains', 0)}\n")
            f.write(f"Intents: {stats.get('intents', 0)}\n")
            if 'utterance_stats' in stats:
                f.write(f"Avg utterance length: {stats['utterance_stats']['avg_length']:.1f} chars\n")
            if 'slot_stats' in stats:
                f.write(f"Total entities: {stats['slot_stats']['total_entities']}\n")

        return stats['total_samples']

    except Exception as e:
        # Write error to stderr to avoid GitHub Actions parsing issues
        sys.stderr.write(f"Error generating statistics: {e}\n")
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 0


def main():
    if len(sys.argv) != 3:
        sys.stderr.write("Usage: python scripts/generate_stats.py <corpus_file> <output_dir>\n")
        sys.exit(1)

    corpus_file = sys.argv[1]
    output_dir = sys.argv[2]

    sample_count = generate_statistics(corpus_file, output_dir)

    # Only output the sample count to stdout for capture
    print(sample_count)

    return 0 if sample_count > 0 else 1


if __name__ == '__main__':
    sys.exit(main())
