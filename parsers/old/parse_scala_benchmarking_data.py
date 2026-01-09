import re
import json
import argparse
from collections import defaultdict

# Map raw variant names to desired labels
variant_rename = {
    "": "SC",
    "Staged": "ScAllegro"
}

def parse_benchmark_line(line):
    match = re.search(
        r'GenBm\.generate([A-Za-z]+?)(Staged)?(\d+)\s+avgt\s+\d+\s+([0-9.]+)\s+±\s+[0-9.]+\s+ns/op',
        line
    )
    if match:
        benchmark = match.group(1)
        variant_raw = match.group(2) or ""
        size = int(match.group(3))
        score = float(match.group(4))
        variant = variant_rename[variant_raw]
        return benchmark, variant, size, round(score, 2)
    return None

def parse_file(filepath):
    result = defaultdict(lambda: defaultdict(dict))
    with open(filepath, 'r') as f:
        for line in f:
            if "[info]" in line:
                parsed = parse_benchmark_line(line)
                if parsed:
                    bench, variant, size, score = parsed
                    result[bench][variant][size] = score
    return result

def main():
    parser = argparse.ArgumentParser(description="Parse benchmark output to JSON.")
    parser.add_argument("input_file", help="Path to the benchmark output text file")
    parser.add_argument("output_file", help="Path to the output JSON file")
    args = parser.parse_args()

    parsed = parse_file(args.input_file)

    with open(args.output_file, 'w') as f:
        json.dump(parsed, f, indent=4)

    print(f"Wrote parsed benchmark data to {args.output_file}")

if __name__ == "__main__":
    main()
