import re
from pathlib import Path
from math import prod

import matplotlib.pyplot as plt
import numpy as np

def parse_log(path):
    text = path.read_text()
    ipc = miss_rate = None

    m = re.search(r"CPU 0 cumulative IPC:\s+([\d.]+)", text)
    if m:
        ipc = float(m.group(1))

    m = re.search(r"cpu0->cpu0_L2C TOTAL\s+ACCESS:\s+(\d+)\s+HIT:\s+\d+\s+MISS:\s+(\d+)", text)
    if m:
        acc, miss = int(m.group(1)), int(m.group(2))
        miss_rate = miss / acc if acc > 0 else 0.0

    return ipc, miss_rate


def gmean(values):
    values = [v for v in values if v and v > 0]
    return prod(values) ** (1 / len(values)) if values else 0


def main():
    RESULTS_DIR = Path(__file__).parent / "results"
    POLICIES = ["lru", "pseudo_lru", "srrip", "lru_lip", "lru_bip"]
    LABELS = {
        "lru": "LRU",
        "pseudo_lru": "Pseudo-LRU",
        "srrip": "SRRIP",
        "lru_lip": "LRU+LIP",
        "lru_bip": "LRU+BIP",
    }

    data = {}
    all_traces = set()
    for policy in POLICIES:
        data[policy] = {}
        for log in sorted((RESULTS_DIR / policy).glob("*.log")):
            trace = log.stem.replace(".champsimtrace", "")
            ipc, miss_rate = parse_log(log)
            if ipc is not None:
                data[policy][trace] = (ipc, miss_rate)
                all_traces.add(trace)

    traces = sorted(all_traces)
    x = np.arange(len(traces))
    width = 0.8 / len(POLICIES)
    colors = plt.cm.tab10.colors

    print(f"{'Trace':<40}", end="")
    for p in POLICIES:
        print(f"{LABELS[p]:>15}", end="")
    print()
    print("-" * (40 + 15 * len(POLICIES)))

    for idx, label in [(0, "IPC"), (1, "L2C Miss Rate")]:
        print(f"\n{label}")
        for trace in traces:
            print(f"  {trace:<38}", end="")
            for p in POLICIES:
                val = data[p].get(trace, (None, None))[idx]
                print(f"{val:>15.4f}" if val is not None else f"{'N/A':>15}", end="")
            print()
        print(f"  {'GMEAN':<38}", end="")
        for p in POLICIES:
            vals = [data[p].get(t, (None, None))[idx] for t in traces]
            print(f"{gmean(vals):>15.4f}", end="")
        print()

    _, ax = plt.subplots(figsize=(16, 6))
    for i, (p, color) in enumerate(zip(POLICIES, colors)):
        vals = [data[p].get(t, (None, None))[0] or 0 for t in traces]
        gm = gmean(vals)
        ax.bar(x + i * width, vals, width, label=f"{LABELS[p]} (gmean={gm:.3f})", color=color)

    ax.set_xticks(x + width * (len(POLICIES) - 1) / 2)
    ax.set_xticklabels([t.split("-")[0] for t in traces], rotation=45, ha="right")
    ax.set_ylabel("IPC")
    ax.set_title("IPC per trace")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "ipc.png", dpi=300)
    print(f"\nSaved: {RESULTS_DIR / 'ipc.png'}")

    _, ax = plt.subplots(figsize=(16, 6))
    for i, (p, color) in enumerate(zip(POLICIES, colors)):
        vals = [data[p].get(t, (None, None))[1] or 0 for t in traces]
        gm = gmean(vals)
        ax.bar(x + i * width, vals, width, label=f"{LABELS[p]} (gmean={gm:.4f})", color=color)

    ax.set_xticks(x + width * (len(POLICIES) - 1) / 2)
    ax.set_xticklabels([t.split("-")[0] for t in traces], rotation=45, ha="right")
    ax.set_ylabel("L2C Demand Miss Rate")
    ax.set_title("L2C demand miss rate per trace")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "miss_rate.png", dpi=300)
    print(f"Saved: {RESULTS_DIR / 'miss_rate.png'}")


if __name__ == "__main__":
    main()
