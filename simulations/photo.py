"""Shared helpers for the photoelectric-effect topics (Chapter 2, Section 2)."""
import simulations.bb as bb

E_CHARGE = 1.602176634e-19   # C  (and 1 eV in joules)

# Photocathode / metal work functions in eV.
MATERIALS = {
    "cesium": 2.10,
    "sodium": 2.28,
    "calcium": 2.87,
    "zinc": 4.30,
    "copper": 4.70,
    "platinum": 6.35,
}


def photon_energy_eV(f14):
    """Photon energy (eV) for a frequency given in units of 1e14 Hz."""
    return bb.H * (f14 * 1e14) / E_CHARGE


def freq_to_nm(f14):
    """Wavelength (nm) for a frequency in units of 1e14 Hz."""
    return 3.0e8 / (f14 * 1e14) * 1e9


def threshold_f14(work_eV):
    """Threshold frequency (in 1e14 Hz) for a work function in eV."""
    return work_eV * E_CHARGE / bb.H / 1e14


def wavelength_to_rgb(nm):
    """Approximate sRGB hex for a visible wavelength (Dan Bruton's algorithm).

    Ultraviolet (<380 nm) is shown as a pale violet, infrared (>750 nm) as a
    deep red, so light outside the visible band still reads sensibly.
    """
    if nm < 380:
        r, g, b = 0.4, 0.2, 0.6         # UV -> violet-ish
        return _pack(r, g, b)
    if nm > 750:
        return _pack(0.5, 0.05, 0.05)   # IR -> deep red

    if nm < 440:
        r, g, b = -(nm - 440) / (440 - 380), 0.0, 1.0
    elif nm < 490:
        r, g, b = 0.0, (nm - 440) / (490 - 440), 1.0
    elif nm < 510:
        r, g, b = 0.0, 1.0, -(nm - 510) / (510 - 490)
    elif nm < 580:
        r, g, b = (nm - 510) / (580 - 510), 1.0, 0.0
    elif nm < 645:
        r, g, b = 1.0, -(nm - 645) / (645 - 580), 0.0
    else:
        r, g, b = 1.0, 0.0, 0.0

    # intensity falloff at the ends of the visible range
    if nm < 420:
        f = 0.3 + 0.7 * (nm - 380) / (420 - 380)
    elif nm > 700:
        f = 0.3 + 0.7 * (750 - nm) / (750 - 700)
    else:
        f = 1.0
    return _pack(r * f, g * f, b * f)


def _pack(r, g, b):
    gamma = 0.8
    def ch(v):
        return int(max(0.0, min(1.0, v)) ** gamma * 255)
    return f"#{ch(r):02x}{ch(g):02x}{ch(b):02x}"


def photon_color(f14):
    return wavelength_to_rgb(freq_to_nm(f14))
