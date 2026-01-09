#!/usr/bin/env python3
"""
Parser for ETNA benchmark results (BST and STLC mutation testing).

Usage:
    python parse_etna_data.py --source precomputed --system BST
    python parse_etna_data.py --source precomputed --system STLC
    python parse_etna_data.py --source fresh --system BST
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict

# Base directory for eval data
EVAL_DIR = Path(__file__).parent.parent


def parse_results(system_name, base_dir):
    strategy_order = [
        "baseType", "baseTypestaged", "baseTypestagedc", "baseTypestagedcsr",
        "baseBespoke", "baseBespokestaged", "baseBespokestagedc", "baseBespokestagedcsr",
        "baseBespokesingle", "baseBespokesinglestaged", "baseBespokesinglestagedc", "baseBespokesinglestagedcsr"
    ]

    seed_dirs = []
    for item in os.listdir(base_dir):
        if os.path.isdir(os.path.join(base_dir, item)) and item.startswith(f"oc3-{system_name.lower()}-"):
            seed_match = re.search(rf"oc3-{system_name.lower()}-(\d+)", item)
            if seed_match:
                seed = seed_match.group(1)
                seed_dirs.append((seed, os.path.join(base_dir, item)))

    results = defaultdict(lambda: defaultdict(lambda: {}))

    for seed, seed_dir in seed_dirs:
        for root, _, files in os.walk(seed_dir):
            for file in files:
                parts = file.split(",")
                if len(parts) >= 3 and parts[0] == system_name:
                    strategy = parts[1]
                    mutant = parts[2]

                    prop_match = re.search(r"prop_([^\.]+)\.txt", parts[-1])
                    if prop_match:
                        property_name = f"prop_{prop_match.group(1)}"

                        try:
                            with open(os.path.join(root, file), 'r') as f:
                                content = f.read()

                                if "[exit timeout]" in content:
                                    duration = 60.0
                                else:
                                    duration_match = re.search(r"duration (\d+)|(\d+\.\d+) duration", content)
                                    if duration_match:
                                        duration = duration_match.group(1) or duration_match.group(2)
                                        if not duration:
                                            alt_match = re.search(r"\[exit ok, (\d+\.\d+) duration", content)
                                            if alt_match:
                                                duration = alt_match.group(1)
                                        duration = float(duration) if duration else None
                                    else:
                                        duration = None

                                if duration is not None:
                                    strategy_seed = f"{strategy}_{seed}"
                                    results[mutant][property_name][strategy_seed] = duration

                        except Exception as e:
                            print(f"Error processing file {file}: {e}")

    sorted_results = {}
    for mutant in sorted(results.keys()):
        sorted_results[mutant] = {}
        for prop in sorted(results[mutant].keys()):
            sorted_results[mutant][prop] = {}
            for strategy in strategy_order:
                for seed, _ in sorted(seed_dirs, key=lambda x: int(x[0])):
                    strategy_seed = f"{strategy}_{seed}"
                    if strategy_seed in results[mutant][prop]:
                        sorted_results[mutant][prop][strategy_seed] = results[mutant][prop][strategy_seed]
                    else:
                        sorted_results[mutant][prop][strategy_seed] = None
    return sorted_results


def main():
    parser = argparse.ArgumentParser(description="Parse ETNA benchmark results (BST or STLC).")
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
        help="Benchmark system to parse"
    )
    args = parser.parse_args()

    # Determine input and output paths based on source
    input_dir = EVAL_DIR / "4.2_data" / args.source
    output_dir = EVAL_DIR / "parsed_4.2_data" / args.source / "parsed"

    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Parsing {args.system} data from {input_dir}...")
    parsed_results = parse_results(args.system, input_dir)

    output_file = output_dir / f"{args.system.lower()}_results.json"
    with open(output_file, "w") as f:
        json.dump(parsed_results, f, indent=2)

    print(f"Results saved to {output_file}")
    print(f"Parsed {len(parsed_results)} mutants")

    return 0


if __name__ == "__main__":
    exit(main())
