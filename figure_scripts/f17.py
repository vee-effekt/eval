import matplotlib.pyplot as plt
import numpy as np

datasets = {
    "BST (Repeated Insert)": {
        "AllegrOCaml": 1.1695746950606363,
        "AllegrOCaml + CSM": 2.6711125604202617
    },
    "BST (Single-Pass)": {
        "AllegrOCaml": 2.0746104652292834,
        "AllegrOCaml + CSM": 3.893737103304992
    },
    "BST (Type-Derived)": {
        "AllegrOCaml": 1.264428857447493,
        "AllegrOCaml + CSM": 3.4140967241269244
    },
    "STLC": {
        "AllegrOCaml": 2.649940339746985,
        "AllegrOCaml + CSM": 3.3970157118245052
    },
    "STLC (Type-Derived)": {
        "AllegrOCaml": 1.5777481512565767,
        "AllegrOCaml + CSM": 2.371727192953227
    }
}

colors = ["#0072B2", "#D55E00"]  # AllegrOCaml (blue) and AllegrOCaml + CSM (orange)

fig, axes = plt.subplots(1, 5, figsize=(12, 3.5), sharey=True)

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
plt.show()
