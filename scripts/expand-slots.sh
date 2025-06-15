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

   # Count initial occurrences
   local initial_count=$(grep -o "$slot" "$WORK_FILE" | wc -l)
   if [ "$initial_count" -eq 0 ]; then
       return 0
   fi

   echo "  Processing $initial_count occurrences of $slot"

   while IFS= read -r text; do
       # Skip empty lines
       [ -z "$text" ] && continue

       # Check if slot still exists in file before processing
       if ! grep -q "$slot" "$WORK_FILE"; then
           break
       fi

       if [ "$ADD_BIO" = "true" ]; then
           short_slot=$(echo "$slot" | sed 's/.*\.SLOT\.//g')
           # Use more precise sed with line-by-line processing to avoid infinite loops
           sed "1,/$slot/{s|$slot|{$short_slot:$text}|;}" "$WORK_FILE" > "$WORK_FILE.tmp" && mv "$WORK_FILE.tmp" "$WORK_FILE"
       else
           # Use more precise sed with line-by-line processing to avoid infinite loops
           sed "1,/$slot/{s|$slot|$text|;}" "$WORK_FILE" > "$WORK_FILE.tmp" && mv "$WORK_FILE.tmp" "$WORK_FILE"
       fi

       # Safety check: if we're in repeat mode and nothing changed, break to avoid infinite loop
       if [ "$REPEAT" = "true" ]; then
           local current_count=$(grep -o "$slot" "$WORK_FILE" | wc -l)
           if [ "$current_count" -eq "$initial_count" ]; then
               echo "  Warning: No progress made on $slot, stopping to avoid infinite loop"
               break
           fi
           initial_count=$current_count
       fi

   done < "$slot_file"
}

# Replace __ with tab
sed -i 's/__ /__\t/g' "$WORK_FILE"

# Process slots if directory exists and has files
if [ -d "$SLOTS_DIR" ] && [ "$(ls -A "$SLOTS_DIR" 2>/dev/null)" ]; then
   # Create a list of slot files sorted by length (longest first) to avoid substring issues
   slot_files_sorted=$(find "$SLOTS_DIR" -name "*" -type f -exec basename {} \; | awk '{print length, $0}' | sort -nr | cut -d' ' -f2-)

   # Process each slot file
   for slot in $slot_files_sorted; do
       slot_file="$SLOTS_DIR/$slot"
       if [ -f "$slot_file" ]; then
           # Check if this slot exists in the work file
           if grep -q "$slot" "$WORK_FILE"; then
               echo "Expanding with phrases from $slot"

               # Track iterations to prevent infinite loops
               max_iterations=1000
               iteration=0

               if [ "$REPEAT" = "true" ]; then
                   # Keep processing until no more instances of this slot exist
                   while grep -q "$slot" "$WORK_FILE" && [ $iteration -lt $max_iterations ]; do
                       before_count=$(grep -o "$slot" "$WORK_FILE" | wc -l)
                       substitute_slots "$slot"
                       after_count=$(grep -o "$slot" "$WORK_FILE" | wc -l)

                       # If no progress, break to avoid infinite loop
                       if [ "$after_count" -ge "$before_count" ]; then
                           echo "  No progress made, stopping expansion of $slot"
                           break
                       fi

                       iteration=$((iteration + 1))
                   done

                   if [ $iteration -ge $max_iterations ]; then
                       echo "  Warning: Maximum iterations reached for $slot"
                   fi
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
