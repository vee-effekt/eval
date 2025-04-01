import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_context("notebook")

file_paths = [
    "/Users/lapwing/Desktop/eval/cleaned_data/speedup_results_bespoke_bst_30.json",
    "/Users/lapwing/Desktop/eval/cleaned_data/speedup_results_bespokesingle_bst_30.json",
    "/Users/lapwing/Desktop/eval/cleaned_data/speedup_results_type_bst_30.json",
    "/Users/lapwing/Desktop/eval/cleaned_data/speedup_results_bespoke_stlc_30.json",
    "/Users/lapwing/Desktop/eval/cleaned_data/speedup_results_type_stlc_30.json",
]  

workload_names = [
    "BST (Repeated Insert)",
    "BST (Single-Pass)",
    "BST (Type-Derived)",
    "STLC",
    "STLC (Type-Derived)"
]

swarm_enabled = [
    {"AOC": False, "AOC + CSM": True},  # Workload 1: Show CSR swarm only
    {"AOC": True, "AOC + CSM": True},  # Workload 2: Show both swarms
    {"AOC": False, "AOC + CSM": True},  # Workload 3: Show CSR swarm only
    {"AOC": True, "AOC + CSM": True},  # Workload 4: Show both swarms
    {"AOC": False, "AOC + CSM": False},  # Workload 5: Show no swarms
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

custom_palette = ["#0072B2", "#D55E00"]  # Blue for "AOC", Orange for "AOC + CSM"

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

    if not isinstance(data, dict):
        print(f"Unexpected JSON format in {file_path}: Expected a dictionary but got {type(data)}")
        continue

    for condition in data.values():
        if not isinstance(condition, dict):
            continue

        for property_data in condition.values():
            if not isinstance(property_data, dict):
                continue

            for seed_data in property_data.values():
                if not isinstance(seed_data, dict):
                    continue

                for old_name, new_name in category_mapping.items():
                    if old_name in seed_data:
                        values[new_name].append(seed_data[old_name])

    for category, vals in values.items():
        print(f"  {category}: {len(vals)} values")

    if all(len(vals) == 0 for vals in values.values()):
        print(f"Skipping {file_path}: No valid data found.")
        continue

    sns.boxplot(data=[values[cat] for cat in category_order], palette=custom_palette, showfliers=False, ax=ax)

    for i, cat in enumerate(category_order):
        if swarm_enabled[idx][cat]:
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
    ax.set_title(workload_names[idx], fontsize=16)

    ax.set_ylim(0, 10)
    ax.set_yticks(range(0, 11))

def format_y_ticks(x, _):
    return f"{int(x)}X"

for ax in axes:
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_y_ticks))

plt.tight_layout(rect=[0.01, 0.01, 1, 1])

fig.supylabel('Speedup', x=0.000001, fontsize=16)
plt.show()
