#!/bin/bash -e

LANG=$1
INPUT_FILE=$2
OUTPUT_FILE=$3
ADD_BIO=${4:-"false"}
REPEAT=${5:-"true"}

if [ -z "$LANG" ] || [ -z "$INPUT_FILE" ] || [ -z "$OUTPUT_FILE" ]; then
   echo "Usage: $0 <language> <input_file> <output_file> [add_bio] [repeat]"
   echo "Example: $0 csb-PL patterns/csb-PL/airconditioner.tsv output.tsv true true"
   exit 1
fi

# Get the script directory for proper path resolution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Set paths relative to project root
SLOTS_DIR="$PROJECT_ROOT/slots/$LANG"
CONVERT_SCRIPT="$SCRIPT_DIR/convert_str_to_bio.py"

echo "Using slots directory: $SLOTS_DIR"
echo "Convert script: $CONVERT_SCRIPT"

# Check if slots directory exists
if [ ! -d "$SLOTS_DIR" ]; then
   echo "Warning: Slots directory does not exist: $SLOTS_DIR"
   echo "Creating empty directory and continuing..."
   mkdir -p "$SLOTS_DIR"
fi

# Check if convert script exists when needed
if [ "$ADD_BIO" = "true" ] && [ ! -f "$CONVERT_SCRIPT" ]; then
   echo "Error: convert_str_to_bio.py not found at: $CONVERT_SCRIPT"
   exit 1
fi

# Create a working copy of the input file
WORK_FILE=$(mktemp)
cp "$INPUT_FILE" "$WORK_FILE"

function substitute_slots {
   local slot=$1
   local slot_file="$SLOTS_DIR/$slot"

   if [ ! -f "$slot_file" ]; then
       echo "Warning: Slot file not found: $slot_file"
       return 0
   fi

   while IFS= read -r text; do
       # Skip empty lines
       [ -z "$text" ] && continue

       if [ "$ADD_BIO" = "true" ]; then
           short_slot=$(echo "$slot" | sed 's/.*\.SLOT\.//g')
           # Use temporary file for sed operations
           sed "0,/$slot/ s|$slot|{$short_slot:$text}|" "$WORK_FILE" > "$WORK_FILE.tmp" && mv "$WORK_FILE.tmp" "$WORK_FILE"
       else
           sed "0,/$slot/ s|$slot|$text|" "$WORK_FILE" > "$WORK_FILE.tmp" && mv "$WORK_FILE.tmp" "$WORK_FILE"
       fi
   done < "$slot_file"
}

# Replace __ with tab
sed -i 's/__ /__\t/g' "$WORK_FILE"

# Process slots if directory exists and has files
if [ -d "$SLOTS_DIR" ] && [ "$(ls -A "$SLOTS_DIR" 2>/dev/null)" ]; then
   for slot_file in "$SLOTS_DIR"/*; do
       if [ -f "$slot_file" ]; then
           slot=$(basename "$slot_file")
           if grep -q "$slot" "$WORK_FILE"; then
               echo "Expanding with phrases from $slot"
               if [ "$REPEAT" = "true" ]; then
                   while grep -q "$slot" "$WORK_FILE"; do
                       substitute_slots "$slot"
                   done
               else
                   substitute_slots "$slot"
               fi
           fi
       fi
   done
else
   echo "No slot files found in $SLOTS_DIR, continuing without slot expansion"
fi

if [ "$ADD_BIO" = "true" ]; then
   echo "Saving patterns expanded with slot values to: $OUTPUT_FILE"
   # Create output directory if it doesn't exist
   mkdir -p "$(dirname "$OUTPUT_FILE")"

   # Process with BIO tagging
   if command -v python3 >/dev/null 2>&1; then
       cut -f1-4 "$WORK_FILE" > "$WORK_FILE.prefix"
       cut -f5 "$WORK_FILE" | python3 "$CONVERT_SCRIPT" > "$WORK_FILE.bio"
       paste "$WORK_FILE.prefix" "$WORK_FILE.bio" > "$OUTPUT_FILE"
       rm -f "$WORK_FILE.prefix" "$WORK_FILE.bio"
   else
       echo "Error: python3 not found for BIO conversion"
       exit 1
   fi
else
   echo "Saving patterns to: $OUTPUT_FILE"
   mkdir -p "$(dirname "$OUTPUT_FILE")"
   cp "$WORK_FILE" "$OUTPUT_FILE"
fi

# Cleanup
rm -f "$WORK_FILE" "$WORK_FILE.tmp"

echo "Slot expansion completed successfully"
