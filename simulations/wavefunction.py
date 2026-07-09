"""Shared math for wave-function statistics (Ch.3 Sec.3+)."""
import math
import random

from simulations.atom import H_BAR, M_E, E_CHARGE


def double_slit_intensity(y, d, lam, L):
    """Two-slit interference intensity (normalised 0–1).

    y = transverse position on screen, d = slit separation,
    lam = wavelength, L = slit-to-screen distance.
    """
    if lam <= 0 or L <= 0:
        return 0.0
    beta = math.pi * d * y / (lam * L)
    return math.cos(beta) ** 2


def infinite_well_psi(n, x, a):
    """Normalised real eigenfunction for 1-D box [0, a]."""
    if x < 0 or x > a:
        return 0.0
    return math.sqrt(2.0 / a) * math.sin(n * math.pi * x / a)


def infinite_well_prob(n, x, a):
    """|ψ|² for particle in a box."""
    psi = infinite_well_psi(n, x, a)
    return psi * psi


def sample_from_prob(prob_fn, x_min, x_max, n_bins=80):
    """Sample one x from a discretised probability density."""
    step = (x_max - x_min) / n_bins
    weights = []
    xs = []
    for i in range(n_bins):
        x = x_min + (i + 0.5) * step
        w = max(0.0, prob_fn(x))
        weights.append(w)
        xs.append(x)
    total = sum(weights) or 1.0
    r = random.random() * total
    acc = 0.0
    for x, w in zip(xs, weights):
        acc += w
        if acc >= r:
            return x
    return xs[-1]


def infinite_well_energy_J(n, a, mass=M_E):
    """Energy eigenvalue E_n for 1-D infinite square well (J)."""
    if n < 1 or a <= 0:
        return 0.0
    return n * n * math.pi * math.pi * H_BAR * H_BAR / (2.0 * mass * a * a)


def infinite_well_energy_eV(n, a, mass=M_E):
    """Energy eigenvalue (eV)."""
    return infinite_well_energy_J(n, a, mass) / E_CHARGE


def infinite_well_ground_eV(a, mass=M_E):
    return infinite_well_energy_eV(1, a, mass)


def psi_superposition(x, a, n1, n2, t, omega_scale=1.0):
    """Real part of ψ = ψ_{n1} e^{-iω₁t} + ψ_{n2} e^{-iω₂t} (equal weights)."""
    if x < 0 or x > a:
        return 0.0
    psi1 = infinite_well_psi(n1, x, a)
    psi2 = infinite_well_psi(n2, x, a)
    E1 = infinite_well_energy_J(n1, a)
    E2 = infinite_well_energy_J(n2, a)
    w1 = E1 / H_BAR * omega_scale * t
    w2 = E2 / H_BAR * omega_scale * t
    return psi1 * math.cos(w1) + psi2 * math.cos(w2)


def prob_superposition(x, a, n1, n2, t, omega_scale=1.0):
    """|ψ|² for superposition (uses full complex sum)."""
    if x < 0 or x > a:
        return 0.0
    psi1 = infinite_well_psi(n1, x, a)
    psi2 = infinite_well_psi(n2, x, a)
    E1 = infinite_well_energy_J(n1, a)
    E2 = infinite_well_energy_J(n2, a)
    w1 = E1 / H_BAR * omega_scale * t
    w2 = E2 / H_BAR * omega_scale * t
    re = psi1 * math.cos(w1) + psi2 * math.cos(w2)
    im = -psi1 * math.sin(w1) - psi2 * math.sin(w2)
    return re * re + im * im

