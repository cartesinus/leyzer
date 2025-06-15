#!/bin/bash
# scripts/create_build_summary.sh
# Create a build summary markdown file for GitHub Actions

set -e

LANGUAGE=$1
VERSION=$2
COMMIT_SHA=$3
VALIDATION_PASSED=$4
SAMPLE_COUNT=$5
OUTPUT_DIR=$6

if [ -z "$LANGUAGE" ] || [ -z "$VERSION" ] || [ -z "$COMMIT_SHA" ] || [ -z "$VALIDATION_PASSED" ] || [ -z "$SAMPLE_COUNT" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Usage: $0 <language> <version> <commit_sha> <validation_passed> <sample_count> <output_dir>"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

SUMMARY_FILE="$OUTPUT_DIR/build_summary.md"
VALIDATION_ICON="❌"
if [ "$VALIDATION_PASSED" = "true" ]; then
    VALIDATION_ICON="✅"
fi

cat > "$SUMMARY_FILE" << EOF
# Leyzer Corpus Build Summary

- **Language**: $LANGUAGE
- **Version**: $VERSION
- **Build Date**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
- **Commit**: $COMMIT_SHA
- **Validation**: $VALIDATION_ICON $([ "$VALIDATION_PASSED" = "true" ] && echo "Passed" || echo "Failed")
- **Total Samples**: $SAMPLE_COUNT

## Files Generated

\`\`\`
$(ls -la "$OUTPUT_DIR" 2>/dev/null || echo "No files in output directory yet")
\`\`\`

## Validation Report

\`\`\`
$(cat "$OUTPUT_DIR/../validation/validation_report.txt" 2>/dev/null || echo "No validation report available")
\`\`\`

## Statistics

\`\`\`json
$(cat "$OUTPUT_DIR/../validation/corpus_stats.json" 2>/dev/null || echo "No statistics available")
\`\`\`

---
*Generated automatically by Leyzer Corpus Pipeline*
EOF

echo "Build summary created: $SUMMARY_FILE"
