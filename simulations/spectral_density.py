"""Chapter 2, Section 1, Topic 1 - Spectral energy density.

Introduces the idea that thermal radiation is described by a *spectral energy
density* u(lambda, T): the energy contained in each small wavelength interval.
The curve is the (measured) blackbody spectrum. A movable cursor highlights a
narrow band dlambda and reports the fraction of the total energy it holds, so
students see what "u dlambda = energy in [lambda, lambda+dlambda]" means.
"""
from simulations.spectrum_base import SpectrumSim, XTICKS
import simulations.bb as bb


class SpectralDensitySim(SpectrumSim):
    title_key = "topic.spectral_density.title"
    desc_key = "topic.spectral_density.desc"

    BAND_NM = 80  # half-width of the highlighted band

    def __init__(self, master, app):
        self.temp = 5000.0
        self.cursor = 600.0   # nm
        super().__init__(master, app)

    def build_controls(self, parent):
        self.t_var, _ = self.add_slider(
            parent, self.t("topic.spectral_density.temperature"), 1000, 8000, self.temp,
            command=lambda v: setattr(self, "temp", v), fmt="{:.0f} K",
        )
        self.c_var, _ = self.add_slider(
            parent, self.t("topic.spectral_density.cursor"), 100, 3000, self.cursor,
            command=lambda v: setattr(self, "cursor", v), fmt="{:.0f} nm",
        )
        self.r_peak = self.add_readout(parent, self.t("topic.spectral_density.peak"))
        self.r_u = self.add_readout(parent, self.t("topic.spectral_density.u_here"))
        self.r_band = self.add_readout(parent, self.t("topic.spectral_density.band_energy"))

    def reset(self):
        self.temp = 5000.0
        self.cursor = 600.0
        self.t_var.set(self.temp)
        self.c_var.set(self.cursor)

    def draw(self):
        c = self.canvas
        c.delete("all")
        lams = self.lam_grid()
        us = [bb.planck_u(l, self.temp) for l in lams]
        ymax = (max(us) or 1.0) * 1.15
        p = self.make_plot(ymax)

        # highlighted band around the cursor
        p.band(self.cursor - self.BAND_NM, self.cursor + self.BAND_NM, "#1e293b")
        p.axes(self.t("topic.spectral_density.xlabel"),
               self.t("topic.spectral_density.ylabel"), XTICKS)
        p.curve(self.nm(lams), us, "#38bdf8", width=2)

        # Wien peak marker
        peak_nm = bb.wien_peak(self.temp) * 1e9
        p.vline(peak_nm, "#fbbf24", label=self.t("topic.spectral_density.peak_mark"))

        # cursor line
        p.vline(self.cursor, "#f472b6")

        # readouts
        self.r_peak.set(f"{peak_nm:.0f} nm")
        u_here = bb.planck_u(self.cursor * 1e-9, self.temp)
        self.r_u.set(f"{u_here / ymax * 1.15 * 100:.0f} %")  # relative to peak
        total = sum(us)
        lo, hi = self.cursor - self.BAND_NM, self.cursor + self.BAND_NM
        band_sum = sum(u for l, u in zip(self.nm(lams), us) if lo <= l <= hi)
        self.r_band.set(f"{100.0 * band_sum / (total or 1):.1f} %")
