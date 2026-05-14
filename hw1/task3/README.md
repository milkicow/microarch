# Partitioned vs Monolithic Instruction Queue on Neoverse V2

## Setup

- **Simulator**: gem5 v25.1, SE mode, ARM ISA
- **CPU model**: Neoverse V2 (`NeoverseV2` / `NeoverseV2Monolithic`)
- **Benchmarks**: GAP Benchmark Suite (GAPBS) — BC, BFS, CC, PR, SSSP, TC
- **Input graph**: Kronecker, scale 10 (`-g 10 -n 1`)
- **Compile flags**: `aarch64-linux-gnu-g++ -std=c++11 -O1 -Wall -static`, `SERIAL=1`
- **Config script**: `configs/example/arm/fdp_neoverse_v2.py`

---

## IQ Configurations

### Partitioned - baseline (9 IQs)

| IQ  | Entries | Function unit pool           |
|-----|---------|------------------------------|
| IQ0 | 22      | Simple Int ×2 (ALU+branch)   |
| IQ1 | 22      | Simple Int ×2 (ALU+branch)   |
| IQ2 | 22      | Complex Int ×1 (MUL/DIV)     |
| IQ3 | 22      | Complex Int ×1 (MUL/DIV)     |
| IQ4 | 28      | FP/SIMD ×2                   |
| IQ5 | 28      | FP/SIMD ×2                   |
| IQ6 | 16      | Load ×1                      |
| IQ7 | 16      | Load ×1 + Store ×1           |
| IQ8 | 16      | Load ×1 + Store ×1           |
| **Total** | **192** |                         |

### Monolithic (1 IQ)

| IQ  | Entries | Function unit pool                                          |
|-----|---------|-------------------------------------------------------------|
| IQ0 | 192     | Simple Int ×4, Complex Int ×2, FP ×4, Load ×3, Store ×2   |

---

### Run commands

```bash
./build/ARM/gem5.opt --outdir=results/partitioned/<bench> \
    configs/example/arm/fdp_neoverse_v2.py \
    --binary gapbs/<bench> --app-args "-g 10 -n 1"
```

```bash
./build/ARM/gem5.opt --outdir=results/monolithic/<bench> \
    configs/example/arm/fdp_neoverse_v2.py \
    --binary gapbs/<bench> --app-args "-g 10 -n 1" \
    --monolithic-iq
```
---

## Results

### IPC comparison

| Benchmark | Partitioned IQ | Monolithic IQ | Δ IPC  |
|-----------|---------------|---------------|--------|
| BC        | 1.4238        | 1.2087        | −15.1% |
| BFS       | 1.4321        | 1.1924        | −16.7% |
| CC        | 1.3487        | 1.1657        | −13.6% |
| PR        | 1.5047        | 1.2746        | −15.3% |
| SSSP      | 1.4914        | 1.2589        | −15.6% |
| TC        | 1.2126        | 1.0303        | −15.0% |

**The monolithic IQ is 15–16.7% slower across all benchmarks.**

---

## Analysis

On monolithic instruction queue compared to partitioned:

- `numIssuedDist::0` is higher: more cycles where no instructions are sent to execution units at all
- `numIssuedDist::mean` is lower: on average fewer instructions issue per cycle

This happens because in a single large queue all instruction types compete for the same issue slots. Each instruction type requires its specific FU — loads need load units, integers need ALUs, etc. When multiple long-latency operations (e.g. a load with cache miss and a multiply) are executing simultaneously, instructions of different types are all waiting for their operands at once. So no instruction ready — producing a zero-issue cycle. With partitioned IQs each type has its own independent issue slot, so stall in one type does not affect others — the probability of a fully empty cycle is much lower.

The extra zero-issue cycles trigger a stall cascade:

```
slower issue →
  instructions accumulate in the ROB (>20* more ROB-full events) →
        all front-end stalls
```
