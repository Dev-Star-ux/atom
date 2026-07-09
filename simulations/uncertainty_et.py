"""Chapter 3, Section 2, Topic 3 - Uncertainty between time and energy.

An excited state that lives only a short time Δt does not have a perfectly
defined energy: the spectral line acquires a natural width ΔE. The
energy–time uncertainty relation

    ΔE · Δt ≥ ħ/2

implies that shorter-lived states have broader energy distributions (and
vice versa). This is seen in the natural linewidth of atomic transitions.
"""
import math

from simulations.base import Simulation
from simulations.plot import Plot
import simulations.uncertainty as unc


class UncertaintyETSim(Simulation):
    title_key = "topic.uncertainty_et.title"
    desc_key = "topic.uncertainty_et.desc"

    def __init__(self, master, app):
        self.tau_fs = 5.0      # lifetime in femtoseconds
        self._t_anim = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        self.t_var, _ = self.add_slider(
            parent, self.t("topic.uncertainty_et.lifetime"), 0.5, 20.0, self.tau_fs,
            command=lambda v: setattr(self, "tau_fs", v), fmt="{:.1f} fs",
        )
        self.r_dt = self.add_readout(parent, self.t("topic.uncertainty_et.delta_t"))
        self.r_de = self.add_readout(parent, self.t("topic.uncertainty_et.delta_e"))
        self.r_product = self.add_readout(parent, self.t("topic.uncertainty_et.product"))
        self.r_width = self.add_readout(parent, self.t("topic.uncertainty_et.linewidth"))

    def _tau_s(self):
        return self.tau_fs * 1e-15

    def reset(self):
        self.tau_fs = 5.0
        self.t_var.set(self.tau_fs)
        self._t_anim = 0.0

    def tick(self, dt):
        if dt > 0:
            self._t_anim = (self._t_anim + dt) % (self._tau_s() * 6)

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        tau = self._tau_s()
        dE = unc.energy_uncertainty_eV(tau)
        product_ev = dE * tau

        self.r_dt.set(f"Δt ≈ {self.tau_fs:.1f} fs")
        self.r_de.set(f"ΔE ≈ {dE:.3f} eV")
        self.r_product.set(f"ΔE·Δt ≈ {product_ev:.3e} eV·s")
        self.r_width.set(f"Γ ≈ {2 * dE:.3f} eV (FWHM)")

        # decay |ψ(t)|² (top)
        box_t = (72, 28, w - 28, h * 0.40)
        t_max = 5.0 * tau
        ts = [t_max * i / 99 for i in range(100)]
        decay = [unc.decay_envelope(t, tau) for t in ts]
        p_t = Plot(c, box_t, (0, t_max * 1e15), (0, 1.1), col, self.font("small"))
        p_t.axes(self.t("topic.uncertainty_et.t_axis"),
                 self.t("topic.uncertainty_et.prob_axis"),
                 (0, t_max * 1e15 / 2, t_max * 1e15))
        p_t.curve([t * 1e15 for t in ts], decay, "#38bdf8", width=2)
        t_mark = self._t_anim * 1e15
        if t_mark <= t_max * 1e15:
            p_t.vline(t_mark, col["accent2"])

        c.create_text((box_t[0] + box_t[2]) / 2, 14,
                      text=self.t("topic.uncertainty_et.decay_title"),
                      fill=col["accent2"], font=self.font("small"))

        # energy Lorentzian (bottom)
        box_e = (72, h * 0.52, w - 28, h - 48)
        E0 = 2.0   # eV (example transition)
        gamma = 2.0 * dE
        Es = [E0 - 4 * gamma + 8 * gamma * i / 99 for i in range(100)]
        spec = [unc.lorentzian_energy(E, E0, gamma) for E in Es]
        ymax = max(spec) or 1.0
        p_e = Plot(c, box_e, (Es[0], Es[-1]), (0, ymax * 1.15), col, self.font("small"))
        p_e.axes(self.t("topic.uncertainty_et.e_axis"),
                 self.t("topic.uncertainty_et.intensity_axis"), ())
        p_e.curve(Es, spec, "#f472b6", width=2)
        p_e.vline(E0 - dE, col["warn"], dash=(3, 3))
        p_e.vline(E0 + dE, col["warn"], dash=(3, 3))

        c.create_text((box_e[0] + box_e[2]) / 2, h * 0.47,
                      text=self.t("topic.uncertainty_et.spectrum_title"),
                      fill=col["accent2"], font=self.font("small"))

        c.create_text(w * 0.5, h * 0.44,
                      text=self.t("topic.uncertainty_et.formula"),
                      fill=col["accent2"], font=self.font("bold"))
        c.create_text(w * 0.5, h - 14,
                      text=self.t("topic.uncertainty_et.note"),
                      fill=col["muted"], font=self.font("tiny"))
