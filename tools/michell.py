#!/usr/bin/env python
"""Michell's thin-ship wave resistance, for the Wigley hull.

Michell (1898) solved the wave resistance of a thin ship in closed form as a
double integral over the centreplane.  For a hull y = f(x, z) advancing at U,

    R_w = (4 rho g^2 / (pi U^2)) Int_1^inf |I(lam)|^2 lam^2 / sqrt(lam^2-1) dlam

    I(lam) = Int Int (df/dx) exp(k0 lam^2 z) exp(i k0 lam x) dx dz,
             k0 = g / U^2

Two things make this evaluable to graph accuracy:

1.  lam = sec(theta) removes the sqrt singularity at lam = 1, leaving
    Int_0^{pi/2} |I|^2 sec^3(theta) d(theta).

2.  The depth factor exp(k0 lam^2 z) decays as lam grows, so the integrand
    dies well before lam = inf.  The upper limit is set from that decay
    (exp(-k0 lam^2 T) < 1e-14) instead of being guessed, which is what keeps
    the fast phase oscillation exp(i k0 lam x) resolved by the x grid.

This is the reference the CFD is judged against: an independent, analytic
prediction of the same quantity.
"""

from __future__ import annotations

import numpy as np

G = 9.81


def wigley_dydx(x, z, L, B, T):
    """Slope of the Wigley centreplane offsets, dy/dx."""
    xi = 2.0 * x / L
    zeta = z / T
    return (B / 2.0) * (-8.0 * x / L**2) * (1.0 - zeta**2) * (np.abs(xi) <= 1.0)


def _lambda_max(k0: float, T: float, decay: float = 1e-14) -> float:
    """Where the depth factor has decayed to `decay` at the keel."""
    return float(np.sqrt(-np.log(decay) / (k0 * T)))


def michell_resistance(
    Fn, L=3.0, B=0.3, T=0.1875, rho=999.0, n_x=2001, n_z=201, n_theta=4001, dydx=wigley_dydx
):
    """Wave resistance R_w (N) of the whole ship at one Froude number."""
    U = Fn * np.sqrt(G * L)
    k0 = G / U**2

    x = np.linspace(-L / 2, L / 2, n_x)
    z = np.linspace(-T, 0.0, n_z)
    X, Z = np.meshgrid(x, z, indexing="ij")
    slope = dydx(X, Z, L, B, T)

    lam_max = _lambda_max(k0, T)
    theta_max = np.arccos(1.0 / lam_max)
    theta = np.linspace(0.0, theta_max, n_theta)
    lam = 1.0 / np.cos(theta)

    # resolve the phase: at least 12 points per wavelength of exp(i k0 lam x)
    need = int(np.ceil(12 * k0 * lam_max * L / (2 * np.pi)))
    if need > n_x:
        x = np.linspace(-L / 2, L / 2, need | 1)
        X, Z = np.meshgrid(x, z, indexing="ij")
        slope = dydx(X, Z, L, B, T)

    I = np.empty(len(theta), dtype=complex)
    for i, lm in enumerate(lam):
        depth = np.exp(k0 * lm**2 * z)                      # (z,)
        inner = np.trapezoid(slope * depth[None, :], z, axis=1)   # (x,)
        I[i] = np.trapezoid(inner * np.exp(1j * k0 * lm * x), x)

    integrand = np.abs(I) ** 2 / np.cos(theta) ** 3
    Rw = (4.0 * rho * G**2 / (np.pi * U**2)) * np.trapezoid(integrand, theta)
    return float(Rw)


def wetted_surface(L=3.0, B=0.3, T=0.1875, n=801):
    """Wetted surface at the design waterline, both sides, m^2."""
    x = np.linspace(-L / 2, L / 2, n)
    z = np.linspace(-T, 0.0, n)
    X, Z = np.meshgrid(x, z, indexing="ij")
    xi, zeta = 2 * X / L, Z / T
    dydx = (B / 2) * (-8 * X / L**2) * (1 - zeta**2)
    dydz = (B / 2) * (1 - xi**2) * (-2 * Z / T**2)
    dS = np.sqrt(1.0 + dydx**2 + dydz**2)
    area_half = np.trapezoid(np.trapezoid(dS, z, axis=1), x, axis=0)
    return float(2.0 * area_half)


def cw_curve(fns, L=3.0, B=0.3, T=0.1875, rho=999.0, **kw):
    """Cw = Rw / (0.5 rho S U^2) over a range of Froude numbers."""
    S = wetted_surface(L=L, B=B, T=T)
    cw = []
    for fn in fns:
        U = fn * np.sqrt(G * L)
        Rw = michell_resistance(fn, L=L, B=B, T=T, rho=rho, **kw)
        cw.append(Rw / (0.5 * rho * S * U**2))
    return np.array(cw), S


def ittc57(Re):
    """ITTC-1957 model-ship correlation line."""
    return 0.075 / (np.log10(Re) - 2.0) ** 2


if __name__ == "__main__":
    fns = np.arange(0.20, 0.451, 0.01)
    cw, S = cw_curve(fns)
    print(f"Wigley L=3.0 B=0.3 T=0.1875, wetted surface {S:.4f} m^2 (both sides)")
    print(f"{'Fn':>6} {'Cw x1e3':>10}")
    for f, c in zip(fns, cw):
        print(f"{f:6.3f} {1e3 * c:10.4f}")
