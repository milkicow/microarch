import re
from pathlib import Path
from math import prod

import matplotlib.pyplot as plt
import numpy as np

def parse_log(path):
    ipc = mpki = None
    for line in open(path):
        m = re.search(r"Simulation complete.*cumulative IPC:\s*([\d.]+)", line)
        if m:
            ipc = float(m.group(1))
        m = re.search(r"Branch Prediction Accuracy:.*MPKI:\s*([\d.]+)", line)
        if m:
            mpki = float(m.group(1))
    return ipc, mpki

def gmean(values):
    values = [v for v in values if v and v > 0]
    return prod(values) ** (1 / len(values)) if values else 0

def main():
    RESULTS_DIR = Path(__file__).parent / "results"
    PREDICTORS = sorted(d.name for d in RESULTS_DIR.iterdir() if d.is_dir())

    data = {}
    all_traces = set()
    for predictor in PREDICTORS:
        data[predictor] = {}
        for log in sorted((RESULTS_DIR / predictor).glob("*.log")):
            trace = log.stem.replace(".champsimtrace", "")
            ipc, mpki = parse_log(log)
            if ipc and mpki:
                data[predictor][trace] = (ipc, mpki)
                all_traces.add(trace)

    traces = sorted(all_traces)
    x = np.arange(len(traces))
    width = 0.8 / len(PREDICTORS)
    colors = plt.cm.tab10.colors

    print(f"{'Trace':<40}", end="")
    for p in PREDICTORS:
        print(f"{p:>20}", end="")
    print()
    print("-" * (40 + 20 * len(PREDICTORS)))

    for idx, label in [(0, "IPC"), (1, "MPKI")]:
        print(f"\n{label}")
        for trace in traces:
            print(f"  {trace:<38}", end="")
            for p in PREDICTORS:
                val = data[p].get(trace, (None, None))[idx]
                print(f"{val:>20.3f}" if val else f"{'N/A':>20}", end="")
            print()
        print(f"  {'GMEAN':<38}", end="")
        for p in PREDICTORS:
            vals = [data[p].get(t, (None, None))[idx] for t in traces]
            print(f"{gmean(vals):>20.3f}", end="")
        print()

    _, ax = plt.subplots(figsize=(16, 6))
    for i, (p, color) in enumerate(zip(PREDICTORS, colors)):
        vals = [data[p].get(t, (None, None))[0] or 0 for t in traces]
        gm = gmean(vals)
        ax.bar(x + i * width, vals, width, label=f"{p} (gmean={gm:.3f})", color=color)

    ax.set_xticks(x + width * (len(PREDICTORS) - 1) / 2)
    ax.set_xticklabels([t.split("-")[0] for t in traces], rotation=45, ha="right")
    ax.set_ylabel("IPC")
    ax.set_title("IPC per trace")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "ipc.png", dpi=300)
    print(f"\nSaved: {RESULTS_DIR / 'ipc.png'}")

    _, ax = plt.subplots(figsize=(16, 6))
    for i, (p, color) in enumerate(zip(PREDICTORS, colors)):
        vals = [data[p].get(t, (None, None))[1] or 0 for t in traces]
        gm = gmean(vals)
        ax.bar(x + i * width, vals, width, label=f"{p} (gmean={gm:.3f})", color=color)

    ax.set_xticks(x + width * (len(PREDICTORS) - 1) / 2)
    ax.set_xticklabels([t.split("-")[0] for t in traces], rotation=45, ha="right")
    ax.set_ylabel("MPKI")
    ax.set_title("MPKI per trace")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "mpki.png", dpi=300)
    print(f"Saved: {RESULTS_DIR / 'mpki.png'}")

if __name__ == "__main__":
    main()
