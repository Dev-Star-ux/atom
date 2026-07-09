"""Chapter 2, Section 1, Topic 4 - Quantum radiation (Planck's law).

Planck assumed the oscillators can only exchange energy in quanta E = h nu.
That single idea produces

    u(lambda, T) = 8 pi h c / lambda^5 * 1 / (exp(h c / (lambda k T)) - 1)

which fits experiment perfectly and cures the ultraviolet catastrophe. The
'h scale' slider shrinks Planck's constant toward zero: as h -> 0 the quantum
curve collapses back onto the classical Rayleigh-Jeans curve and the
catastrophe returns - showing that quantisation is exactly what fixes it.
"""
from simulations.spectrum_base import SpectrumSim, XTICKS
import simulations.bb as bb


class PlanckSim(SpectrumSim):
    title_key = "topic.planck.title"
    desc_key = "topic.planck.desc"

    def __init__(self, master, app):
        self.temp = 4000.0
        self.hscale = 1.0
        super().__init__(master, app)

    def build_controls(self, parent):
        self.t_var, _ = self.add_slider(
            parent, self.t("topic.planck.temperature"), 1000, 8000, self.temp,
            command=lambda v: setattr(self, "temp", v), fmt="{:.0f} K",
        )
        self.h_var, _ = self.add_slider(
            parent, self.t("topic.planck.hscale"), 0.05, 1.5, self.hscale,
            command=lambda v: setattr(self, "hscale", v), fmt="{:.2f}× h",
        )
        self.r_h = self.add_readout(parent, self.t("topic.planck.hvalue"))
        self.r_peak = self.add_readout(parent, self.t("topic.planck.peak"))
        self.r_quantum = self.add_readout(parent, self.t("topic.planck.quantum"))

    def reset(self):
        self.temp = 4000.0
        self.hscale = 1.0
        self.t_var.set(self.temp)
        self.h_var.set(self.hscale)

    def render(self):
        c = self.canvas
        lams = self.lam_grid()
        xs = self.nm(lams)
        # fixed reference scale (true h) so a growing curve visibly clips
        scale = self.planck_peak_value(self.temp) or 1.0
        p = self.make_plot(1.6)
        p.axes(self.t("topic.planck.xlabel"),
               self.t("topic.planck.ylabel"), XTICKS)

        # classical Rayleigh-Jeans for reference
        p.curve(xs, [bb.rayleigh_jeans_u(l, self.temp) / scale for l in lams],
                "#f87171", width=1, dash=(5, 3))
        # Planck with the (possibly reduced) constant
        h = self.hscale * bb.H
        p.curve(xs, [bb.planck_u(l, self.temp, h) / scale for l in lams],
                "#38bdf8", width=2)

        p.label(150, 1.5, self.t("topic.planck.classical_label"), "#f87171", anchor="w")
        p.label(1500, 0.7, self.t("topic.planck.quantum_label"), "#38bdf8", anchor="w")
        if self.hscale < 0.35:
            p.label(900, 1.2, self.t("topic.planck.limit_note"), "#fbbf24", anchor="w")

        # readouts
        self.r_h.set(f"{h:.2e} J·s")
        peak_nm = bb.wien_peak(self.temp) * 1e9
        self.r_peak.set(f"{peak_nm:.0f} nm")
        # quantum of energy at the peak frequency: E = h c / lambda
        e_peak = h * bb.C / (peak_nm * 1e-9)
        self.r_quantum.set(f"{e_peak / 1.602e-19:.2f} eV")
