#!/bin/bash
# scripts/combine_corpus.sh
# Combine individual corpus files into a single file

set -e

LANGUAGE=$1
VERSION=$2
CORPUS_DIR=$3
OUTPUT_FILE=$4

if [ -z "$LANGUAGE" ] || [ -z "$VERSION" ] || [ -z "$CORPUS_DIR" ] || [ -z "$OUTPUT_FILE" ]; then
    echo "Usage: $0 <language> <version> <corpus_dir> <output_file>"
    echo "Example: $0 csb-PL 0.3.0 corpora/0.3.0 corpora/0.3.0/combined.tsv"
    exit 1
fi

echo "Combining corpus files for $LANGUAGE version $VERSION"
echo "Source directory: $CORPUS_DIR"
echo "Output file: $OUTPUT_FILE"

# Create output directory if it doesn't exist
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Create header
echo -e "domain\tintent\tlevel\tpattern\tutterance\tbio" > "$OUTPUT_FILE"

# Track files processed
files_processed=0
total_lines=0

# Find and combine all corpus files for this language/version
for corpus_file in "$CORPUS_DIR"/leyzer-"$LANGUAGE"-*-"$VERSION".tsv; do
    if [ -f "$corpus_file" ] && [[ "$corpus_file" != *"combined"* ]]; then
        echo "Processing: $(basename "$corpus_file")"

        # Check if file has content beyond header
        line_count=$(wc -l < "$corpus_file")
        if [ "$line_count" -gt 1 ]; then
            # Skip header (first line) and append content
            tail -n +2 "$corpus_file" >> "$OUTPUT_FILE"
            files_processed=$((files_processed + 1))
            content_lines=$((line_count - 1))
            total_lines=$((total_lines + content_lines))
            echo "  Added $content_lines lines"
        else
            echo "  Skipping empty file"
        fi
    fi
done

if [ $files_processed -eq 0 ]; then
    echo "ERROR: No corpus files found matching pattern: $CORPUS_DIR/leyzer-$LANGUAGE-*-$VERSION.tsv"
    exit 1
fi

echo "Successfully combined $files_processed files"
echo "Total lines (excluding header): $total_lines"
echo "Combined file: $OUTPUT_FILE"

# Verify the output file
if [ -f "$OUTPUT_FILE" ]; then
    final_line_count=$(wc -l < "$OUTPUT_FILE")
    expected_lines=$((total_lines + 1))  # +1 for header

    if [ "$final_line_count" -eq "$expected_lines" ]; then
        echo "✓ Verification passed: $final_line_count lines in output file"
    else
        echo "✗ Verification failed: Expected $expected_lines lines, got $final_line_count"
        exit 1
    fi
else
    echo "ERROR: Output file was not created"
    exit 1
fi
