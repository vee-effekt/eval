import json
import argparse

def clean_json(input_file, cleaned_output, removed_output):
    with open(input_file, 'r') as f:
        data = json.load(f)

    removed_data = {}

    strategy_prefixes = ["baseType", "baseBespoke", "baseBespokesingle"]

    for mutant, properties in data.items():
        for prop, values in properties.items():
            seeds_to_remove = set()
            for key, value in list(values.items()):
                if value is not None and any(key.startswith(prefix + "_") for prefix in strategy_prefixes) and value <= 0.0005:
                    seed = key.split("_")[1]
                    seeds_to_remove.add(seed)
                    removed_data.setdefault(mutant, {}).setdefault(prop, {})[key] = value
                    del values[key]

            # Remove corresponding staged versions
            for seed in seeds_to_remove:
                for prefix in strategy_prefixes:
                    base_key = f"{prefix}_{seed}"
                    if base_key in removed_data.get(mutant, {}).get(prop, {}):
                        for suffix in ["staged", "stagedc", "stagedcsr"]:
                            key_to_remove = f"{prefix}{suffix}_{seed}"
                            if key_to_remove in values:
                                removed_data[mutant][prop][key_to_remove] = values[key_to_remove]
                                del values[key_to_remove]

            # Remove entries where all 4 variants are 60.0
            to_remove = set()
            for seed in list(values.keys()):
                if any(seed.startswith(prefix + "_") for prefix in strategy_prefixes):
                    base_seed = seed.split("_")[1]

                    base_variants = {
                        "baseType": [
                            f"baseType_{base_seed}",
                            f"baseTypestaged_{base_seed}",
                            f"baseTypestagedc_{base_seed}",
                            f"baseTypestagedcsr_{base_seed}",
                        ],
                        "baseBespoke": [
                            f"baseBespoke_{base_seed}",
                            f"baseBespokestaged_{base_seed}",
                            f"baseBespokestagedc_{base_seed}",
                            f"baseBespokestagedcsr_{base_seed}",
                        ],
                        "baseBespokesingle": [
                            f"baseBespokesingle_{base_seed}",
                            f"baseBespokesinglestaged_{base_seed}",
                            f"baseBespokesinglestagedc_{base_seed}",
                            f"baseBespokesinglestagedcsr_{base_seed}",
                        ],
                    }

                    for variants in base_variants.values():
                        if all(values.get(var, -1) == 60.0 for var in variants):
                            to_remove.update(variants)

            for key in to_remove:
                if key in values:
                    removed_data.setdefault(mutant, {}).setdefault(prop, {})[key] = values[key]
                    del values[key]

    with open(cleaned_output, 'w') as f:
        json.dump(data, f, indent=2)

    with open(removed_output, 'w') as f:
        json.dump(removed_data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Clean JSON and extract removed items.")
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument("--output", required=True, help="Path to write cleaned JSON")
    parser.add_argument("--filtered", required=True, help="Path to write removed entries")
    args = parser.parse_args()

    clean_json(args.input, args.output, args.filtered)

if __name__ == "__main__":
    main()
