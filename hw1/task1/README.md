# Heterogeneous Architecture Power Model

# Architecture Assumptions

| Property | Efficient Core | Performance Core |
|---|---|---|
| Capacitance coefficient `C` | `1` | `4` |
| IPC | `1` | `2` |
| Performance model | `Perf(f) = f` | `Perf(f) = 2f` |

# Power Model

$P = C U^2 f$

where:

- `C` — effective capacitance
- `U` — voltage
- `f` — frequency

---

# Voltage–Frequency Relation

Assume a linear dependency between voltage and frequency:

$f = kU + b$

Boundary conditions:

- when `f = 1`, `U = 1.2`
- when `f = 1.8`, `U = 2`

Substituting:

$1 = 1.2k + b$

$1.8 = 2k + b$

Solution:

$k = 1$

$b = -0.2$

Thus:

$f = U - 0.2$

$U = f + 0.2$

Frequency range:

$f \in [0.8, 1.8]$

---

# Efficient Core Power Function

Substitute:

$U = f + 0.2$

into:

$P = C U^2 f$

For efficient cores:

- $C = 1$
- $Perf = f$

Substitute and normalize: $Power = 1$ when $Perf = 1$, $C = 1$

Therefore:

$$Power_{Eff}(Perf)=\frac{Perf(Perf + 0.2)^2}{1.44}$$

$Perf \in [0.8, 1.8]$

---

# Performance Core Power Function

For performance cores:

- $C = 4$
- $Perf = 2f$ -> $f = \frac{Perf}{2}$

Therefore for normalized formula:

$$Power_{Perf}(Perf)=\frac{4 \cdot \frac{Perf}{2} \cdot \left(\frac{Perf}{2}+0.2\right)^2}{1.44}$$

$Perf \in [1.6, 3.6]$

---

# Power(Perf) plot

![Power(Perf) plot](power_perf.png)