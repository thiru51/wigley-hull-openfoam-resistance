#!/usr/bin/env python
"""Figures: force convergence, the Cw curve against Michell, the mesh study,
and wave cuts taken from the captured free surface.

    python tools/plots.py
"""

from __future__ import annotations

import argparse
import glob
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import michell
import postprocess as pp


def convergence(cases, out):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for case in cases:
        data = pp.read_forces(case)
        if data is None:
            continue
        it, tot, pres, visc = data
        ax.plot(it, tot, lw=1, label=os.path.basename(case))
    ax.set_xlabel("LTS iteration")
    ax.set_ylabel("total x-force on the half hull, N")
    ax.set_title("Convergence of the resistance")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    p = os.path.join(out, "convergence.png")
    fig.savefig(p, dpi=160)
    plt.close(fig)
    return p


def cw_curve(rows, out, level="medium"):
    """CFD pressure-resistance coefficient against Michell's wave resistance."""
    all_rows = rows
    rows = [r for r in rows if r["level"] == level]
    rows.sort(key=lambda r: r["fn"])
    fns = np.array([r["fn"] for r in rows])
    cp = np.array([r["Cp"] for r in rows])
    ct = np.array([r["Ct"] for r in rows])
    cf_ittc = np.array([r["Cf_ittc57"] for r in rows])

    fn_fine = np.arange(0.20, 0.431, 0.01)
    cw_m, S = michell.cw_curve(fn_fine)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(fn_fine, 1e3 * cw_m, "-", color="crimson", lw=1.4,
            label="Michell thin-ship theory, $C_w$")
    ax.plot(fns, 1e3 * cp, "o-", color="navy", ms=5,
            label="OpenFOAM, pressure component $C_p$")
    ax.plot(fns, 1e3 * (cp + cf_ittc), "s--", color="seagreen", ms=4,
            label="OpenFOAM $C_p$ + ITTC-57 friction = $C_t$")

    # every point carries the one number that explains it
    for r in rows:
        ax.annotate(f"{r['cells_per_wave']:.0f} cells/$\\lambda$",
                    (r["fn"], 1e3 * r["Cp"]), textcoords="offset points",
                    xytext=(0, -16), ha="center", fontsize=7, color="0.35")

    other = [r for r in all_rows if r["level"] != level]
    if other:
        ax.plot([r["fn"] for r in other], [1e3 * r["Cp"] for r in other], "o",
                mfc="none", mec="navy", ms=7, label="coarser mesh, same speed")
    ax.set_xlabel("Froude number $F_n = U/\\sqrt{gL}$")
    ax.set_ylabel(r"resistance coefficient $\times 10^3$")
    ax.set_title("Wigley hull: wave resistance, CFD against thin-ship theory")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    p = os.path.join(out, "cw_vs_michell.png")
    fig.savefig(p, dpi=160)
    plt.close(fig)
    return p


def mesh_study(rows, out):
    rows = [r for r in rows if abs(r["fn"] - 0.316) < 1e-6 and r["cells"]]
    if len(rows) < 2:
        return None
    rows.sort(key=lambda r: r["cells"])
    h = np.array([r["cells"] ** (-1 / 3) for r in rows])
    fig, ax = plt.subplots(figsize=(6, 4))
    for key, marker, label in (("Ct", "o", "$C_t$"), ("Cp", "s", "$C_p$"), ("Cf", "^", "$C_f$")):
        ax.plot(h, [1e3 * r[key] for r in rows], marker + "-", label=label)
    ax.set_xlabel(r"representative cell size $N^{-1/3}$")
    ax.set_ylabel(r"coefficient $\times 10^3$")
    ax.set_title("Mesh study at $F_n$ = 0.316")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    p = os.path.join(out, "mesh_study.png")
    fig.savefig(p, dpi=160)
    plt.close(fig)
    return p


def wave_cuts(case, out, L=3.0, U=None, cuts=(0.05, 0.2, 0.5)):
    """Free-surface elevation along lines parallel to the hull centreline."""
    files = glob.glob(os.path.join(case, "postProcessing/waterLine/*/*freeSurface*.raw"))
    if not files:
        return None
    pts = np.loadtxt(sorted(files)[-1], comments="#")
    if pts.ndim != 2 or pts.shape[1] < 3:
        return None
    x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]

    fig, ax = plt.subplots(figsize=(9, 4))
    for frac in cuts:
        y0 = frac * L
        band = np.abs(y - y0) < 0.02 * L
        if band.sum() < 20:
            continue
        xs = x[band]
        zs = z[band]
        o = np.argsort(xs)
        xs, zs = xs[o], zs[o]
        # bin to a regular grid so the trace is readable
        bins = np.linspace(xs.min(), xs.max(), 200)
        idx = np.digitize(xs, bins)
        xb = np.array([xs[idx == i].mean() for i in range(1, len(bins)) if (idx == i).any()])
        zb = np.array([zs[idx == i].mean() for i in range(1, len(bins)) if (idx == i).any()])
        ax.plot(xb / L, zb / L, lw=1.1, label=f"y = {frac:.2f} L")
    ax.axvspan(-0.5, 0.5, color="0.9", zorder=0, label="hull")
    ax.set_xlabel("x / L")
    ax.set_ylabel(r"$\zeta$ / L")
    ax.set_title(f"Wave cuts — {os.path.basename(case)}")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    p = os.path.join(out, f"wave_cuts_{os.path.basename(case)}.png")
    fig.savefig(p, dpi=160)
    plt.close(fig)
    return p


def wave_pattern(case, out, L=3.0):
    """Plan view of the free surface, with the Kelvin half-angle drawn on.

    A steady wave system trails behind a point disturbance inside a wedge of
    half-angle arcsin(1/3) = 19.47 degrees, whatever the speed.  It is the
    cheapest check there is that a free-surface solver is behaving.
    """
    files = glob.glob(os.path.join(case, "postProcessing/waterLine/*/*freeSurface*.raw"))
    if not files:
        return None
    pts = np.loadtxt(sorted(files)[-1], comments="#")
    if pts.ndim != 2 or pts.shape[1] < 3:
        return None
    x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]
    keep = (x > -1.0 * L) & (x < 2.0 * L) & (y < 1.1 * L)
    x, y, z = x[keep], y[keep], z[keep]

    fig, ax = plt.subplots(figsize=(9, 4.2))
    sc = ax.scatter(x / L, y / L, c=z / L, s=1.5, cmap="RdBu_r",
                    vmin=-np.percentile(np.abs(z), 98) / L,
                    vmax=np.percentile(np.abs(z), 98) / L)
    fig.colorbar(sc, ax=ax, label=r"$\zeta$ / L")

    # Kelvin wedge, drawn from the bow
    ang = np.arcsin(1 / 3)
    xs = np.linspace(0.5, 2.0, 10)
    ax.plot(xs, (xs - 0.5) * np.tan(ang), "k--", lw=1,
            label=f"Kelvin half-angle {np.degrees(ang):.2f}°")
    # the hull itself, at the waterline
    xh = np.linspace(-0.5, 0.5, 100)
    ax.fill_between(xh, 0, 0.05 * (1 - (2 * xh) ** 2), color="0.55", zorder=3)
    ax.set_xlabel("x / L")
    ax.set_ylabel("y / L")
    ax.set_title(f"Free-surface elevation, plan view — {os.path.basename(case)}")
    ax.legend(fontsize=8, loc="upper right")
    ax.set_ylim(0, 1.1)
    fig.tight_layout()
    p = os.path.join(out, f"wave_pattern_{os.path.basename(case)}.png")
    fig.savefig(p, dpi=160)
    plt.close(fig)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="cases")
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    cases = [c for c in sorted(glob.glob(os.path.join(a.cases, "fn*"))) if os.path.isdir(c)]
    rows = [r for r in (pp.analyse(c) for c in cases) if r]
    for r, c in zip(rows, cases):
        r["cells"] = pp.cell_count(c)

    made = [convergence(cases, a.out)]
    if rows:
        made.append(cw_curve(rows, a.out))
        made.append(mesh_study(rows, a.out))
    for c in cases:
        made.append(wave_cuts(c, a.out))
        made.append(wave_pattern(c, a.out))
    for m in made:
        if m:
            print("wrote", m)


if __name__ == "__main__":
    main()
