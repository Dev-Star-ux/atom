"""Chapter 2, Section 5, Topic 4 - Compton effect.

When an X-ray photon collides with a nearly free electron the photon is
scattered at angle θ with a longer wavelength. The shift

    Δλ = (h / mc)(1 − cos θ) = λ_C (1 − cos θ)

depends only on θ, not on the initial wavelength — direct evidence that photons
carry momentum as well as energy. The recoiling electron balances momentum
and energy.
"""
import math
import tkinter as tk

from simulations.base import Simulation
from simulations.plot import Plot
import simulations.xray as xr


class ComptonSim(Simulation):
    title_key = "topic.compton.title"
    desc_key = "topic.compton.desc"

    def __init__(self, master, app):
        self.lam = 50.0       # pm incident wavelength
        self.theta = 60.0     # scattering angle (degrees)
        self._pulse = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        self.l_var, _ = self.add_slider(
            parent, self.t("topic.compton.wavelength"), 10, 150, self.lam,
            command=lambda v: setattr(self, "lam", v), fmt="{:.0f} pm",
        )
        self.t_var, _ = self.add_slider(
            parent, self.t("topic.compton.angle"), 0, 180, self.theta,
            command=lambda v: setattr(self, "theta", v), fmt="{:.0f}°",
        )
        self.r_shift = self.add_readout(parent, self.t("topic.compton.shift"))
        self.r_scattered = self.add_readout(parent, self.t("topic.compton.scattered"))
        self.r_e_energy = self.add_readout(parent, self.t("topic.compton.electron_ke"))
        self.r_lambda_c = self.add_readout(parent, self.t("topic.compton.lambda_c"))

    def reset(self):
        self.lam = 50.0
        self.theta = 60.0
        self.l_var.set(self.lam)
        self.t_var.set(self.theta)
        self._pulse = 0.0

    def tick(self, dt):
        if dt > 0:
            self._pulse = (self._pulse + dt) % 2.0

    def _theta_rad(self):
        return math.radians(self.theta)

    def _shift(self):
        return xr.compton_shift_pm(self._theta_rad())

    def _lam_out(self):
        return xr.scattered_lambda_pm(self.lam, self._theta_rad())

    def _electron_ke(self):
        E_in = xr.energy_keV_from_lambda_pm(self.lam)
        E_out = xr.energy_keV_from_lambda_pm(self._lam_out())
        return max(0.0, E_in - E_out)

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        theta = self._theta_rad()
        shift = self._shift()
        lam_out = self._lam_out()
        ke = self._electron_ke()

        self.r_shift.set(f"Δλ = {shift:.3f} pm")
        self.r_scattered.set(f"λ' = {lam_out:.2f} pm")
        self.r_e_energy.set(f"{ke:.3f} keV")
        self.r_lambda_c.set(f"{xr.LAMBDA_C_PM:.3f} pm")

        cx, cy = w * 0.38, h * 0.42
        ex, ey = cx, cy

        # electron at rest (before collision)
        c.create_oval(ex - 10, ey - 10, ex + 10, ey + 10, fill="#64748b", outline="#94a3b8")
        c.create_text(ex, ey + 22, text="e⁻", fill=col["canvas_text"], font=self.font("small"))

        # incident photon (from left)
        inc_len = 120
        t_anim = min(1.0, self._pulse / 0.5) if self._pulse < 0.5 else 1.0
        ix = ex - inc_len * (1 - t_anim * 0.3)
        c.create_line(ix - inc_len, ey, ix, ey, fill="#38bdf8", width=3, arrow=tk.LAST)
        c.create_text(ix - inc_len - 10, ey - 14,
                      text=self.t("topic.compton.incident", lam=f"{self.lam:.0f}"),
                      fill="#38bdf8", font=self.font("tiny"), anchor="e")

        # scattered photon at angle θ (measured from incident direction)
        out_len = 110
        ox = ex + out_len * math.cos(theta)
        oy = ey - out_len * math.sin(theta)
        c.create_line(ex, ey, ox, oy, fill="#fbbf24", width=3, arrow=tk.LAST)
        c.create_text(ox + 12, oy - 8,
                      text=self.t("topic.compton.out", lam=f"{lam_out:.1f}"),
                      fill="#fbbf24", font=self.font("tiny"), anchor="w")

        # recoiling electron
        phi = theta / 2 + 0.4
        er_len = 50 + ke * 8
        erx = ex - er_len * math.cos(phi)
        ery = ey + er_len * math.sin(phi)
        c.create_line(ex, ey, erx, ery, fill="#f472b6", width=2, arrow=tk.LAST)
        c.create_text(erx - 10, ery + 14, text=self.t("topic.compton.recoil"),
                      fill="#f472b6", font=self.font("tiny"))

        # angle arc
        c.create_arc(ex - 40, ey - 40, ex + 40, ey + 40,
                     start=0, extent=-self.theta, outline=col["accent2"], style=tk.ARC)
        c.create_text(ex + 50, ey - 18, text=f"θ = {self.theta:.0f}°",
                      fill=col["accent2"], font=self.font("small"))

        # formula
        c.create_text(w * 0.72, h * 0.18, text=self.t("topic.compton.formula"),
                      fill=col["accent2"], font=self.font("bold"))
        c.create_text(w * 0.72, h * 0.28,
                      text=self.t("topic.compton.formula_val",
                                  shift=f"{shift:.3f}", theta=f"{self.theta:.0f}"),
                      fill=col["canvas_text"], font=self.font("small"))

        # Δλ vs θ plot
        box = (60, h * 0.58, w - 28, h - 40)
        thetas = [math.radians(t) for t in range(0, 181, 3)]
        shifts = [xr.compton_shift_pm(t) for t in thetas]
        ymax = xr.LAMBDA_C_PM * 2 * 1.1
        p = Plot(c, box, (0, 180), (0, ymax), col, self.font("small"))
        p.axes(self.t("topic.compton.theta_axis"),
               self.t("topic.compton.shift_axis"),
               (0, 45, 90, 135, 180))
        xs = [math.degrees(t) for t in thetas]
        p.curve(xs, shifts, col["accent"], width=2)
        p.label(self.theta, self._shift(), "●", col["good"], anchor="s")

        c.create_text(w * 0.5, h * 0.54,
                      text=self.t("topic.compton.note"),
                      fill=col["muted"], font=self.font("tiny"))
