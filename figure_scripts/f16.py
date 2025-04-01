import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

# Parsed benchmark results (same data)
parsed_data = {
    "Bool List": {
        "SC": {10: 3924.09, 100: 37357.92, 1000: 369547.06, 10000: 6090663.84},
        "ScAllegro": {10: 572.03, 100: 4654.39, 1000: 45080.30, 10000: 454101.87},
    },
    "BST (Single-Pass)": {
        "SC": {10: 3544.99, 100: 31701.00, 1000: 263711.61, 10000: 3602343.31},
        "ScAllegro": {10: 725.11, 100: 5566.75, 1000: 40537.46, 10000: 556590.22},
    },
    "STLC": {
        "SC": {10: 5210.40, 100: 43361.96, 1000: 335514.38, 10000: 5102299.93},
        "ScAllegro": {10: 959.08, 100: 7056.24, 1000: 43161.73, 10000: 526159.89},
    }
}

plot_order = list(parsed_data.keys())
n_values = [10, 100, 1000, 10000]

styles = {
    "SC": ("s", "#de3423", ":"),    
    "ScAllegro": ("o", "#23b6de", "--"),
}

fig, axes = plt.subplots(1, 3, figsize=(5.5, 2.25), sharey=True)

def plot_data(ax, data, title):
    for method, values in data.items():
        marker, color, linestyle = styles[method]
        y_vals = [values[n] for n in n_values]
        ax.plot(n_values, y_vals, marker=marker, linestyle=linestyle,
                linewidth=1.5, color=color, label=method)
    ax.set_title(title, fontsize=10)
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.set_xticks(n_values)
    ax.get_xaxis().set_major_formatter(ScalarFormatter())
    ax.tick_params(axis="both", which="major", labelsize=8)
    ax.set_box_aspect(1)

for ax, dataset in zip(axes, plot_order):
    plot_data(ax, parsed_data[dataset], dataset)

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=2, fontsize=9, frameon=False)

fig.tight_layout(rect=[0.02, 0.05, 1, 0.91])
fig.supylabel('Run time (ns)', y=0.45, x=0.04, fontsize=10)
fig.supxlabel('Size', fontsize=10)
plt.show()
