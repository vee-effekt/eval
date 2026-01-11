#!/usr/bin/env python3
"""
Plot Scala benchmark results from JSON files.
Figure 16: Runtime comparison across benchmark sizes.

Usage:
    python f16.py --source precomputed -o fig16.png
    python f16.py --source fresh -o fig16.png
"""

import os
import json
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

# Base directory for eval data
EVAL_DIR = Path(__file__).parent.parent


def normalize_title(name):
    return {
        "BoolListBespoke": "Bool List",
        "BstBespoke": "BST (Single-Pass)",
        "BstType": "BST (Repeated Insert)",
        "Term": "STLC"
    }.get(name, name)


def load_data_from_directory(directory):
    merged = {}

    for file in os.listdir(directory):
        if not file.endswith(".json"):
            continue
        with open(os.path.join(directory, file)) as f:
            data = json.load(f)

        for raw_title, variants in data.items():
            title = normalize_title(raw_title)
            if title not in merged:
                merged[title] = {}

            for variant, entries in variants.items():
                if variant not in merged[title]:
                    merged[title][variant] = {}
                merged[title][variant].update({int(k): v for k, v in entries.items()})

    print("Loaded benchmarks:", list(merged.keys()))
    return merged


def plot(parsed_data, output_path):
    # Order: Bool List, BST Single Pass, STLC
    benchmark_order = ["Bool List", "BST (Single-Pass)", "STLC"]
    # Filter to only include benchmarks we have data for
    benchmark_order = [b for b in benchmark_order if b in parsed_data]

    variant_order = ["SC", "ScAllegro"]
    n_values = [10, 100, 1000, 10000]

    styles = {
        "SC": ("s", "#de3423", ":"),
        "ScAllegro": ("o", "#23b6de", "--"),
    }

    n_benchmarks = len(benchmark_order)
    fig, axes = plt.subplots(1, n_benchmarks, figsize=(2.0 * n_benchmarks, 2.25), sharey=True)
    if n_benchmarks == 1:
        axes = [axes]

    def plot_data(ax, data, title):
        for variant in variant_order:
            if variant not in data:
                print(f"Missing variant {variant} in {title}")
                continue
            values = data[variant]
            marker, color, linestyle = styles[variant]
            y_vals = [values.get(n) for n in n_values]
            ax.plot(n_values, y_vals, marker=marker, linestyle=linestyle,
                    linewidth=1.5, color=color, label=variant)
        ax.set_title(title, fontsize=10)
        ax.set_yscale("log")
        ax.set_xscale("log")
        ax.set_xticks(n_values)
        ax.get_xaxis().set_major_formatter(ScalarFormatter())
        ax.tick_params(axis="both", which="major", labelsize=8)
        ax.set_box_aspect(1)

    for ax, benchmark in zip(axes, benchmark_order):
        if benchmark in parsed_data:
            plot_data(ax, parsed_data[benchmark], benchmark)
        else:
            print(f"Benchmark missing: {benchmark}")
            ax.set_title(benchmark + " (missing)", fontsize=10)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, fontsize=9, frameon=False)

    fig.tight_layout(rect=[0.02, 0.05, 1, 0.91])
    fig.supylabel('Run time (ns)', y=0.45, x=0.04, fontsize=10)
    fig.supxlabel('Size', fontsize=10)

    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved figure to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Plot Scala benchmark results (Figure 16)."
    )
    parser.add_argument(
        "--source",
        choices=["precomputed", "fresh"],
        required=True,
        help="Data source: 'precomputed' or 'fresh'"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: figures/{source}/fig16.png)"
    )
    args = parser.parse_args()

    # Determine input directory based on source
    data_dir = EVAL_DIR / "parsed_4.1_data_scala" / args.source

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = EVAL_DIR / "figures" / args.source
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "fig16.png"

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        print("Run the parser first: python parsers/parse_results_scala_csv.py --source", args.source)
        return 1

    parsed_data = load_data_from_directory(data_dir)

    if not parsed_data:
        print(f"Error: No data found in {data_dir}")
        return 1

    plot(parsed_data, output_path)
    return 0


if __name__ == "__main__":
    exit(main())
