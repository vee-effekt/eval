#!/usr/bin/env python3
"""
Plot speedup distribution from ETNA benchmark results.
Figure 18: Box plots showing speedup across different workloads.

Usage:
    python f18.py --source precomputed -o fig18.png
    python f18.py --source fresh -o fig18.png
"""

import json
import os
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_context("notebook")

# Base directory for eval data
EVAL_DIR = Path(__file__).parent.parent


def main():
    parser = argparse.ArgumentParser(description="Plot speedup results (Figure 18).")
    parser.add_argument(
        "--source",
        choices=["precomputed", "fresh"],
        required=True,
        help="Data source: 'precomputed' or 'fresh'"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: figures/{source}/fig18.png)"
    )
    args = parser.parse_args()

    # Determine input directory based on source
    data_dir = EVAL_DIR / "parsed_4.2_data" / args.source / "speedups"

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = EVAL_DIR / "figures" / args.source
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "fig18.png"

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        return 1

    file_paths = sorted([
        os.path.join(data_dir, fname)
        for fname in os.listdir(data_dir)
        if fname.endswith(".json")
    ])

    if not file_paths:
        print(f"Error: No JSON files found in {data_dir}")
        return 1

    workload_names = [
        "BST (Repeated Insert)",
        "BST (Single-Pass)",
        "BST (Type-Derived)",
        "STLC",
        "STLC (Type-Derived)"
    ]

    swarm_enabled = [
        {"AOC": False, "AOC + CSM": True},   # Repeated Insert
        {"AOC": True, "AOC + CSM": True},    # Single-Pass
        {"AOC": False, "AOC + CSM": True},   # Type-Derived (BST)
        {"AOC": True, "AOC + CSM": True},    # STLC
        {"AOC": False, "AOC + CSM": False},  # Type-Derived (STLC)
    ]

    category_order = ["AOC", "AOC + CSM"]
    category_mapping = {
        "baseTypestaged": "AOC",
        "baseTypestagedcsr": "AOC + CSM",
        "baseBespokestaged": "AOC",
        "baseBespokestagedcsr": "AOC + CSM",
        "baseBespokesinglestaged": "AOC",
        "baseBespokesinglestagedcsr": "AOC + CSM",
    }

    custom_palette = ["#0072B2", "#D55E00"]  # Blue for AOC, Orange for AOC + CSM

    num_workloads = len(file_paths)
    fig, axes = plt.subplots(1, num_workloads, figsize=(4 * num_workloads, 4), sharey=True)

    if num_workloads == 1:
        axes = [axes]

    for idx, (file_path, ax) in enumerate(zip(file_paths, axes)):
        print(f"Loading data from: {file_path}")

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue

        values = {name: [] for name in category_order}

        for condition in data.values():
            for property_data in condition.values():
                for seed_data in property_data.values():
                    for old_name, new_name in category_mapping.items():
                        if old_name in seed_data:
                            values[new_name].append(seed_data[old_name])

        for category, vals in values.items():
            print(f"  {category}: {len(vals)} values")

        if all(len(vals) == 0 for vals in values.values()):
            print(f"Skipping {file_path}: No valid data found.")
            continue

        sns.boxplot(
            data=[values[cat] for cat in category_order],
            palette=custom_palette,
            showfliers=False,
            ax=ax
        )

        for i, cat in enumerate(category_order):
            if idx < len(swarm_enabled) and swarm_enabled[idx][cat]:
                sns.swarmplot(
                    x=[i] * len(values[cat]),
                    y=values[cat],
                    color="black",
                    size=1.6,
                    alpha=0.6,
                    ax=ax
                )

        ax.axhline(y=1, color="gray", linestyle="dotted", linewidth=1)
        ax.set_xticks(range(len(category_order)))
        ax.set_xticklabels(category_order, fontsize=13)
        if idx < len(workload_names):
            ax.set_title(workload_names[idx], fontsize=16)
        ax.set_ylim(0, 10)
        ax.set_yticks(range(0, 11))

    def format_y_ticks(x, _):
        return f"{int(x)}X"

    for ax in axes:
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_y_ticks))

    plt.tight_layout(rect=[0.01, 0.01, 1, 1])
    fig.supylabel('Speedup', x=0.000001, fontsize=16)

    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved figure to {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
