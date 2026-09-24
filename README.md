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
| speeds | Fn = 0.10 (baseline), 0.25, 0.30, 0.316, 0.35, 0.40 |
| Reynolds number | 1.4 × 10⁶ to 5.7 × 10⁶ |
| solver | `interFoam`, VOF, local time stepping |
| turbulence | k-ω SST with wall functions |
| mesh | 268 k cells (medium); coarse and fine variants for the mesh study |
| domain | half ship on a symmetry plane, 1.25 L ahead, 2 L astern |

Full description of the numerics, and what the study deliberately does not
claim, is in [docs/METHOD.md](docs/METHOD.md).

## Results

See [out/RESULTS.md](out/RESULTS.md), which is regenerated from the case
directories rather than typed, and the figures in `out/`:

| Figure | What it shows |
|---|---|
| `cw_vs_michell.png` | computed wave resistance against Michell's theory across the Froude range |
| `convergence.png` | the force history of every case, and how settled it is |
| `mesh_study.png` | coefficients against cell size at Fn = 0.316 |
| `wave_cuts_*.png` | free-surface elevation along cuts parallel to the centreline |

## Why this hull, and why Michell

The Wigley form is thin, which is the assumption Michell's integral is built
on, and analytic, so there is no geometry uncertainty in the comparison. That
makes it the standard first validation case for a free-surface solver: if the
computed wave resistance does not follow the theory's humps and hollows, the
mesh or the numerics are wrong, and it is clear which way.

The ITTC-1957 line plays the same role for friction — an agreed correlation
line, not a fit to this computation.
