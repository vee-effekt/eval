import os
import json
import argparse
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

# Rename top-level keys from files
def normalize_title(name):
    return {
        "BoolListBespoke": "Bool List",
        "BstBespoke": "BST (Single-Pass)",
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

def plot(parsed_data):
    benchmark_order = ["Bool List", "BST (Single-Pass)", "STLC"]
    variant_order = ["SC", "ScAllegro"]
    n_values = [10, 100, 1000, 10000]

    styles = {
        "SC": ("s", "#de3423", ":"),
        "ScAllegro": ("o", "#23b6de", "--"),
    }

    fig, axes = plt.subplots(1, 3, figsize=(5.5, 2.25), sharey=True)

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
    plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Path to directory containing JSON files")
    args = parser.parse_args()

    parsed_data = load_data_from_directory(args.directory)
    plot(parsed_data)

if __name__ == "__main__":
    main()
