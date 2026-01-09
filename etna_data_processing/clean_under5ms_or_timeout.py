#!/usr/bin/env python3
"""
Clean ETNA benchmark results by removing entries with very short times or all-timeout.

Usage:
    python clean_under5ms_or_timeout.py --source precomputed --system BST
    python clean_under5ms_or_timeout.py --source precomputed --system STLC
    python clean_under5ms_or_timeout.py --source fresh --system BST
"""

import json
import argparse
from pathlib import Path

# Base directory for eval data
EVAL_DIR = Path(__file__).parent.parent


def clean_json(input_file, cleaned_output, removed_output):
    with open(input_file, 'r') as f:
        data = json.load(f)

    removed_data = {}

    strategy_prefixes = ["baseType", "baseBespoke", "baseBespokesingle"]

    for mutant, properties in data.items():
        for prop, values in properties.items():
            seeds_to_remove = set()
            for key, value in list(values.items()):
                if value is not None and any(key.startswith(prefix + "_") for prefix in strategy_prefixes) and value <= 0.0005:
                    seed = key.split("_")[1]
                    seeds_to_remove.add(seed)
                    removed_data.setdefault(mutant, {}).setdefault(prop, {})[key] = value
                    del values[key]

            # Remove corresponding staged versions
            for seed in seeds_to_remove:
                for prefix in strategy_prefixes:
                    base_key = f"{prefix}_{seed}"
                    if base_key in removed_data.get(mutant, {}).get(prop, {}):
                        for suffix in ["staged", "stagedc", "stagedcsr"]:
                            key_to_remove = f"{prefix}{suffix}_{seed}"
                            if key_to_remove in values:
                                removed_data[mutant][prop][key_to_remove] = values[key_to_remove]
                                del values[key_to_remove]

            # Remove entries where all 4 variants are 60.0
            to_remove = set()
            for seed in list(values.keys()):
                if any(seed.startswith(prefix + "_") for prefix in strategy_prefixes):
                    base_seed = seed.split("_")[1]

                    base_variants = {
                        "baseType": [
                            f"baseType_{base_seed}",
                            f"baseTypestaged_{base_seed}",
                            f"baseTypestagedc_{base_seed}",
                            f"baseTypestagedcsr_{base_seed}",
                        ],
                        "baseBespoke": [
                            f"baseBespoke_{base_seed}",
                            f"baseBespokestaged_{base_seed}",
                            f"baseBespokestagedc_{base_seed}",
                            f"baseBespokestagedcsr_{base_seed}",
                        ],
                        "baseBespokesingle": [
                            f"baseBespokesingle_{base_seed}",
                            f"baseBespokesinglestaged_{base_seed}",
                            f"baseBespokesinglestagedc_{base_seed}",
                            f"baseBespokesinglestagedcsr_{base_seed}",
                        ],
                    }

                    for variants in base_variants.values():
                        if all(values.get(var, -1) == 60.0 for var in variants):
                            to_remove.update(variants)

            for key in to_remove:
                if key in values:
                    removed_data.setdefault(mutant, {}).setdefault(prop, {})[key] = values[key]
                    del values[key]

    with open(cleaned_output, 'w') as f:
        json.dump(data, f, indent=2)

    with open(removed_output, 'w') as f:
        json.dump(removed_data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Clean ETNA benchmark results.")
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
        help="Benchmark system to clean"
    )
    args = parser.parse_args()

    # Determine input and output paths based on source
    input_dir = EVAL_DIR / "parsed_4.2_data" / args.source / "parsed"
    output_dir = EVAL_DIR / "parsed_4.2_data" / args.source / "cleaned"

    input_file = input_dir / f"{args.system.lower()}_results.json"

    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    cleaned_output = output_dir / f"{args.system.lower()}_results_cleaned.json"
    removed_output = output_dir / f"{args.system.lower()}_results_removed.json"

    print(f"Cleaning {args.system} data from {input_file}...")
    clean_json(input_file, cleaned_output, removed_output)

    print(f"Cleaned results saved to {cleaned_output}")
    print(f"Removed entries saved to {removed_output}")

    return 0


if __name__ == "__main__":
    exit(main())
