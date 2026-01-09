#!/usr/bin/env python3
"""
Plot AllegrOCaml speedup bar charts from ETNA benchmark results.
Figure 17: Geometric average of all speedups for each strategy and benchmark.

Usage:
    python f17.py --source precomputed
    python f17.py --source fresh -o fig17.png
"""

import json
import argparse
from pathlib import Path
import numpy as np
from scipy.stats import gmean
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Base directory for eval data
EVAL_DIR = Path(__file__).parent.parent

# Mapping from JSON files to display names and speedup keys
BENCHMARK_FILES = [
    ("bst_bespoke.json", "BST (Repeated Insert)", "baseBespokestaged", "baseBespokestagedcsr"),
    ("bst_bespokesingle.json", "BST (Single-Pass)", "baseBespokesinglestaged", "baseBespokesinglestagedcsr"),
    ("bst_type.json", "BST (Type-Derived)", "baseTypestaged", "baseTypestagedcsr"),
    ("stlc_bespoke.json", "STLC", "baseBespokestaged", "baseBespokestagedcsr"),
    ("stlc_type.json", "STLC (Type-Derived)", "baseTypestaged", "baseTypestagedcsr"),
]


def compute_geomean_speedups(data, staged_key, staged_csr_key):
    """Compute geometric mean speedup across all mutants/properties/seeds."""
    staged_speedups = []
    staged_csr_speedups = []

    for mutant_data in data.values():
        for prop_data in mutant_data.values():
            for seed_data in prop_data.values():
                if staged_key in seed_data:
                    staged_speedups.append(seed_data[staged_key])
                if staged_csr_key in seed_data:
                    staged_csr_speedups.append(seed_data[staged_csr_key])

    gm_staged = gmean(staged_speedups) if staged_speedups else 0
    gm_csr = gmean(staged_csr_speedups) if staged_csr_speedups else 0

    return {
        "AllegrOCaml": gm_staged,
        "AllegrOCaml + CSM": gm_csr
    }


def main():
    parser = argparse.ArgumentParser(description="Plot AllegrOCaml speedups (Figure 17).")
    parser.add_argument(
        "--source",
        choices=["precomputed", "fresh"],
        required=True,
        help="Data source: 'precomputed' or 'fresh'"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: figures/{source}/fig17.png)"
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
        output_path = output_dir / "fig17.png"

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        print("Run the ETNA pipeline first to generate speedup data.")
        return 1

    # Load data and compute speedups
    datasets = {}
    for filename, display_name, staged_key, staged_csr_key in BENCHMARK_FILES:
        file_path = data_dir / filename
        if not file_path.exists():
            print(f"Warning: {file_path} not found, skipping {display_name}")
            continue

        with open(file_path) as f:
            data = json.load(f)

        speedups = compute_geomean_speedups(data, staged_key, staged_csr_key)
        datasets[display_name] = speedups
        print(f"{display_name}: AllegrOCaml={speedups['AllegrOCaml']:.4f}X, AllegrOCaml + CSM={speedups['AllegrOCaml + CSM']:.4f}X")

    if not datasets:
        print("Error: No data loaded")
        return 1

    # Plot
    colors = ["#0072B2", "#D55E00"]  # AllegrOCaml (blue) and AllegrOCaml + CSM (orange)

    fig, axes = plt.subplots(1, len(datasets), figsize=(12, 3.5), sharey=True)

    if len(datasets) == 1:
        axes = [axes]

    max_value = max(max(data.values()) for data in datasets.values())
    y_limit = np.ceil(max_value) * 1.1

    for ax, (title, data) in zip(axes, datasets.items()):
        labels = list(data.keys())
        values = list(data.values())

        bars = ax.bar(labels, values, color=colors)

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height + (y_limit * 0.02), f'{height:.2f}X',
                    ha='center', va='bottom', fontsize=7)

        ax.set_title(title, fontsize=10)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
        ax.set_ylim(0, y_limit)

        ax.tick_params(axis="y", labelsize=7)

    def format_y_ticks(x, _):
        return f"{int(x)}X"

    y_ticks = np.arange(0, y_limit, step=1)
    axes[0].set_yticks(y_ticks)
    axes[0].yaxis.set_major_formatter(plt.FuncFormatter(format_y_ticks))

    fig.supylabel('Speedup', y=0.6, x=0.01, fontsize=9)
    plt.tight_layout()

    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved figure to {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
