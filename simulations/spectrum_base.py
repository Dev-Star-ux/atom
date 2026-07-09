"""Common base for the blackbody spectrum plots (Chapter 2, Section 1)."""
from simulations.base import Simulation
from simulations.plot import Plot
import simulations.bb as bb

LAM_MIN = 1e-9          # 1 nm
LAM_MAX = 3000e-9       # 3000 nm
N = 280                 # samples across the wavelength axis
XTICKS = (0, 500, 1000, 1500, 2000, 2500, 3000)


class SpectrumSim(Simulation):
    """Provides a shared wavelength grid and a configured Plot."""

    def lam_grid(self):
        step = (LAM_MAX - LAM_MIN) / (N - 1)
        return [LAM_MIN + i * step for i in range(N)]

    def nm(self, lams):
        return [l * 1e9 for l in lams]

    def make_plot(self, ymax):
        w, h = self.cwh()
        box = (72, 26, w - 26, h - 58)
        return Plot(self.canvas, box, (0, LAM_MAX * 1e9), (0, ymax),
                    self.colors, self.font("small"))

    def planck_peak_value(self, T, h=bb.H):
        return max(bb.planck_u(l, T, h) for l in self.lam_grid())
