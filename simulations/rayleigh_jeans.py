"""Chapter 2, Section 1, Topic 3 - The Rayleigh-Jeans law.

The classical result u = 8 pi k T / lambda^4 matches experiment at long
wavelengths but blows up as lambda -> 0: it predicts an infinite total energy,
the "ultraviolet catastrophe". Shown here against the actual (Planck) spectrum
on the same axes so the divergence at short wavelengths is unmistakable.
"""
from simulations.spectrum_base import SpectrumSim, XTICKS
import simulations.bb as bb


class RayleighJeansSim(SpectrumSim):
    title_key = "topic.rayleigh_jeans.title"
    desc_key = "topic.rayleigh_jeans.desc"

    def __init__(self, master, app):
        self.temp = 4000.0
        super().__init__(master, app)

    def build_controls(self, parent):
        self.t_var, _ = self.add_slider(
            parent, self.t("topic.rayleigh_jeans.temperature"), 1000, 8000, self.temp,
            command=lambda v: setattr(self, "temp", v), fmt="{:.0f} K",
        )
        self.r_peak = self.add_readout(parent, self.t("topic.rayleigh_jeans.peak"))
        self.r_ratio = self.add_readout(parent, self.t("topic.rayleigh_jeans.ratio"))

    def reset(self):
        self.temp = 4000.0
        self.t_var.set(self.temp)

    def render(self):
        c = self.canvas
        lams = self.lam_grid()
        xs = self.nm(lams)
        scale = self.planck_peak_value(self.temp) or 1.0
        p = self.make_plot(1.6)
        p.axes(self.t("topic.rayleigh_jeans.xlabel"),
               self.t("topic.rayleigh_jeans.ylabel"), XTICKS)

        # Rayleigh-Jeans (classical) - diverges toward short wavelengths
        p.curve(xs, [bb.rayleigh_jeans_u(l, self.temp) / scale for l in lams],
                "#f87171", width=2, dash=(5, 3))
        # Planck (experiment)
        p.curve(xs, [bb.planck_u(l, self.temp) / scale for l in lams], "#38bdf8", width=2)

        # annotations
        p.label(140, 1.5, self.t("topic.rayleigh_jeans.uv"), "#f87171", anchor="w")
        p.label(1700, 0.42, self.t("topic.rayleigh_jeans.planck_label"), "#38bdf8", anchor="w")
        p.label(2200, 0.12, self.t("topic.rayleigh_jeans.agree"), self.colors["canvas_text"], anchor="w")

        peak_nm = bb.wien_peak(self.temp) * 1e9
        self.r_peak.set(f"{peak_nm:.0f} nm")
        # classical vs actual at 400 nm (deep in the divergence)
        rj = bb.rayleigh_jeans_u(400e-9, self.temp)
        pl = bb.planck_u(400e-9, self.temp) or 1e-30
        self.r_ratio.set(f"{rj / pl:.0f}×")
