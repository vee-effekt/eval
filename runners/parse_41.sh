#!/bin/bash
chmod -R u+w /4.1_data_ocaml /parsed_4.1_data_ocaml

# Exit immediately on error
set -e

# Path to your parser script
PARSER="parsers/parse_ocaml_benchmarking_data.py"

# List of (input, output) pairs
declare -a JOBS=(
    "4.1_data/boollist_bespoke.txt parsed_4.1_data/boollist_bespoke.json"
    "4.1_data/bst_bespoke.txt parsed_4.1_data/bst_bespoke.json"
    "4.1_data/stlc_bespoke.txt parsed_4.1_data/stlc_bespoke.json"
    "4.1_data/stlc_type.txt parsed_4.1_data/stlc_type.json"
    "4.1_data/bst_type.txt parsed_4.1_data/bst_type.json"
    "4.1_data/bst_single.txt parsed_4.1_data/bst_single.json"
)

for job in "${JOBS[@]}"; do
    set -- $job
    input="$1"
    output="$2"
    output_dir=$(dirname "$output")

    # Make sure the output directory exists
    mkdir -p "$output_dir"

    echo "Processing $input → $output"
    python3 "$PARSER" "$input" "$output"
done

echo "✅ All benchmark files processed."