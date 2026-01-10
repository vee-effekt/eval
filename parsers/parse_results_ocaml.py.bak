#!/usr/bin/env python3
"""
Parser for results_ocaml.txt benchmark output.
Generates JSON files for f14.py plotting and a separate compilation times file.

Usage:
    python parse_results_ocaml.py --source precomputed
    python parse_results_ocaml.py --source fresh
"""

import argparse
import json
import re
from pathlib import Path
from collections import defaultdict

# Base directory for eval data
EVAL_DIR = Path(__file__).parent.parent


def parse_time_ns(s):
    """Convert a time string like '1_234.56ns' to a float."""
    if not s or s.strip() == '':
        return None
    s = s.replace('_', '').replace('ns', '').strip()
    try:
        return float(s)
    except ValueError:
        return None


def parse_benchmark_name(name):
    """
    Parse benchmark names and return (group, variant, size).

    Examples:
        'boollist_base:n=10' -> ('boollist_bespoke', 'base', 10)
        'boollist_staged_sr:n=100' -> ('boollist_bespoke', 'base_Staged_SR', 100)
        'bst_baseBespoke:n=10' -> ('bst_bespoke', 'base', 10)
        'bst_baseBespoke_Staged_SR:n=10' -> ('bst_bespoke', 'base_Staged_SR', 10)
        'bst_baseSingleBespoke:n=10' -> ('bst_single', 'base', 10)
        'bst_baseType:n=10' -> ('bst_type', 'base', 10)
        'stlc_baseBespoke:n=10' -> ('stlc_bespoke', 'base', 10)
        'stlc_baseType:n=10' -> ('stlc_type', 'base', 10)
    """
    match = re.match(r'(.+?):n=(\d+)', name)
    if not match:
        return None, None, None

    full_name, size = match.groups()
    size = int(size)

    # Handle boollist benchmarks (different naming convention)
    if full_name.startswith('boollist_'):
        rest = full_name[len('boollist_'):]
        if rest == 'base':
            return 'boollist_bespoke', 'base', size
        elif rest == 'staged_sr':
            return 'boollist_bespoke', 'base_Staged_SR', size
        elif rest == 'staged_csr':
            return 'boollist_bespoke', 'base_Staged_CSR', size

    # Handle bst benchmarks
    elif full_name.startswith('bst_'):
        rest = full_name[len('bst_'):]

        # BST Single Pass
        if rest.startswith('baseSingleBespoke'):
            suffix = rest[len('baseSingleBespoke'):]
            if suffix == '':
                return 'bst_single', 'base', size
            elif suffix == '_Staged_SR':
                return 'bst_single', 'base_Staged_SR', size
            elif suffix == '_Staged_CSR':
                return 'bst_single', 'base_Staged_CSR', size

        # BST Bespoke (Repeated Insert)
        elif rest.startswith('baseBespoke'):
            suffix = rest[len('baseBespoke'):]
            if suffix == '':
                return 'bst_bespoke', 'base', size
            elif suffix == '_Staged_SR':
                return 'bst_bespoke', 'base_Staged_SR', size
            elif suffix == '_Staged_CSR':
                return 'bst_bespoke', 'base_Staged_CSR', size

        # BST Type
        elif rest.startswith('baseType'):
            suffix = rest[len('baseType'):]
            if suffix == '':
                return 'bst_type', 'base', size
            elif suffix == '_Staged_SR':
                return 'bst_type', 'base_Staged_SR', size
            elif suffix == '_Staged_CSR':
                return 'bst_type', 'base_Staged_CSR', size

    # Handle stlc benchmarks
    elif full_name.startswith('stlc_'):
        rest = full_name[len('stlc_'):]

        # STLC Bespoke
        if rest.startswith('baseBespoke'):
            suffix = rest[len('baseBespoke'):]
            if suffix == '':
                return 'stlc_bespoke', 'base', size
            elif suffix == '_Staged_SR':
                return 'stlc_bespoke', 'base_Staged_SR', size
            elif suffix == '_Staged_CSR':
                return 'stlc_bespoke', 'base_Staged_CSR', size

        # STLC Type
        elif rest.startswith('baseType'):
            suffix = rest[len('baseType'):]
            if suffix == '':
                return 'stlc_type', 'base', size
            elif suffix == '_Staged_SR':
                return 'stlc_type', 'base_Staged_SR', size
            elif suffix == '_Staged_CSR':
                return 'stlc_type', 'base_Staged_CSR', size

    return None, None, None


def parse_compilation_times(lines):
    """Extract compilation times from the file."""
    times = {}
    in_compilation_section = False

    for line in lines:
        if 'Compilation times:' in line:
            in_compilation_section = True
            continue

        if in_compilation_section and ':' in line:
            match = re.match(r'(.+?)\s*:\s*([\d.]+)ms', line.strip())
            if match:
                name, time_ms = match.groups()
                times[name.strip()] = float(time_ms)

    return times


def main():
    parser = argparse.ArgumentParser(
        description="Parse OCaml benchmark results into JSON format."
    )
    parser.add_argument(
        "--source",
        choices=["precomputed", "fresh"],
        required=True,
        help="Data source: 'precomputed' or 'fresh'"
    )
    args = parser.parse_args()

    # Determine input and output paths based on source
    input_dir = EVAL_DIR / "4.1_data_ocaml" / args.source
    output_dir = EVAL_DIR / "parsed_4.1_data_ocaml" / args.source

    input_path = input_dir / "results_ocaml.txt"

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1

    # Read the file
    with input_path.open() as f:
        lines = f.readlines()

    # Parse benchmark data
    result = defaultdict(lambda: defaultdict(dict))

    for line in lines:
        if not line.startswith('│ '):
            continue

        parts = [col.strip() for col in line.strip('│ \n').split('│')]
        if len(parts) < 2:
            continue

        name, time_str = parts[0], parts[1]

        # Skip header rows
        if name == 'Name' or 'Time' in name:
            continue

        group, variant, size = parse_benchmark_name(name)
        if not group or not variant or size is None:
            continue

        time_val = parse_time_ns(time_str)
        if time_val is not None:
            result[group][variant][size] = time_val

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

    # Parse and write compilation times
    compilation_times = parse_compilation_times(lines)
    if compilation_times:
        comp_file = output_dir / 'compilation_times.txt'
        with comp_file.open('w') as f:
            f.write("Compilation Times\n")
            f.write("=" * 40 + "\n\n")
            for name, time_ms in compilation_times.items():
                f.write(f"{name}: {time_ms:.3f} ms\n")
        print(f"Wrote {comp_file}")

    print(f"\nParsed {len(result)} benchmark groups from {args.source} data")
    for group in sorted(result.keys()):
        print(f"  - {group}: {len(result[group])} variants")

    return 0


if __name__ == "__main__":
    exit(main())
