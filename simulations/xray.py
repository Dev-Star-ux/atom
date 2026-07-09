"""Shared physics for X-ray topics (Chapter 2, Section 5).

Wavelengths in picometres (pm), energies in keV unless noted.
"""
import math

from simulations.atom import H, C, E_CHARGE, M_E

# Compton wavelength of the electron
LAMBDA_C_PM = H / (M_E * C) * 1e12   # ≈ 2.43 pm

HC_KEV_NM = H * C / E_CHARGE * 1e-3   # hc in keV·nm ≈ 1.2398


def energy_keV_from_lambda_pm(lam_pm):
    """Photon energy (keV) from wavelength in pm."""
    if lam_pm <= 0:
        return 0.0
    lam_nm = lam_pm * 1e-3
    return HC_KEV_NM / lam_nm


def lambda_pm_from_energy_keV(E):
    """Wavelength (pm) from photon energy in keV."""
    if E <= 0:
        return 0.0
    return HC_KEV_NM / E * 1e3


def lambda_min_nm(voltage_kV):
    """Duane–Hunt cutoff wavelength (nm) for an X-ray tube at voltage V (kV)."""
    if voltage_kV <= 0:
        return 0.0
    return HC_KEV_NM / voltage_kV


def compton_shift_pm(theta_rad):
    """Compton wavelength shift Δλ (pm) for scattering angle θ."""
    return LAMBDA_C_PM * (1.0 - math.cos(theta_rad))


def scattered_lambda_pm(lam_pm, theta_rad):
    """Scattered photon wavelength (pm)."""
    return lam_pm + compton_shift_pm(theta_rad)


def bragg_order(n, d_pm, lam_pm):
    """Bragg angle (degrees) for order n, plane spacing d, wavelength λ."""
    if d_pm <= 0 or lam_pm <= 0:
        return 0.0
    s = n * lam_pm / (2.0 * d_pm)
    if abs(s) > 1.0:
        return None
    return math.degrees(math.asin(s))


def bragg_constructive(n, d_pm, lam_pm, theta_deg):
    """Path difference in units of λ for Bragg reflection (integer → bright)."""
    if lam_pm <= 0:
        return 0.0
    return 2.0 * d_pm * math.sin(math.radians(theta_deg)) / lam_pm
