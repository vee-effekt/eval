import os
import json
import argparse
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

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
    parser = argparse.ArgumentParser(description="Plot benchmark results from JSON files.")
    parser.add_argument("directory", help="Path to the directory containing JSON files")
    args = parser.parse_args()

    parsed_data = load_parsed_data_from_directory(args.directory)

    plot_order = list(parsed_data.keys())
    n_values = [10, 100, 1000, 10000]
    styles = [
        ("s", "#c90076", ":"),    # BQ
        ("^", "#D55E00", "-."),   # AllegrOCaml + CSplitMix
        ("o", "#0072B2", "--"),   # AllegrOCaml
    ]

    fig, axes = plt.subplots(2, 3, figsize=(7, 5.5), sharey=True)

    def plot_data(ax, data, title):
        for (method, values), (marker, color, linestyle) in zip(data.items(), styles):
            y_vals = [values[n] for n in n_values]
            ax.plot(n_values, y_vals, marker=marker, linestyle=linestyle,
                    linewidth=1.5, color=color, label=method)
        ax.set_title(title, fontsize=10)
        ax.set_yscale("log")
        ax.set_xscale("log")
        ax.set_xticks(n_values)
        ax.get_xaxis().set_major_formatter(ScalarFormatter())
        ax.tick_params(axis="both", which="major", labelsize=8)

    for ax, dataset in zip(axes.flat, plot_order):
        plot_data(ax, parsed_data[dataset], dataset)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=9, frameon=False)

    fig.tight_layout(rect=[0.02, 0.05, 1, 0.91])
    fig.supylabel('Run time (ns)', y=0.466, x=0.018, fontsize=10)
    fig.supxlabel('Size', y=0.04, fontsize=10)

    plt.show()

if __name__ == "__main__":
    main()
