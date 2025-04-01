import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

parsed_data = {
    "BST (Type-Derived)": {
        "BQ": {10: 4400.79, 100: 47200.20, 1000: 449213.46, 10000: 11409773.29},
        "AllegrOCaml": {10: 3375.10, 100: 34186.67, 1000: 340126.31, 10000: 8800010.49},
        "AllegrOCaml + CSplitMix": {10: 615.75, 100: 6078.61, 1000: 77830.00, 10000: 5349017.53},
    },
    "BST (Repeated Insert)": {
        "BQ": {10: 3250.84, 100: 22028.50, 1000: 174848.57, 10000: 2184878.80},
        "AllegrOCaml": {10: 2658.55, 100: 18603.05, 1000: 150717.42, 10000: 1798695.09},
        "AllegrOCaml + CSplitMix": {10: 515.35, 100: 4150.16, 1000: 37292.05, 10000: 570619.28},
    },
    "BST (Single-Pass)": {
        "BQ": {10: 3567.34, 100: 30201.04, 1000: 224580.17, 10000: 2646695.68},
        "AllegrOCaml": {10: 1594.31, 100: 13574.49, 1000: 99675.74, 10000: 1191136.16},
        "AllegrOCaml + CSplitMix": {10: 393.99, 100: 3175.59, 1000: 22902.59, 10000: 269595.17},
    },
    "STLC (Type-Derived)": {
        "BQ": {10: 1075.38, 100: 6989.00, 1000: 72122.27, 10000: 4198493.60},
        "AllegrOCaml": {10: 602.99, 100: 3153.25, 1000: 41712.66, 10000: 1037925.18},
        "AllegrOCaml + CSplitMix": {10: 321.53, 100: 2412.61, 1000: 34571.98, 10000: 778437.15},
    },
    "STLC": {
        "BQ": {10: 2158.64, 100: 35510.83, 1000: 612699.75, 10000: 34902239.74},
        "AllegrOCaml": {10: 446.54, 100: 6776.14, 1000: 107280.73, 10000: 8503176.17},
        "AllegrOCaml + CSplitMix": {10: 405.09, 100: 6203.26, 1000: 73543.40, 10000: 6292880.05},
    },
    "Bool List": {
        "BQ": {10: 327.21, 100: 3924.84, 1000: 53253.71, 10000: 1295748.16},
        "AllegrOCaml": {10: 83.61, 100: 1415.84, 1000: 14418.78, 10000: 173523.72},
        "AllegrOCaml + CSplitMix": {10: 83.69, 100: 1415.36, 1000: 14370.66, 10000: 171112.66},
    },
}

plot_order = list(parsed_data.keys())
n_values = [10, 100, 1000, 10000]
styles = [
    ("s", "#c90076", ":"),    # BQ
    ("o", "#0072B2", "--"),   # AllegrOCaml
    ("^", "#D55E00", "-."),   # AllegrOCaml + CSplitMix
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
