import json
import argparse
from collections import defaultdict

# Define the strategy keys per workload
WORKLOAD_KEYS = {
    "type": (
        "baseType", [
            "baseType", "baseTypestaged", "baseTypestagedc", "baseTypestagedcsr"
        ]
    ),
    "bespoke": (
        "baseBespoke", [
            "baseBespoke", "baseBespokestaged", "baseBespokestagedc", "baseBespokestagedcsr"
        ]
    ),
    "bespokesingle": (
        "baseBespokesingle", [
            "baseBespokesingle", "baseBespokesinglestaged", "baseBespokesinglestagedc", "baseBespokesinglestagedcsr"
        ]
    )
}

def compute_speedup(data, workload):
    baseline_key, strategy_keys = WORKLOAD_KEYS[workload]
    speedup_data = defaultdict(lambda: defaultdict(dict))

    for mutant, properties in data.items():
        for prop, values in properties.items():
            per_seed_values = defaultdict(dict)

            for key, value in values.items():
                *field_name_parts, seed = key.split("_")
                field_name = "_".join(field_name_parts)
                per_seed_values[seed][field_name] = value

            for seed, timings in per_seed_values.items():
                base_time = timings.get(baseline_key)
                if base_time is None:
                    continue

                speedup_data[mutant][prop][seed] = {
                    k: base_time / timings[k]
                    for k in strategy_keys
                    if k in timings and timings[k] is not None
                }

                # Assert base key always maps to speedup 1.0
                if baseline_key in speedup_data[mutant][prop][seed] and speedup_data[mutant][prop][seed][baseline_key] != 1.0:
                    raise ValueError(f"Incorrect base speedup for {baseline_key} seed {seed} in {mutant} -> {prop}")

    return speedup_data

def main():
    parser = argparse.ArgumentParser(description="Compute speedups by workload.")
    parser.add_argument("--input", help="Input JSON file with timing data")
    parser.add_argument("--output", help="Output JSON file for speedup results")
    parser.add_argument("--workload", choices=["type", "bespoke", "bespokesingle"], required=True,
                        help="Workload group (required)")

    args = parser.parse_args()

    with open(args.input, "r") as file:
        data = json.load(file)

    result = compute_speedup(data, args.workload)

    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Speedup results saved to {args.output}")

if __name__ == "__main__":
    main()
