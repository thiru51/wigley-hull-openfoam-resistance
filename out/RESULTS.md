# Results — generated 2026-09-25

Wigley hull, L = 3.0 m, B = 0.3 m, T = 0.1875 m, fresh water at 15 °C.
Coefficients use the wetted surface of the half hull; the domain is a half model.

| case | Fn | cells | iters | cells/λ | Ct×10³ | Cp×10³ | Cf×10³ | ITTC-57 Cf×10³ | Michell Cw×10³ | Cp/Cw | drift | oscillation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fn0250 | 0.250 | 268,322 | 3000 | 11.8 | 2.701 | 0.968 | 1.733 | 3.588 | 1.063 | 0.91 | +5 % | 54 % |
| fn0316 | 0.316 | 268,322 | 3000 | 18.8 | 3.048 | 1.410 | 1.638 | 3.433 | 1.830 | 0.77 | -53 % | 39 % |
| fn0350 | 0.350 | 268,322 | 1730 | 23.1 | 4.637 | 2.906 | 1.731 | 3.369 | 1.247 | 2.33 | -27 % | 12 % |
| fn0400 | 0.400 | 268,322 | 1740 | 30.2 | 4.854 | 3.191 | 1.664 | 3.288 | 2.733 | 1.17 | -6 % | 2 % |

`Cp/Cw` compares the computed pressure resistance with Michell's thin-ship wave
resistance. Two effects pull it in opposite directions: the computed pressure
force also carries viscous form drag, which Michell's inviscid theory has no
term for and which pushes the ratio above 1; while a mesh that cannot carry the
waves damps them, which pulls it below 1. The `cells/λ` column says which effect
should dominate each row -- ship CFD practice asks for 40 or more.

## At Fn = 0.316

- total resistance on the half hull: **2.996 N** (1.386 N pressure, 1.610 N viscous)
- Ct = 3.048 × 10⁻³, of which pressure 1.410 × 10⁻³
- Michell wave resistance at the same speed: Cw = 1.830 × 10⁻³
- ITTC-57 friction line at Re = 4.72e+06: Cf = 3.433 × 10⁻³

### Diagnostics

- y+ on the hull: min 1.9, max 736, mean 111 — no prism layers, so the friction is under-resolved and is reported beside the ITTC line rather than instead of it.
- far-field still-water level: -1.9 mm at 1200, -2.8 mm at 3000 — it should be zero; the drift is the leading defect in this setup.
- pressure force oscillation over the averaging window: 39 % of its mean, period roughly 900 iterations.
