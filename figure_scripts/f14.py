#!/usr/bin/env python3
"""
Plot OCaml benchmark results from JSON files.
Figure 14: Runtime comparison across benchmark sizes.

Usage:
    python f14.py --source precomputed -o fig14.png
    python f14.py --source fresh -o fig14.png
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


def load_parsed_data_from_directory(directory):
    combined_data = {}

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), "r") as file:
                data = json.load(file)

                for benchmark, results in data.items():
                    title = format_title(benchmark)

                    if title not in combined_data:
                        combined_data[title] = {}

                    for variant, timings in results.items():
                        label = format_variant_label(variant)
                        combined_data[title][label] = {int(k): v for k, v in timings.items()}

    return combined_data


def format_title(raw_name):
    title_map = {
        "boollist_bespoke": "Bool List",
        "stlc_bespoke": "STLC",
        "stlc_type": "STLC (Type-Derived)",
        "bst_single": "BST (Single-Pass)",
        "bst_bespoke": "BST (Repeated Insert)",
        "bst_type": "BST (Type-Derived)",
    }
    return title_map.get(raw_name.lower(), raw_name)


def format_variant_label(raw_label):
    mapping = {
        "base": "BQ",
        "base_Staged_SR": "AllegrOCaml",
        "base_Staged_CSR": "AllegrOCaml + CSplitMix",
    }
    return mapping.get(raw_label, raw_label)


def main():
    parser = argparse.ArgumentParser(
        description="Plot OCaml benchmark results (Figure 14)."
    )
    parser.add_argument(
        "--source",
        choices=["precomputed", "fresh"],
        required=True,
        help="Data source: 'precomputed' or 'fresh'"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: figures/{source}/fig14.png)"
    )
    args = parser.parse_args()

    # Determine input directory based on source
    data_dir = EVAL_DIR / "parsed_4.1_data_ocaml" / args.source

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = EVAL_DIR / "figures" / args.source
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "fig14.png"

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        print("Run the parser first: python parsers/parse_results_ocaml.py --source", args.source)
        return 1

    parsed_data = load_parsed_data_from_directory(data_dir)

    if not parsed_data:
        print(f"Error: No data found in {data_dir}")
        return 1

    # Define plot order to match expected figure layout
    # Top row: BST variants, Bottom row: STLC variants + Bool List
    plot_order = [
        "BST (Type-Derived)",
        "BST (Repeated Insert)",
        "BST (Single-Pass)",
        "STLC (Type-Derived)",
        "STLC",
        "Bool List",
    ]
    # Filter to only include benchmarks we have data for
    plot_order = [p for p in plot_order if p in parsed_data]

    n_values = [10, 100, 1000, 10000]
    styles = [
        ("s", "#c90076", ":"),    # BQ
        ("^", "#D55E00", "-."),   # AllegrOCaml + CSplitMix
        ("o", "#0072B2", "--"),   # AllegrOCaml
    ]

    # Calculate grid dimensions
    n_plots = len(plot_order)
    n_cols = 3
    n_rows = (n_plots + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(7, 5.5), sharey=True)
    axes = axes.flatten() if n_plots > 1 else [axes]

    def plot_data(ax, data, title):
        for (method, values), (marker, color, linestyle) in zip(data.items(), styles):
            y_vals = [values.get(n, None) for n in n_values]
            if None not in y_vals:
                ax.plot(n_values, y_vals, marker=marker, linestyle=linestyle,
                        linewidth=1.5, color=color, label=method)
        ax.set_title(title, fontsize=10)
        ax.set_yscale("log")
        ax.set_xscale("log")
        ax.set_xticks(n_values)
        ax.get_xaxis().set_major_formatter(ScalarFormatter())
        ax.tick_params(axis="both", which="major", labelsize=8)

    for i, (ax, dataset) in enumerate(zip(axes, plot_order)):
        plot_data(ax, parsed_data[dataset], dataset)

    # Hide unused axes
    for i in range(len(plot_order), len(axes)):
        axes[i].set_visible(False)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=9, frameon=False)

    fig.tight_layout(rect=[0.02, 0.05, 1, 0.91])
    fig.supylabel('Run time (ns)', y=0.466, x=0.018, fontsize=10)
    fig.supxlabel('Size', y=0.04, fontsize=10)

    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved figure to {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
