"""Shared physics for atomic-spectrum topics (Chapter 2, Section 3).

All wavelengths are in metres unless noted. Energies in eV.
"""
import math

H = 6.62607015e-34     # Planck constant (J s)
C = 2.99792458e8       # speed of light (m/s)
E_CHARGE = 1.602176634e-19
R_H = 1.0973731568160e7   # Rydberg constant for hydrogen (m^-1)

# First excitation energies for Frank–Hertz gases (eV)
GASES = {
    "mercury": 4.89,
    "neon": 16.62,
}

# Named emission lines for prism-spectroscope sources (wavelength nm, relative intensity)
HYDROGEN_LINES = [
    (656.3, 1.00, "Hα"),
    (486.1, 0.55, "Hβ"),
    (434.0, 0.35, "Hγ"),
    (410.2, 0.22, "Hδ"),
    (397.0, 0.15, "Hε"),
]

HELIUM_LINES = [
    (587.6, 0.90, "He D3"),
    (447.1, 0.70, "He blue"),
    (492.2, 0.45, "He green"),
    (667.8, 0.55, "He red"),
    (706.5, 0.40, "He IR"),
]

SODIUM_LINES = [
    (589.0, 1.00, "D2"),
    (589.6, 0.95, "D1"),
]


def hydrogen_wavelength(n1, n2):
    """Wavelength (m) for transition n2 -> n1 (n2 > n1)."""
    if n2 <= n1 or n1 < 1:
        return 0.0
    inv_lam = R_H * (1.0 / (n1 * n1) - 1.0 / (n2 * n2))
    return 1.0 / inv_lam if inv_lam > 0 else 0.0


def hydrogen_series(n1, n_max=7):
    """List of (wavelength_nm, relative_intensity, label) for n1 -> n2 transitions."""
    out = []
    greek = ("α", "β", "γ", "δ", "ε", "ζ", "η")
    for i, n2 in enumerate(range(n1 + 1, n_max + 1)):
        lam = hydrogen_wavelength(n1, n2) * 1e9
        if lam <= 0:
            continue
        rel = 1.0 / ((n2 - n1) ** 1.5)
        series = {1: "L", 2: "B", 3: "P", 4: "B", 5: "P", 6: "B"}.get(n1, "")
        label = f"{series}{greek[i]}" if series else f"{n1}→{n2}"
        out.append((lam, rel, label))
    if out:
        peak = max(r for _, r, _ in out)
        out = [(lam, r / peak, lbl) for lam, r, lbl in out]
    return out


def energy_level_eV(n):
    """Bohr energy level En = -13.6 / n² eV."""
    return -13.6 / (n * n)


def transition_energy_eV(n1, n2):
    """Photon energy for transition n2 -> n1 (eV)."""
    return energy_level_eV(n1) - energy_level_eV(n2)


def photon_energy_eV_from_nm(nm):
    """Photon energy (eV) from wavelength in nm."""
    if nm <= 0:
        return 0.0
    return H * C / (nm * 1e-9) / E_CHARGE


def wavelength_to_rgb(nm):
    """Approximate sRGB hex for a monochromatic wavelength (nm).

    Returns grey for wavelengths outside the visible band (~380–780 nm).
    """
    if nm < 380 or nm > 780:
        t = max(0.0, min(1.0, (nm - 300) / 80))
        g = int(80 + 60 * t)
        return f"#{g:02x}{g:02x}{g:02x}"

    if nm < 440:
        r = -(nm - 440) / (440 - 380)
        g = 0.0
        b = 1.0
    elif nm < 490:
        r = 0.0
        g = (nm - 440) / (490 - 440)
        b = 1.0
    elif nm < 510:
        r = 0.0
        g = 1.0
        b = -(nm - 510) / (510 - 490)
    elif nm < 580:
        r = (nm - 510) / (580 - 510)
        g = 1.0
        b = 0.0
    elif nm < 645:
        r = 1.0
        g = -(nm - 645) / (645 - 580)
        b = 0.0
    else:
        r = 1.0
        g = 0.0
        b = 0.0

    # intensity falloff near violet / deep red
    if nm < 420:
        factor = 0.3 + 0.7 * (nm - 380) / (420 - 380)
    elif nm > 700:
        factor = 0.3 + 0.7 * (780 - nm) / (780 - 700)
    else:
        factor = 1.0

    def clamp(v):
        return int(max(0, min(255, v * factor * 255)))

    return f"#{clamp(r):02x}{clamp(g):02x}{clamp(b):02x}"


def frank_hertz_current(V, E0, scale=1.0):
    """Model collector current (arbitrary units) vs accelerating voltage V (V).

    Rises overall with V but shows dips near V = n·E0 when inelastic
    collisions with gas atoms become energetically allowed.
    """
    if V <= 0:
        return 0.0
    base = scale * math.sqrt(V) * (1.0 - 0.08 / V)
    for n in range(1, 6):
        Ve = n * E0
        width = max(0.12, 0.06 * Ve)
        dip = 0.55 * math.exp(-((V - Ve) ** 2) / (2 * width * width))
        base *= 1.0 - dip
    return max(0.0, base)
