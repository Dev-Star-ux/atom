"""Shared physics for matter-wave topics (Chapter 3, Section 1).

de Broglie wavelength λ = h / p = h / (mv).
"""
import math

from simulations.atom import H, C, E_CHARGE, M_E

# Common particle masses (kg)
PARTICLES = {
    "electron": M_E,
    "proton": 1.67262192369e-27,
    "neutron": 1.67492749804e-27,
    "alpha": 6.6446573357e-27,
}


def momentum(mass, velocity):
    """Linear momentum (kg·m/s)."""
    return mass * velocity


def de_broglie_wavelength(mass, velocity):
    """de Broglie wavelength (m)."""
    p = momentum(mass, velocity)
    return H / p if p > 0 else 0.0


def de_broglie_wavelength_pm(mass, velocity):
    """de Broglie wavelength in picometres."""
    return de_broglie_wavelength(mass, velocity) * 1e12


def electron_wavelength_from_voltage(V_volts):
    """Electron λ (m) accelerated through potential V (non-relativistic).

    KE = eV = p²/2m  →  p = √(2m eV)  →  λ = h/p
    """
    if V_volts <= 0:
        return 0.0
    p = math.sqrt(2.0 * M_E * E_CHARGE * V_volts)
    return H / p


def electron_wavelength_pm(V_volts):
    return electron_wavelength_from_voltage(V_volts) * 1e12


def davisson_peak_angle_deg(V_volts, d_pm, n=1):
    """First-order diffraction angle (degrees) — Davisson condition nλ = d sin θ."""
    lam = electron_wavelength_pm(V_volts)
    if lam <= 0 or d_pm <= 0:
        return None
    s = n * lam / d_pm
    if abs(s) > 1.0:
        return None
    return math.degrees(math.asin(s))
