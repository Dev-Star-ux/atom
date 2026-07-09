"""Shared physics for uncertainty-principle topics (Ch.3 Sec.2).

Gaussian wave-packet minimum uncertainty:  Δx·Δp = ħ/2.
"""
import math

from simulations.atom import H, H_BAR

HBAR_EV_S = H_BAR / 1.602176634e-19   # ħ in eV·s ≈ 6.58×10⁻¹⁶


def gaussian_dx(sigma_x):
    """Position uncertainty for a Gaussian packet (m)."""
    return sigma_x


def gaussian_dp(sigma_x):
    """Momentum uncertainty at minimum uncertainty (kg·m/s)."""
    return H_BAR / (2.0 * sigma_x) if sigma_x > 0 else float("inf")


def xp_product(sigma_x):
    """Δx·Δp for minimum-uncertainty Gaussian (= ħ/2)."""
    return gaussian_dx(sigma_x) * gaussian_dp(sigma_x)


def gaussian_dk(sigma_x):
    """Wave-number spread (m⁻¹)."""
    return 1.0 / (2.0 * sigma_x) if sigma_x > 0 else float("inf")


def psi_gaussian(x, sigma_x, k0=0.0):
    """Real part of a Gaussian plane-wave packet (arbitrary normalisation)."""
    if sigma_x <= 0:
        return 0.0
    env = math.exp(-(x * x) / (2.0 * sigma_x * sigma_x))
    return env * math.cos(k0 * x)


def prob_gaussian(x, sigma_x):
    """|ψ|² ∝ Gaussian."""
    if sigma_x <= 0:
        return 0.0
    return math.exp(-(x * x) / (sigma_x * sigma_x))


def momentum_prob(k, sigma_x, k0=0.0):
    """Momentum-space probability (Gaussian in k-k0)."""
    dk = gaussian_dk(sigma_x)
    if dk <= 0:
        return 0.0
    return math.exp(-((k - k0) ** 2) / (4.0 * dk * dk))


def energy_uncertainty_eV(lifetime_s):
    """Energy uncertainty (eV) for state lifetime τ (s): ΔE ≈ ħ/2τ."""
    if lifetime_s <= 0:
        return float("inf")
    return HBAR_EV_S / (2.0 * lifetime_s)


def decay_envelope(t, tau):
    """|ψ(t)|² for exponential decay with lifetime τ."""
    if tau <= 0:
        return 0.0
    return math.exp(-t / tau)


def lorentzian_energy(E, E0, gamma):
    """Lorentzian energy distribution (arb. units)."""
    if gamma <= 0:
        return 0.0
    d = E - E0
    return gamma / (d * d + gamma * gamma)
