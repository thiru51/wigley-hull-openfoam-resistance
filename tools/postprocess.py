#!/usr/bin/env python
"""Turn the solver's force history into resistance coefficients, and compare.

    python tools/postprocess.py            # every finished case in cases/

For each case it reads postProcessing/forces/*/force.dat, averages the last
window of the run (LTS marches to a steady state, so the tail is the answer),
and forms

    Ct = R_total    / (0.5 rho S U^2)      total resistance coefficient
    Cp = R_pressure / (0.5 rho S U^2)      pressure (wave + form) part
    Cf = R_viscous  / (0.5 rho S U^2)      friction part

with S the wetted surface of the half hull, since the domain is a half model.

Cp is then set against Michell's thin-ship wave resistance and Cf against the
ITTC-1957 line: two independent references, neither of them fitted.
"""

from __future__ import annotations

import argparse
import glob
import json
import os

import numpy as np

import michell

G = 9.81


def read_forces(case: str):
    """Iteration number and the x-components of total, pressure and viscous force."""
    paths = sorted(glob.glob(os.path.join(case, "postProcessing/forces/*/force.dat")))
    if not paths:
        return None
    it, tot, pres, visc = [], [], [], []
    for p in paths:
        for line in open(p):
            if line.startswith("#"):
                continue
            v = line.split()
            if len(v) < 10:
                continue
            it.append(float(v[0]))
            tot.append(float(v[1]))
            pres.append(float(v[4]))
            visc.append(float(v[7]))
    o = np.argsort(it)
    return (np.array(it)[o], np.array(tot)[o], np.array(pres)[o], np.array(visc)[o])


def analyse(case: str, tail_fraction: float = 0.2):
    meta_path = os.path.join(case, "case.json")
    if not os.path.exists(meta_path):
        return None          # a deferred or half-built case directory
    meta = json.load(open(meta_path))
    data = read_forces(case)
    if data is None:
        return None
    it, tot, pres, visc = data

    n_tail = max(5, int(len(it) * tail_fraction))
    sl = slice(-n_tail, None)

    U, L, rho = meta["U"], meta["L"], meta["rho"]
    S_half = michell.wetted_surface(L=meta["L"], B=meta["B"], T=meta["T"]) / 2.0
    q = 0.5 * rho * S_half * U**2

    Rt, Rp, Rv = tot[sl].mean(), pres[sl].mean(), visc[sl].mean()
    spread = tot[sl].std() / abs(Rt) if Rt else np.nan

    # Scatter alone can look settled while the force is still walking
    # downhill, which is exactly what the first runs of this study did.  The
    # drift -- the least-squares slope over the averaging window, expressed as
    # a percentage change across it -- is the honest convergence measure.
    if len(it[sl]) > 2 and Rt:
        slope = np.polyfit(it[sl], tot[sl], 1)[0]
        drift = slope * (it[sl][-1] - it[sl][0]) / abs(Rt)
    else:
        drift = np.nan

    Re = U * L / meta["nu"]
    cw_michell = michell.michell_resistance(meta["fn"], L=meta["L"], B=meta["B"], T=meta["T"],
                                            rho=rho) / 2.0 / q

    return dict(
        case=os.path.basename(case),
        fn=meta["fn"],
        level=meta["level"],
        cells=meta.get("cells"),
        iterations=int(it[-1]),
        U=U,
        Re=Re,
        R_total_N=Rt,
        R_pressure_N=Rp,
        R_viscous_N=Rv,
        Ct=Rt / q,
        Cp=Rp / q,
        Cf=Rv / q,
        Cf_ittc57=michell.ittc57(Re),
        Cw_michell=cw_michell,
        tail_spread=spread,
        tail_drift=drift,
    )


def y_plus(case: str):
    """Min, mean and max y+ on the hull, from the yPlus function object.

    Reported because it is the number that says how far the friction can be
    trusted: without prism layers it lands far above the log-layer range.
    """
    files = sorted(glob.glob(os.path.join(case, "postProcessing/yPlus/*/yPlus.dat")))
    if not files:
        return None
    last = None
    for line in open(files[-1]):
        if line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 5 and parts[1] == "hull":
            last = tuple(float(v) for v in parts[2:5])
    return last  # (min, max, average)


def cell_count(case: str):
    log = os.path.join(case, "log.snappyHexMesh")
    if not os.path.exists(log):
        return None
    cells = None
    for line in open(log):
        if "cells:" in line:
            try:
                cells = int(line.split("cells:")[1].split()[0])
            except (IndexError, ValueError):
                pass
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="cases")
    ap.add_argument("--out", default="out")
    ap.add_argument("--tail", type=float, default=0.2)
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    rows = []
    for case in sorted(glob.glob(os.path.join(a.cases, "fn*"))):
        if not os.path.isdir(case):
            continue
        r = analyse(case, a.tail)
        if r:
            r["cells"] = cell_count(case)
            r["yplus"] = y_plus(case)
            rows.append(r)

    if not rows:
        print("no finished cases yet")
        return

    keys = list(rows[0].keys())
    with open(os.path.join(a.out, "results.csv"), "w") as fh:
        fh.write(",".join(keys) + "\n")
        for r in rows:
            fh.write(",".join("" if r[k] is None else str(r[k]) for k in keys) + "\n")

    print(f"{'case':>16} {'Fn':>6} {'cells':>8} {'iters':>6} {'Ct*1e3':>8} {'Cp*1e3':>8} "
          f"{'Cf*1e3':>8} {'ITTC*1e3':>9} {'Michell*1e3':>12} {'sd%':>6} {'drift%':>7}")
    for r in rows:
        print(f"{r['case']:>16} {r['fn']:6.3f} {r['cells'] or 0:8d} {r['iterations']:6d} "
              f"{1e3*r['Ct']:8.3f} {1e3*r['Cp']:8.3f} {1e3*r['Cf']:8.3f} "
              f"{1e3*r['Cf_ittc57']:9.3f} {1e3*r['Cw_michell']:12.3f} "
              f"{100*r['tail_spread']:6.2f} {100*r['tail_drift']:7.2f}")
    return rows


if __name__ == "__main__":
    main()
