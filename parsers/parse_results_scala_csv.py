#!/usr/bin/env python3
"""
Parser for results_scala.csv benchmark output (JMH CSV format).
Generates JSON files for plotting, compatible with f16-style plots.

Usage:
    python parse_results_scala_csv.py --source precomputed
    python parse_results_scala_csv.py --source fresh
"""

import argparse
import csv
import json
import re
from pathlib import Path
from collections import defaultdict

# Base directory for eval data
EVAL_DIR = Path(__file__).parent.parent


def parse_benchmark_name(benchmark):
    """
    Parse benchmark names from CSV and return (group, variant, size).

    Examples:
        'benchmark.GenBm.generateBoolListBespoke10' -> ('BoolListBespoke', 'SC', 10)
        'benchmark.GenBm.generateBoolListBespokeStaged10' -> ('BoolListBespoke', 'ScAllegro', 10)
        'benchmark.GenBm.generateBstBespoke100' -> ('BstBespoke', 'SC', 100)
        'benchmark.GenBm.generateBstType10' -> ('BstType', 'SC', 10)
        'benchmark.GenBm.generateTerm10' -> ('Term', 'SC', 10)
    """
    # Extract the method name part
    match = re.match(r'benchmark\.GenBm\.generate(.+?)(\d+)$', benchmark)
    if not match:
        return None, None, None

    name_part = match.group(1)
    size = int(match.group(2))

    # Check if it's a staged variant
    is_staged = name_part.endswith('Staged')
    if is_staged:
        name_part = name_part[:-6]  # Remove 'Staged' suffix

    # Variant names for f16.py compatibility
    variant = 'ScAllegro' if is_staged else 'SC'

    # Keep original benchmark names for f16.py compatibility
    # f16.py normalizes: BoolListBespoke -> "Bool List", BstBespoke -> "BST (Single-Pass)", Term -> "STLC"
    group = name_part

    return group, variant, size


def main():
    parser = argparse.ArgumentParser(
        description="Parse Scala benchmark results (CSV) into JSON format."
    )
    parser.add_argument(
        "--source",
        choices=["precomputed", "fresh"],
        required=True,
        help="Data source: 'precomputed' or 'fresh'"
    )
    args = parser.parse_args()

    # Determine input and output paths based on source
    input_dir = EVAL_DIR / "4.1_data_scala" / args.source
    output_dir = EVAL_DIR / "parsed_4.1_data_scala" / args.source

    input_path = input_dir / "results_scala.csv"

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1

    # Parse CSV
    result = defaultdict(lambda: defaultdict(dict))

    with input_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            benchmark = row['Benchmark']
            score = float(row['Score'])

            group, variant, size = parse_benchmark_name(benchmark)
            if not group or not variant or size is None:
                print(f"Skipping unknown benchmark: {benchmark}")
                continue

            result[group][variant][size] = score

    # Write JSON files for each benchmark group
    output_dir.mkdir(parents=True, exist_ok=True)

    for group, group_data in sorted(result.items()):
        json_data = {
            group: {
                variant: {
                    size: variant_data[size]
                    for size in sorted(variant_data)
                }
                for variant, variant_data in sorted(group_data.items())
            }
        }

        output_file = output_dir / f"{group}.json"
        with output_file.open('w') as f:
            json.dump(json_data, f, indent=4)
        print(f"Wrote {output_file}")

    print(f"\nParsed {len(result)} benchmark groups from {args.source} data")
    for group in sorted(result.keys()):
        print(f"  - {group}: {len(result[group])} variants")

    return 0


if __name__ == "__main__":
    exit(main())
