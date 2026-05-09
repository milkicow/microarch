import numpy as np
import matplotlib.pyplot as plt


def main():
    def eff_power(perf):
        return (perf * (perf + 0.2) ** 2) / 1.44

    def perf_power(perf):
        return (4 * (perf / 2) * ((perf / 2) + 0.2) ** 2) / 1.44

    eff_start = 0.8
    eff_end = 1.8

    perf_start = 1.6
    perf_end = 3.6

    perf_eff = np.linspace(eff_start, eff_end, 500)
    perf_perf = np.linspace(perf_start, perf_end, 500)

    power_eff = eff_power(perf_eff)
    power_perf = perf_power(perf_perf)

    perf_common = np.linspace(min(eff_start, perf_start), max(eff_end, perf_end), 500)
    optimal_power = []

    for p in perf_common:
        eff_available = eff_start <= p <= eff_end
        power_available = perf_start <= p <= perf_end

        pe_power = eff_power(p) if eff_available else np.inf
        pp_power = perf_power(p) if power_available else np.inf

        optimal_power.append(min(pe_power, pp_power))

    optimal_power = np.array(optimal_power)

    plt.figure(figsize=(12, 8))

    plt.plot(
        perf_eff,
        power_eff,
        color="green",
        linewidth=2,
        label="Efficient core Power(Perf)",
    )
    plt.plot(
        perf_perf,
        power_perf,
        color="red",
        linewidth=2,
        label="Performance core Power(Perf)",
    )
    plt.plot(
        perf_common,
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

    plt.axvspan(eff_start, eff_end, alpha=0.08, color="green")
    plt.axvspan(perf_start, perf_end, alpha=0.08, color="red")

    plt.tight_layout()

    plt.savefig("power_perf.png", dpi=300)


if __name__ == "__main__":
    main()
