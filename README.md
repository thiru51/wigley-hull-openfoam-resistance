# wigley-cfd — free-surface resistance of a Wigley hull in OpenFOAM

A ship resistance study run end to end from scripts: the case dictionaries are
generated, the mesh is built in three stages, `interFoam` solves the
free-surface flow at a series of Froude numbers, and the resulting resistance
is compared against **Michell's 1898 thin-ship theory** and the **ITTC-1957**
friction line.

The hull geometry comes from the companion project
[hullform](../hullform), which writes the same hull as a Rhino model and as
the watertight mesh used here — one definition of the ship, two uses.

```bash
python tools/gen_case.py --fn 0.316 --level medium --out cases/fn0316
bash   tools/run_case.sh cases/fn0316 10
python tools/postprocess.py      # coefficients from the force history
python tools/plots.py            # figures
python tools/report.py           # out/RESULTS.md, generated not typed
bash   tools/sweep.sh            # the whole Froude sweep and mesh study
```

## The case

| | |
|---|---|
| hull | Wigley parabolic, L = 3.0 m, B = 0.3 m, T = 0.1875 m |
| speeds | Fn = 0.25, 0.316, 0.35, 0.40 |
| Reynolds number | 3.7 × 10⁶ to 6.0 × 10⁶ |
| solver | `interFoam`, VOF, local time stepping |
| turbulence | k-ω SST with wall functions |
| mesh | 268 k cells (medium); coarse and fine variants for the mesh study |
| domain | half ship on a symmetry plane, 1.25 L ahead, 2 L astern |

Full description of the numerics, and what the study deliberately does not
claim, is in [docs/METHOD.md](docs/METHOD.md).

## Results

Five cases, all run to 3,000 LTS iterations and averaged over the second half.
Full table, with the convergence and mesh diagnostics, in
[out/RESULTS.md](out/RESULTS.md) — regenerated from the case directories
rather than typed.

| Fn | mesh | cells/λ | Cp × 10³ | Michell Cw × 10³ | Cp / Cw |
|---|---|---|---|---|---|
| 0.250 | 268 k | 11.8 | 0.97 | 1.06 | 0.91 |
| 0.316 | 59 k | 12.5 | 1.86 | 1.83 | 1.01 |
| 0.316 | 268 k | 18.8 | 1.41 | 1.83 | 0.77 |
| 0.350 | 268 k | 23.1 | 2.30 | 1.25 | 1.85 |
| 0.400 | 268 k | 30.2 | 2.95 | 2.73 | **1.08** |

**The best-resolved, best-converged case is the one to read.** At Fn = 0.400 —
30 cells per wavelength, force drift under 1 % across the averaging window —
the computed pressure resistance sits **8 % above** Michell's wave resistance,
which is the right side to be on: the computed force also carries viscous form
drag, and Michell's inviscid theory has no term for it.

**What the computation does not reproduce is the hump-and-hollow structure.**
Michell predicts a hump near Fn 0.30 and a hollow near 0.35, both of which are
interference effects between the bow and stern wave systems and so depend on
getting the wave *phase* right over a ship length. With 12–30 cells per
wavelength in the plane of the free surface — practice asks for 40 or more —
those features are smeared, and the computed curve rises smoothly through
them. The annotation on `cw_vs_michell.png` puts the resolution next to each
point, because that is the number that explains the disagreement.

The free surface itself is right: the plan view shows a Kelvin wave system
inside the expected 19.47° wedge, with bow and stern crests in the right
places and the transverse waves trailing astern.

### What the mesh study says

Between the 59 k and 268 k meshes at Fn = 0.316 the **total** changes by only
2 % — but the split does not: pressure falls by 24 % and friction rises by
46 % as the mesh refines. Agreement in a total can hide two errors cancelling,
which is the argument for reporting the components separately throughout.

### Friction, and what prism layers are worth

The sweep above has no prism layers on the hull, so its friction cannot be
trusted. One extra case at Fn = 0.400 adds three layers and says how much that
costs and buys:

| | cells | mean y⁺ | Cf × 10³ | fraction of ITTC-57 | Cp × 10³ | Ct × 10³ |
|---|---|---|---|---|---|---|
| no layers | 268 k | 109 | 1.60 | 48 % | 2.95 | 4.54 |
| 3 prism layers | 353 k | 12.7 | 2.66 | **81 %** | 3.12 | 5.79 |

Adding layers raises the computed friction from **48 % to 81 %** of the
ITTC-1957 line for 32 % more cells, and moves the pressure force by only 6 % —
which is the evidence for treating `Cp` as the reliable half of this
computation and `Cf` as the unreliable half.

The residual 19 % gap has a named cause: mean y⁺ lands at **12.7**, inside the
buffer layer, which is precisely where wall functions are least accurate. The
next step would be either thicker layers to push y⁺ above 30, or many more to
resolve down to y⁺ < 1.

### Figures

| Figure | What it shows |
|---|---|
| `cw_vs_michell.png` | computed wave resistance against Michell's theory, each point labelled with its wave resolution |
| `wave_pattern_*.png` | plan view of the free surface, with the Kelvin half-angle drawn on |
| `wave_cuts_*.png` | free-surface elevation along cuts parallel to the centreline |
| `convergence.png` | the force history of every case, and how settled it is |
| `mesh_study.png` | coefficients against cell size at Fn = 0.316 |

## Why this hull, and why Michell

The Wigley form is thin, which is the assumption Michell's integral is built
on, and analytic, so there is no geometry uncertainty in the comparison. That
makes it the standard first validation case for a free-surface solver: if the
computed wave resistance does not follow the theory's humps and hollows, the
mesh or the numerics are wrong, and it is clear which way.

The ITTC-1957 line plays the same role for friction — an agreed correlation
line, not a fit to this computation.
