# Results — generated 2026-09-25

Wigley hull, L = 3.0 m, B = 0.3 m, T = 0.1875 m, fresh water at 15 °C.
Coefficients use the wetted surface of the half hull; the domain is a half model.

| case | Fn | cells | iters | cells/λ | Ct×10³ | Cp×10³ | Cf×10³ | ITTC-57 Cf×10³ | Michell Cw×10³ | Cp/Cw | drift | oscillation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fn0316_coarse | 0.316 | 59,507 | 3000 | 12.5 | 2.979 | 1.857 | 1.122 | 3.433 | 1.830 | 1.01 | -13 % | 22 % |
| fn0250 | 0.250 | 268,322 | 3000 | 11.8 | 2.701 | 0.968 | 1.733 | 3.588 | 1.063 | 0.91 | +5 % | 54 % |
| fn0300 | 0.300 | 268,322 | 3000 | 17.0 | 2.835 | 1.181 | 1.654 | 3.467 | 2.140 | 0.55 | -71 % | 53 % |
| fn0316 | 0.316 | 268,322 | 3000 | 18.8 | 3.048 | 1.410 | 1.638 | 3.433 | 1.830 | 0.77 | -53 % | 39 % |
| fn0350 | 0.350 | 268,322 | 3000 | 23.1 | 3.939 | 2.303 | 1.636 | 3.369 | 1.247 | 1.85 | -13 % | 11 % |
| fn0400 | 0.400 | 268,322 | 3000 | 30.2 | 4.542 | 2.947 | 1.595 | 3.288 | 2.733 | 1.08 | -0 % | 5 % |
| fn0400_layers | 0.400 | 353,132 | 3000 | 30.2 | 5.785 | 3.122 | 2.663 | 3.288 | 2.733 | 1.14 | +7 % | 6 % |

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
