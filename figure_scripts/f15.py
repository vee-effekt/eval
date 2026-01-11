#!/usr/bin/env python3
"""
Plot OCaml speedup analysis (Figure 15).
Static data showing speedup from AllegrOCaml and CSplitMix.

Usage:
    python f15.py --source precomputed
    python f15.py --source fresh
"""

import argparse
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# Base directory for eval data
EVAL_DIR = Path(__file__).parent.parent

data2 = {
    "Name": ["BST (RI)", "STLC", "Bool List", "BST (SP)"],
    "RandCalls": [353, 211, 100, 271],
    "Speedup": [4.4824, 1.0923, 1.000339, 4.2746]
}

df1 = pd.DataFrame(data2)

data1 = {
    "Name": ["BST (RI)", "STLC", "Bool List", "BST (SP)"],
    "Binds": [2, 670, 300, 188],
    "Speedup": [1.18, 5.24, 2.77, 2.22]
}
df2 = pd.DataFrame(data1)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), sharey=True, constrained_layout=False)

ax1.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
ax1.scatter(df2["Binds"], df2["Speedup"], s=80, color="#1f77b4", edgecolor="black", zorder=3)

for _, row in df2.iterrows():
    ax1.text(row["Binds"] + 10, row["Speedup"] + 0.1, row["Name"], fontsize=9, va='center')

ax1.set_xlabel("Binds", fontsize=12)
ax1.set_ylabel("Speedup from AllegrOCaml", fontsize=12)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}×"))
ax1.margins(x=0.1, y=0.2)

ax2.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
ax2.scatter(df1["RandCalls"], df1["Speedup"], s=80, color="#1f77b4", edgecolor="black", zorder=3)

for _, row in df1.iterrows():
    ax2.text(row["RandCalls"] + 10, row["Speedup"] + 0.1, row["Name"], fontsize=9, va='center')

ax2.set_xlabel("Samples", fontsize=12)
ax2.set_ylabel("Speedup from CSplitMix (over AllegrOCaml)", fontsize=12)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}×"))
ax2.margins(x=0.5, y=0.5)

ax1.set_yticks(range(0, 7))
ax2.set_yticks(range(0, 7))

for ax in (ax1, ax2):
    for label in ax.get_yticklabels():
        label.set_horizontalalignment('left')
        label.set_x(-0.05)

plt.subplots_adjust(left=0.08, right=0.98, wspace=0.3)


def main():
    parser = argparse.ArgumentParser(
        description="Plot OCaml speedup analysis (Figure 15)."
    )
    parser.add_argument(
        "--source",
        choices=["precomputed", "fresh"],
        required=True,
        help="Data source: 'precomputed' or 'fresh'"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: figures/{source}/fig15.png)"
    )
    args = parser.parse_args()

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = EVAL_DIR / "figures" / args.source
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "fig15.png"

    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved figure to {output_path}")
    return 0


if __name__ == "__main__":
    exit(main())
