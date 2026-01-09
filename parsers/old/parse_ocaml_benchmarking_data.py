import sys
import json
import re
from collections import defaultdict
from pathlib import Path

def parse_time_ns(s):
    """Convert a time string like '1_234.56ns' to a float."""
    if not s or s.strip() == '':
        return None
    s = s.replace('_', '').replace('ns', '')
    try:
        return float(s)
    except ValueError:
        return None

def parse_line_name(name):
    """
    Parse names like 'Group_structure_baseBespoke_Staged_SR:n=100'
    Keep only the components from the 3rd onward, and prefix with 'base'.
    If no extra parts exist, just return 'base'.

    Examples:
        'structure_baseBespoke'                  -> 'base'
        'structure_baseBespoke_Staged_SR'        -> 'base_Staged_SR'
        'structure_baseType_CSR'                 -> 'base_CSR'
        'structure_baseType_Staged_Super_SR_Foo' -> 'base_Staged_Super_SR_Foo'
    """
    match = re.match(r'(.+?)_(.+?):n=(\d+)', name)
    if not match:
        return None, None, None
    group, raw_variant, size = match.groups()

    parts = raw_variant.split('_')

    if len(parts) <= 1:
        variant = "base"
    else:
        suffix = '_'.join(parts[1:])
        variant = f"base_{suffix}"

    return group.strip(), variant.strip(), int(size)

def main():
    if len(sys.argv) != 3:
        print("Usage: python parse_bench.py <input_file> <output_file>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    result = defaultdict(lambda: defaultdict(dict))

    with input_path.open() as f:
        for line in f:
            if not line.startswith("│ "):
                continue
            parts = [col.strip() for col in line.strip('│ \n').split('│')]
            if len(parts) < 2:
                continue

            name, time_str = parts[0], parts[1]
            group, variant, size = parse_line_name(name)
            if not group or not variant or size is None:
                continue

            time_val = parse_time_ns(time_str)
            if time_val is not None:
                result[group][variant][size] = time_val

    # Extract top-level name from filename
    top_key = input_path.stem

    for group, group_data in sorted(result.items()):
        sorted_result = {
            top_key: {
                variant: {
                    size: variant_data[size]
                    for size in sorted(variant_data)
                }
                for variant, variant_data in sorted(group_data.items())
            }
        }

        with output_path.open("w") as out:
            json.dump(sorted_result, out, indent=4)

        print(f"Wrote output to {output_path}")
        break  # Only process one group, since we're wrapping it under the filename


if __name__ == "__main__":
    main()
