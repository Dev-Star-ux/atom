"""Chapter 3, Section 3, Topic 3 - Double-slit electromagnetic interference.

Monochromatic light passing through two narrow slits produces an interference
pattern on a screen. Waves from the two slits superpose; path difference

    δ = d sin θ ≈ d y / L

gives intensity I ∝ cos²(π d y / (λ L)). This classic experiment demonstrates
the wave nature of light and, with single photons, the statistical buildup of
the same pattern.
"""
import math

from simulations.base import Simulation
from simulations.plot import Plot
import simulations.wavefunction as wf
import simulations.photo as photo


class DoubleSlitEMSim(Simulation):
    title_key = "topic.double_slit.title"
    desc_key = "topic.double_slit.desc"

    def __init__(self, master, app):
        self.freq = 7.0        # ×10¹⁴ Hz
        self.slit_sep = 80.0   # µm (arb. scale for sim)
        self.distance = 1.0    # m
        self._phase = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        self.f_var, _ = self.add_slider(
            parent, self.t("topic.double_slit.frequency"), 3, 15, self.freq,
            command=lambda v: setattr(self, "freq", v), fmt="{:.1f}",
        )
        self.d_var, _ = self.add_slider(
            parent, self.t("topic.double_slit.separation"), 30, 150, self.slit_sep,
            command=lambda v: setattr(self, "slit_sep", v), fmt="{:.0f} µm",
        )
        self.L_var, _ = self.add_slider(
            parent, self.t("topic.double_slit.distance"), 0.5, 2.5, self.distance,
            command=lambda v: setattr(self, "distance", v), fmt="{:.1f} m",
        )
        self.r_lam = self.add_readout(parent, self.t("topic.double_slit.wavelength"))
        self.r_fringe = self.add_readout(parent, self.t("topic.double_slit.fringe"))

    def _lam_m(self):
        return photo.freq_to_nm(self.freq) * 1e-9

    def _fringe_spacing(self):
        lam = self._lam_m()
        d = self.slit_sep * 1e-6
        if d <= 0:
            return 0.0
        return lam * self.distance / d

    def reset(self):
        self.freq = 7.0
        self.slit_sep = 80.0
        self.distance = 1.0
        self.f_var.set(self.freq)
        self.d_var.set(self.slit_sep)
        self.L_var.set(self.distance)
        self._phase = 0.0

    def tick(self, dt):
        if dt > 0:
            self._phase = (self._phase + dt * 2.0) % (2 * math.pi)

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        lam = self._lam_m()
        lam_nm = lam * 1e9
        d = self.slit_sep * 1e-6
        L = self.distance
        fringe = self._fringe_spacing()

        self.r_lam.set(f"{lam_nm:.0f} nm")
        self.r_fringe.set(f"{fringe * 1e3:.2f} mm" if fringe > 0 else "—")

        slit_x = w * 0.32
        cy = h * 0.40
        screen_x = w * 0.82

        # source waves
        for i in range(5):
            x = w * 0.06 + i * 22
            yoff = math.sin(self._phase + i * 0.5) * 4
            c.create_line(x, cy - 60 + yoff, x, cy + 60 + yoff, fill="#38bdf8", width=1)

        # barrier with two slits
        c.create_rectangle(slit_x - 6, cy - 70, slit_x + 6, cy - 12, fill="#475569", outline="")
        c.create_rectangle(slit_x - 6, cy + 12, slit_x + 6, cy + 70, fill="#475569", outline="")
        gap = self.slit_sep * 0.15
        c.create_rectangle(slit_x - 6, cy - gap, slit_x + 6, cy + gap, fill="#475569", outline="")
        c.create_line(slit_x - 6, cy - gap, slit_x + 6, cy - gap, fill=col["accent2"], width=3)
        c.create_line(slit_x - 6, cy + gap, slit_x + 6, cy + gap, fill=col["accent2"], width=3)
        c.create_text(slit_x, cy - 82, text=self.t("topic.double_slit.slits"),
                      fill=col["canvas_text"], font=self.font("tiny"))

        # path lines to screen centre
        c.create_line(slit_x, cy - gap, screen_x, cy - 30, fill="#334155", dash=(4, 4))
        c.create_line(slit_x, cy + gap, screen_x, cy + 30, fill="#334155", dash=(4, 4))

        # interference fringes on screen
        y_span = 0.04   # metres on screen (arb.)
        for row in range(int(cy - 75), int(cy + 75), 3):
            y_m = (row - cy) / (h * 0.75) * y_span
            I = wf.double_slit_intensity(y_m, d, lam, L)
            bright = int(30 + I * 200)
            c.create_line(screen_x, row, screen_x + 10, row,
                          fill=f"#{bright:02x}{bright:02x}{min(255, bright + 50):02x}")

        c.create_text(screen_x + 14, cy, text=self.t("topic.double_slit.screen"),
                      fill=col["canvas_text"], font=self.font("tiny"), anchor="w")

        # I(y) plot
        box = (60, h * 0.58, w - 28, h - 40)
        ys = [-y_span + 2 * y_span * i / 99 for i in range(100)]
        Is = [wf.double_slit_intensity(y, d, lam, L) for y in ys]
        p = Plot(c, box, (-y_span * 1e3, y_span * 1e3), (0, 1.1), col, self.font("small"))
        p.axes(self.t("topic.double_slit.y_axis"),
               self.t("topic.double_slit.intensity_axis"),
               (int(-y_span * 1e3), 0, int(y_span * 1e3)))
        p.curve([y * 1e3 for y in ys], Is, col["accent"], width=2)

        c.create_text(w * 0.5, h * 0.54,
                      text=self.t("topic.double_slit.formula"),
                      fill=col["accent2"], font=self.font("small"))
