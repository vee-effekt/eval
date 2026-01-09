#!/usr/bin/env python3
"""
Calculate speedups for ETNA benchmark results.

Usage:
    python calculate_speedups.py --source precomputed --system BST --workload type
    python calculate_speedups.py --source precomputed --system BST --workload bespoke
    python calculate_speedups.py --source precomputed --system STLC --workload bespokesingle
"""

import json
import argparse
from pathlib import Path
from collections import defaultdict

# Base directory for eval data
EVAL_DIR = Path(__file__).parent.parent

# Define the strategy keys per workload
WORKLOAD_KEYS = {
    "type": (
        "baseType", [
            "baseType", "baseTypestaged", "baseTypestagedc", "baseTypestagedcsr"
        ]
    ),
    "bespoke": (
        "baseBespoke", [
            "baseBespoke", "baseBespokestaged", "baseBespokestagedc", "baseBespokestagedcsr"
        ]
    ),
    "bespokesingle": (
        "baseBespokesingle", [
            "baseBespokesingle", "baseBespokesinglestaged", "baseBespokesinglestagedc", "baseBespokesinglestagedcsr"
        ]
    )
}

def compute_speedup(data, workload):
    baseline_key, strategy_keys = WORKLOAD_KEYS[workload]
    speedup_data = defaultdict(lambda: defaultdict(dict))

    for mutant, properties in data.items():
        for prop, values in properties.items():
            per_seed_values = defaultdict(dict)

            for key, value in values.items():
                *field_name_parts, seed = key.split("_")
                field_name = "_".join(field_name_parts)
                per_seed_values[seed][field_name] = value

            for seed, timings in per_seed_values.items():
                base_time = timings.get(baseline_key)
                if base_time is None:
                    continue

                speedup_data[mutant][prop][seed] = {
                    k: base_time / timings[k]
                    for k in strategy_keys
                    if k in timings and timings[k] is not None
                }

                # Assert base key always maps to speedup 1.0
                if baseline_key in speedup_data[mutant][prop][seed] and speedup_data[mutant][prop][seed][baseline_key] != 1.0:
                    raise ValueError(f"Incorrect base speedup for {baseline_key} seed {seed} in {mutant} -> {prop}")

    return speedup_data

def main():
    parser = argparse.ArgumentParser(description="Compute ETNA benchmark speedups.")
    parser.add_argument(
        "--source",
        choices=["precomputed", "fresh"],
        required=True,
        help="Data source: 'precomputed' or 'fresh'"
    )
    parser.add_argument(
        "--system",
        choices=["BST", "STLC"],
        required=True,
        help="Benchmark system to process"
    )
    parser.add_argument(
        "--workload",
        choices=["type", "bespoke", "bespokesingle"],
        required=True,
        help="Workload group"
    )
    args = parser.parse_args()

    # Determine input and output paths based on source
    input_dir = EVAL_DIR / "parsed_4.2_data" / args.source / "cleaned"
    output_dir = EVAL_DIR / "parsed_4.2_data" / args.source / "speedups"

    input_file = input_dir / f"{args.system.lower()}_results_cleaned.json"

    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{args.system.lower()}_{args.workload}.json"

    print(f"Computing {args.workload} speedups for {args.system} from {input_file}...")

    with open(input_file, "r") as file:
        data = json.load(file)

    result = compute_speedup(data, args.workload)

    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Speedup results saved to {output_file}")
    return 0


if __name__ == "__main__":
    exit(main())
