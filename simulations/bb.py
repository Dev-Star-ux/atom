"""Shared physics for the blackbody-radiation topics (Chapter 2, Section 1).

All functions use SI units. Wavelength lambda is in metres.
"""
import math

H = 6.62607015e-34     # Planck constant (J s)
C = 2.99792458e8       # speed of light (m/s)
K = 1.380649e-23       # Boltzmann constant (J/K)
SIGMA = 5.670374e-8    # Stefan-Boltzmann constant (W m^-2 K^-4)
WIEN = 2.897771e-3     # Wien displacement constant (m K)


def planck_u(lam, T, h=H):
    """Planck spectral energy density per unit wavelength (J / m^3 / m).

    u(lam,T) = 8 pi h c / lam^5 * 1 / (exp(h c / (lam k T)) - 1)

    `h` is exposed so the Planck topic can show the classical limit h -> 0.
    """
    if lam <= 0 or T <= 0:
        return 0.0
    x = h * C / (lam * K * T)
    if x > 700:          # exp overflow guard; the term is ~0 here anyway
        return 0.0
    if x < 1e-6:
        return 0.0
    return (8.0 * math.pi * h * C) / (lam ** 5) / (math.exp(x) - 1.0)


def rayleigh_jeans_u(lam, T):
    """Rayleigh-Jeans spectral energy density: 8 pi k T / lam^4.

    Diverges as lam -> 0 (the ultraviolet catastrophe)."""
    if lam <= 0 or T <= 0:
        return 0.0
    return 8.0 * math.pi * K * T / (lam ** 4)


def wien_peak(T):
    """Wavelength of peak emission (m) from Wien's displacement law."""
    return WIEN / T if T > 0 else 0.0


def stefan_boltzmann(T):
    """Total radiated power per unit area (W/m^2): sigma T^4."""
    return SIGMA * T ** 4


def blackbody_rgb(T):
    """Approximate sRGB hex colour of a blackbody at temperature T (K).

    Based on Tanner Helland's widely used approximation. Good for ~1000-40000 K.
    """
    t = min(40000.0, max(1000.0, T)) / 100.0
    # red
    if t <= 66:
        r = 255.0
    else:
        r = 329.698727446 * (t - 60) ** -0.1332047592
    # green
    if t <= 66:
        g = 99.4708025861 * math.log(t) - 161.1195681661
    else:
        g = 288.1221695283 * (t - 60) ** -0.0755148492
    # blue
    if t >= 66:
        b = 255.0
    elif t <= 19:
        b = 0.0
    else:
        b = 138.5177312231 * math.log(t - 10) - 305.0447927307

    def clamp(v):
        return int(max(0.0, min(255.0, v)))

    return f"#{clamp(r):02x}{clamp(g):02x}{clamp(b):02x}"
