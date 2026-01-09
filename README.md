# Eval Pipeline

Scripts for parsing benchmark data and generating figures.

## Quick Start

From the Docker container (`/ff_artifact/artifact`):

```bash
# Analyze all precomputed data and generate all figures
./scripts/analyze_all.sh

# Or run fresh benchmarks and generate figures
./scripts/run_all.sh
```

## Directory Structure

```
eval/
├── 4.1_data_ocaml/{precomputed,fresh}/     # Raw OCaml benchmark output
├── 4.1_data_scala/{precomputed,fresh}/     # Raw Scala benchmark output (CSV)
├── 4.2_data/{precomputed,fresh}/
│   ├── bst-experiments/                    # BST mutation testing data
│   └── stlc-experiments/                   # STLC mutation testing data
├── parsed_4.1_data_ocaml/{precomputed,fresh}/  # Parsed OCaml JSON
├── parsed_4.1_data_scala/{precomputed,fresh}/  # Parsed Scala JSON
├── parsed_4.2_data/{precomputed,fresh}/    # Parsed Etna data
│   ├── parsed/                             # Initial parse output
│   ├── cleaned/                            # After removing outliers
│   └── speedups/                           # Final speedup calculations
├── figures/{precomputed,fresh}/            # Generated figures
├── parsers/                                # Parsing scripts
├── etna_data_processing/                   # Etna-specific processing
└── figure_scripts/                         # Figure generation scripts
```

## Available Scripts

### Wrapper Scripts (run from `/ff_artifact/artifact`)

| Script | Description |
|--------|-------------|
| `./scripts/run_all.sh` | Run ALL benchmarks and generate fresh figures |
| `./scripts/analyze_all.sh` | Analyze ALL precomputed data |
| `./scripts/run_ocaml.sh` | Run OCaml benchmarks only |
| `./scripts/run_scala.sh` | Run Scala benchmarks only |
| `./scripts/run_etna.sh` | Run Etna benchmarks only |
| `./scripts/analyze_ocaml.sh` | Analyze precomputed OCaml data |
| `./scripts/analyze_scala.sh` | Analyze precomputed Scala data |
| `./scripts/analyze_etna.sh` | Analyze precomputed Etna data |

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

## Etna Benchmark Pipeline (Figures 17 & 18)

Full pipeline from raw data to figures:

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

# 4. Generate figures
python3 figure_scripts/f17.py --source precomputed  # Geometric mean speedups
python3 figure_scripts/f18.py --source precomputed  # Box plots
```

Output:
- `figures/precomputed/fig17.png` - Geometric mean speedup bar charts
- `figures/precomputed/fig18.png` - Speedup distribution box plots

## Hardcoded Data Figure

This figure uses hardcoded data and doesn't require parsing:

- `f15.py` - Speedup correlation scatter plots

```bash
python3 figure_scripts/f15.py
```

## Common Options

All parsing and figure scripts support:
- `--source precomputed` - Use precomputed benchmark data
- `--source fresh` - Use freshly generated benchmark data
- `-o <path>` - Custom output path (figure scripts only)

## Figure Summary

| Figure | Description | Data Source |
|--------|-------------|-------------|
| Fig 14 | OCaml benchmark timing comparison | OCaml benchmarks |
| Fig 15 | Speedup correlation scatter plots | Hardcoded |
| Fig 16 | Scala benchmark timing comparison | Scala/JMH benchmarks |
| Fig 17 | Geometric mean speedup bar charts | Etna mutation testing |
| Fig 18 | Speedup distribution box plots | Etna mutation testing |
