import json

def clean_json(input_file, cleaned_output, removed_output):
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    removed_data = {}
    
    for mutant, properties in data.items():
        for prop, values in properties.items():
            seeds_to_remove = set()
            for key, value in list(values.items()):
                if (key.startswith("baseType_") or key.startswith("baseBespoke_") or key.startswith("baseBespokesingle_")) and value <= 0.0005:
                    seed = key.split("_")[1]
                    seeds_to_remove.add(seed)
                    removed_data.setdefault(mutant, {}).setdefault(prop, {})[key] = value
                    del values[key]
            
            # Remove corresponding staged, stagedc, stagedcsr, and ensure baseType variants are removed only if baseType is below threshold
            for seed in seeds_to_remove:
                for prefix in ["baseType", "baseBespoke", "baseBespokesingle"]:
                    base_key = f"{prefix}_{seed}"
                    if base_key in removed_data.get(mutant, {}).get(prop, {}):
                        for suffix in ["staged", "stagedc", "stagedcsr"]:
                            key_to_remove = f"{prefix}{suffix}_{seed}"
                            if key_to_remove in values:
                                removed_data[mutant][prop][key_to_remove] = values[key_to_remove]
                                del values[key_to_remove]
            
            # Remove entries where all 4 versions are 60.0
            to_remove = set()
            for seed in list(values.keys()):
                if seed.startswith("baseType_") or seed.startswith("baseBespoke_") or seed.startswith("baseBespokesingle_"):
                    base_seed = seed.split("_")[1]
                    base_variants_type = [
                        f"baseType_{base_seed}",
                        f"baseTypestaged_{base_seed}",
                        f"baseTypestagedc_{base_seed}",
                        f"baseTypestagedcsr_{base_seed}"
                    ]
                    base_variants_bespoke = [
                        f"baseBespoke_{base_seed}",
                        f"baseBespokestaged_{base_seed}",
                        f"baseBespokestagedc_{base_seed}",
                        f"baseBespokestagedcsr_{base_seed}"
                    ]
                    base_variants_singlebespoke = [
                        f"baseBespokesingle_{base_seed}",
                        f"baseBespokesinglestaged_{base_seed}",
                        f"baseBespokesinglestagedc_{base_seed}",
                        f"baseBespokesinglestagedcsr_{base_seed}"
                    ]
                    
                    if all(values.get(var, -1) == 60.0 for var in base_variants_type):
                        to_remove.update(base_variants_type)
                    if all(values.get(var, -1) == 60.0 for var in base_variants_bespoke):
                        to_remove.update(base_variants_bespoke)
                    if all(values.get(var, -1) == 60.0 for var in base_variants_singlebespoke):
                        to_remove.update(base_variants_singlebespoke)
            
            for key in to_remove:
                if key in values:
                    removed_data.setdefault(mutant, {}).setdefault(prop, {})[key] = values[key]
                    del values[key]
    
    with open(cleaned_output, 'w') as f:
        json.dump(data, f, indent=2)
    
    with open(removed_output, 'w') as f:
        json.dump(removed_data, f, indent=2)

clean_json('stlc_results_30.json', 'stlc_results_cleaned.json', 'filtered_tasks_stlc.json')
