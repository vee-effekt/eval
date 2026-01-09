# Eval Pipeline

Scripts for parsing benchmark data and generating figures.

## Directory Structure

```
eval/
├── 4.1_data_ocaml/{precomputed,fresh}/     # Raw OCaml benchmark output
├── 4.1_data_scala/{precomputed,fresh}/     # Raw Scala benchmark output (CSV)
├── 4.2_data/{precomputed,fresh}/           # Raw ETNA benchmark output
├── parsed_4.1_data_ocaml/{precomputed,fresh}/  # Parsed OCaml JSON
├── parsed_4.1_data_scala/{precomputed,fresh}/  # Parsed Scala JSON
├── parsed_4.2_data/{precomputed,fresh}/    # Parsed ETNA data
│   ├── parsed/                             # Initial parse output
│   ├── cleaned/                            # After removing outliers
│   └── speedups/                           # Final speedup calculations
├── figures/{precomputed,fresh}/            # Generated figures
├── parsers/                                # Parsing scripts
├── etna_data_processing/                   # ETNA-specific processing
└── figure_scripts/                         # Figure generation scripts
```

## OCaml Benchmark Pipeline (Figure 14)

```bash
# Parse raw data
python3 parsers/parse_results_ocaml.py --source precomputed

# Generate figure
python3 figure_scripts/f14.py --source precomputed
```

Output: `figures/precomputed/fig14.png`

## Scala Benchmark Pipeline (Figure 16)

```bash
# Parse raw data
python3 parsers/parse_results_scala_csv.py --source precomputed

# Generate figure
python3 figure_scripts/f16.py --source precomputed
```

Output: `figures/precomputed/fig16.png`

## ETNA Benchmark Pipeline (Figure 18)

Full pipeline from raw data to figure:

```bash
# 1. Parse raw data
python3 parsers/parse_etna_data.py --source precomputed --system BST
python3 parsers/parse_etna_data.py --source precomputed --system STLC

# 2. Clean data (remove <5ms and all-timeout entries)
python3 etna_data_processing/clean_under5ms_or_timeout.py --source precomputed --system BST
python3 etna_data_processing/clean_under5ms_or_timeout.py --source precomputed --system STLC

# 3. Calculate speedups
python3 etna_data_processing/calculate_speedups.py --source precomputed --system BST --workload type
python3 etna_data_processing/calculate_speedups.py --source precomputed --system BST --workload bespoke
python3 etna_data_processing/calculate_speedups.py --source precomputed --system BST --workload bespokesingle
python3 etna_data_processing/calculate_speedups.py --source precomputed --system STLC --workload type
python3 etna_data_processing/calculate_speedups.py --source precomputed --system STLC --workload bespoke

# 4. Generate figure
python3 figure_scripts/f18.py --source precomputed
```

Output: `figures/precomputed/fig18.png`

## Hardcoded Data Figures

These figures use hardcoded data and don't require parsing:

- `f15.py` - Speedup correlation scatter plots
- `f17.py` - AllegrOCaml speedup bar charts

```bash
python3 figure_scripts/f15.py
python3 figure_scripts/f17.py
```

## Common Options

All scripts support:
- `--source precomputed` - Use precomputed benchmark data
- `--source fresh` - Use freshly generated benchmark data
- `-o <path>` - Custom output path (figure scripts only)
