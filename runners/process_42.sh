#!/bin/bash

# Set directories
INPUT_DIR="4.2_data"
PARSED_DIR="parsed_4.2_data/parsed"
CLEANED_DIR="parsed_4.2_data/cleaned"
FILTERED_DIR="parsed_4.2_data/filtered"
SPEEDUPS_DIR="parsed_4.2_data/speedups"

# Create output directories
mkdir -p "$PARSED_DIR" "$CLEANED_DIR" "$FILTERED_DIR" "$SPEEDUPS_DIR"

# Step 1: Parse ETNA data
echo "Parsing STLC..."
python3 parsers/parse_etna_data.py STLC "$INPUT_DIR" --output "$PARSED_DIR/stlc.json"

echo "Parsing BST..."
python3 parsers/parse_etna_data.py BST "$INPUT_DIR" --output "$PARSED_DIR/bst.json"

# Step 2: Clean/filter parsed data
echo "Filtering STLC..."
python3 etna_data_processing/clean_under5ms_or_timeout.py \
  --input "$PARSED_DIR/stlc.json" \
  --output "$CLEANED_DIR/stlc.json" \
  --filtered "$FILTERED_DIR/stlc.json"

echo "Filtering BST..."
python3 etna_data_processing/clean_under5ms_or_timeout.py \
  --input "$PARSED_DIR/bst.json" \
  --output "$CLEANED_DIR/bst.json" \
  --filtered "$FILTERED_DIR/bst.json"

# Step 3: Compute speedups (STLC: only type + bespoke, BST: all)
echo "Computing STLC speedups..."
for workload in type bespoke; do
  python3 calculate_speedups.py \
    --input "$CLEANED_DIR/stlc.json" \
    --output "$SPEEDUPS_DIR/stlc_${workload}.json" \
    --workload "$workload"
done

echo "Computing BST speedups..."
for workload in type bespoke bespokesingle; do
  python3 etna_data_processing/calculate_speedups.py \
    --input "$CLEANED_DIR/bst.json" \
    --output "$SPEEDUPS_DIR/bst_${workload}.json" \
    --workload "$workload"
done

echo "✅ All steps complete. Output in: $PARSED_DIR, $CLEANED_DIR, $FILTERED_DIR, $SPEEDUPS_DIR"
