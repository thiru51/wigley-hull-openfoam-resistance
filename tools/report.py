#!/usr/bin/env python
"""Write out/RESULTS.md from the finished cases, so the numbers in the
documentation are generated rather than typed.

    python tools/report.py
"""

from __future__ import annotations

import argparse
import glob
import os
from datetime import date

import postprocess as pp


def table(rows):
    head = ("| case | Fn | cells | iters | cells/λ | Ct×10³ | Cp×10³ | Cf×10³ | "
            "ITTC-57 Cf×10³ | Michell Cw×10³ | Cp/Cw | drift | oscillation |")
    sep = "|" + "---|" * 13
    lines = [head, sep]
    for r in sorted(rows, key=lambda r: (r["level"], r["fn"])):
        ratio = r["Cp"] / r["Cw_michell"] if r["Cw_michell"] else float("nan")
        lines.append(
            f"| {r['case']} | {r['fn']:.3f} | {r['cells']:,} | {r['iterations']} | "
            f"{r['cells_per_wave']:.1f} | "
            f"{1e3*r['Ct']:.3f} | {1e3*r['Cp']:.3f} | {1e3*r['Cf']:.3f} | "
            f"{1e3*r['Cf_ittc57']:.3f} | {1e3*r['Cw_michell']:.3f} | {ratio:.2f} | "
            f"{100*r['tail_drift']:+.0f} % | {100*r['osc_amplitude']:.0f} % |"
        )
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="cases")
    ap.add_argument("--out", default="out")
    a = ap.parse_args()

    cases = [c for c in sorted(glob.glob(os.path.join(a.cases, "fn*"))) if os.path.isdir(c)]
    rows = []
    for c in cases:
        r = pp.analyse(c)
        if r:
            r["cells"] = pp.cell_count(c) or 0
            r["yplus"] = pp.y_plus(c)
            r["levels"] = pp.water_level(c)
            rows.append(r)
    if not rows:
        print("nothing to report yet")
        return

    os.makedirs(a.out, exist_ok=True)
    med = [r for r in rows if r["level"] == "medium"]
    body = [
        f"# Results — generated {date.today().isoformat()}",
        "",
        "Wigley hull, L = 3.0 m, B = 0.3 m, T = 0.1875 m, fresh water at 15 °C.",
        "Coefficients use the wetted surface of the half hull; the domain is a half model.",
        "",
        table(rows),
        "",
        "`Cp/Cw` compares the computed pressure resistance with Michell's thin-ship wave",
        "resistance. Two effects pull it in opposite directions: the computed pressure",
        "force also carries viscous form drag, which Michell's inviscid theory has no",
        "term for and which pushes the ratio above 1; while a mesh that cannot carry the",
        "waves damps them, which pulls it below 1. The `cells/λ` column says which effect",
        "should dominate each row -- ship CFD practice asks for 40 or more.",
        "",
    ]
    if med:
        best = min(med, key=lambda r: abs(r["fn"] - 0.316))
        yp = best.get("yplus")
        lv = best.get("levels") or []
        body += [
            "## At Fn = 0.316",
            "",
            f"- total resistance on the half hull: **{best['R_total_N']:.3f} N** "
            f"({best['R_pressure_N']:.3f} N pressure, {best['R_viscous_N']:.3f} N viscous)",
            f"- Ct = {1e3*best['Ct']:.3f} × 10⁻³, of which pressure {1e3*best['Cp']:.3f} × 10⁻³",
            f"- Michell wave resistance at the same speed: Cw = {1e3*best['Cw_michell']:.3f} × 10⁻³",
            f"- ITTC-57 friction line at Re = {best['Re']:.2e}: Cf = {1e3*best['Cf_ittc57']:.3f} × 10⁻³",
            "",
            "### Diagnostics",
            "",
            (f"- y+ on the hull: min {yp[0]:.1f}, max {yp[1]:.0f}, mean {yp[2]:.0f} — "
             "no prism layers, so the friction is under-resolved and is reported beside "
             "the ITTC line rather than instead of it." if yp else "- y+ not available"),
            (f"- far-field still-water level: " +
             ", ".join(f"{1e3*z:+.1f} mm at {it}" for it, z in lv) +
             " — it should be zero; the drift is the leading defect in this setup."
             if lv else "- water level not available"),
            f"- pressure force oscillation over the averaging window: "
            f"{100*best['osc_amplitude']:.0f} % of its mean, period roughly 900 iterations.",
            "",
        ]
    path = os.path.join(a.out, "RESULTS.md")
    with open(path, "w") as fh:
        fh.write("\n".join(body))
    print(f"wrote {path}")
    print("\n".join(body[:8]))


if __name__ == "__main__":
    main()
