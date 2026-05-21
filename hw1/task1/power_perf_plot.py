import numpy as np
import matplotlib.pyplot as plt


def main():
    def eff_power(perf):
        part1 = perf / 1.44
        part2 = (perf * (perf + 0.2) ** 2) / 1.44
        return np.where(perf < 0.8, part1, part2)

    def perf_power(perf):
        part1 = 2 * perf / 1.44
        part2 = (4 * (perf / 2) * ((perf / 2) + 0.2) ** 2) / 1.44
        return np.where(perf < 1.6, part1, part2)

    start = 0.3
    end = 3.0

    perf = np.linspace(start, end, 500)

    power_eff = eff_power(perf)
    power_perf = perf_power(perf)

    optimal_power = []

    perf_intersection = 0
    for p in perf:
        optimal_power.append(min(eff_power(p), perf_power(p)))
        if eff_power(p) < perf_power(p):
            perf_intersection = p

    power_intersection = eff_power(perf_intersection)
    optimal_power = np.array(optimal_power)

    plt.figure(figsize=(12, 8))

    plt.plot(
        perf,
        power_eff,
        color="green",
        linewidth=2,
        label="Efficient core Power(Perf)",
    )
    plt.plot(perf_intersection, power_intersection, marker='o', color='blue', markersize=8, label='Core switch')

    plt.plot(
        perf,
        power_perf,
        color="red",
        linewidth=2,
        label="Performance core Power(Perf)",
    )
    plt.plot(
        perf,
        optimal_power,
        "--",
        color="blue",
        linewidth=2,
        alpha=0.5,
        label="Optimal Power(Perf)",
    )

    plt.xlabel("Performance")
    plt.ylabel("Power")
    plt.title("Power(Performance)")

    plt.grid(True)
    plt.legend()

    plt.axvspan(start, perf_intersection, alpha=0.08, color="green")
    plt.axvspan(perf_intersection, end, alpha=0.08, color="red")

    plt.tight_layout()

    plt.savefig("power_perf.png", dpi=300)


if __name__ == "__main__":
    main()
