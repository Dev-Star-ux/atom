"""Chapter 3, Section 2, Topic 2 - Uncertainty between position and momentum.

Heisenberg (1927): a particle cannot have both position and momentum sharply
defined at the same time. For any quantum state

    Δx · Δp ≥ ħ/2.

A Gaussian wave packet achieves the minimum. Narrowing the packet in space
(Δx ↓) necessarily broadens the momentum distribution (Δp ↑).
"""
import math

from simulations.base import Simulation
from simulations.plot import Plot
import simulations.uncertainty as unc
from simulations.atom import H_BAR


class UncertaintyXPSim(Simulation):
    title_key = "topic.uncertainty_xp.title"
    desc_key = "topic.uncertainty_xp.desc"

    def __init__(self, master, app):
        self.sigma = 1.0e-10   # metres (≈ 1 Å)
        super().__init__(master, app)

    def build_controls(self, parent):
        self.s_var, _ = self.add_slider(
            parent, self.t("topic.uncertainty_xp.width"), 0.2, 3.0, self.sigma * 1e10,
            command=lambda v: setattr(self, "sigma", v * 1e-10), fmt="{:.2f} Å",
        )
        self.r_dx = self.add_readout(parent, self.t("topic.uncertainty_xp.delta_x"))
        self.r_dp = self.add_readout(parent, self.t("topic.uncertainty_xp.delta_p"))
        self.r_product = self.add_readout(parent, self.t("topic.uncertainty_xp.product"))
        self.r_limit = self.add_readout(parent, self.t("topic.uncertainty_xp.limit"))

    def reset(self):
        self.sigma = 1.0e-10
        self.s_var.set(self.sigma * 1e10)

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        dx = unc.gaussian_dx(self.sigma)
        dp = unc.gaussian_dp(self.sigma)
        product = unc.xp_product(self.sigma)
        limit = H_BAR / 2.0

        self.r_dx.set(f"{dx * 1e10:.2f} Å")
        self.r_dp.set(f"{dp:.3e} kg·m/s")
        self.r_product.set(f"{product:.3e} J·s")
        self.r_limit.set(f"ħ/2 = {limit:.3e} J·s")

        # |ψ(x)|²
        box_x = (72, 30, w - 28, h * 0.40)
        x_range = 4.0 * self.sigma
        xs = [-x_range + 2 * x_range * i / 99 for i in range(100)]
        ps = [unc.prob_gaussian(x, self.sigma) for x in xs]
        ymax = max(ps) or 1.0
        p_pos = Plot(c, box_x, (-x_range, x_range), (0, ymax * 1.15), col, self.font("small"))
        p_pos.axes(self.t("topic.uncertainty_xp.x_axis"),
                   self.t("topic.uncertainty_xp.prob_axis"), ())
        p_pos.curve(xs, ps, "#38bdf8", width=2)
        p_pos.vline(-dx, col["warn"], dash=(3, 3))
        p_pos.vline(dx, col["warn"], dash=(3, 3))

        c.create_text((box_x[0] + box_x[2]) / 2, 16,
                      text=self.t("topic.uncertainty_xp.pos_title"),
                      fill=col["accent2"], font=self.font("small"))

        # |φ(p)|²
        box_p = (72, h * 0.52, w - 28, h - 48)
        p_range = 4.0 * dp
        p_pts = [-p_range + 2 * p_range * i / 99 for i in range(100)]
        pp = [math.exp(-p * p / (2 * dp * dp)) for p in p_pts]
        ymax_p = max(pp) or 1.0
        p_mom = Plot(c, box_p, (-p_range, p_range), (0, ymax_p * 1.15), col, self.font("small"))
        p_mom.axes(self.t("topic.uncertainty_xp.p_axis"),
                   self.t("topic.uncertainty_xp.prob_axis"), ())
        p_mom.curve(p_pts, pp, "#f472b6", width=2)
        p_mom.vline(-dp, col["warn"], dash=(3, 3))
        p_mom.vline(dp, col["warn"], dash=(3, 3))

        c.create_text((box_p[0] + box_p[2]) / 2, h * 0.47,
                      text=self.t("topic.uncertainty_xp.mom_title"),
                      fill=col["accent2"], font=self.font("small"))

        c.create_text(w * 0.5, h * 0.44,
                      text=self.t("topic.uncertainty_xp.formula"),
                      fill=col["accent2"], font=self.font("bold"))
        ok = product >= limit * 0.99
        c.create_text(w * 0.5, h - 14,
                      text=self.t("topic.uncertainty_xp.saturated") if ok
                      else self.t("topic.uncertainty_xp.above"),
                      fill=col["good"] if ok else col["warn"], font=self.font("tiny"))
