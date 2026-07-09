"""Chapter 2, Section 2, Topic 2 - Wave theory of light and the photoelectric effect.

Classical wave theory makes three predictions that all turn out to be WRONG:
  1. The electron energy should grow with the light's intensity (amplitude).
  2. Light of any frequency should work if it is bright enough (no threshold).
  3. Dim light should show a time delay while energy is slowly absorbed.

Experiment shows the opposite: the maximum energy depends only on frequency,
there is a threshold frequency, and emission is essentially instantaneous. This
view puts the two side by side so the conflict is explicit.
"""
import math

from simulations.base import Simulation
import simulations.photo as photo

WORK = photo.MATERIALS["sodium"]


class WaveTheorySim(Simulation):
    title_key = "topic.wave_theory.title"
    desc_key = "topic.wave_theory.desc"

    def __init__(self, master, app):
        self.freq = 7.0
        self.intensity = 60.0
        self.accum = 0.0     # classical energy-accumulation phase
        super().__init__(master, app)

    def build_controls(self, parent):
        self.f_var, _ = self.add_slider(
            parent, self.t("topic.wave_theory.frequency"), 3, 15, self.freq,
            command=lambda v: setattr(self, "freq", v), fmt="{:.1f}",
        )
        self.i_var, _ = self.add_slider(
            parent, self.t("topic.wave_theory.intensity"), 5, 100, self.intensity,
            command=lambda v: setattr(self, "intensity", v), fmt="{:.0f}%",
        )
        self.r_delay = self.add_readout(parent, self.t("topic.wave_theory.delay"))
        self.r_actual = self.add_readout(parent, self.t("topic.wave_theory.actual_ke"))

    def reset(self):
        self.freq = 7.0
        self.intensity = 60.0
        self.accum = 0.0
        self.f_var.set(self.freq)
        self.i_var.set(self.intensity)

    def tick(self, dt):
        # classical accumulation fills faster with brighter light
        self.accum += dt * self.intensity / 100.0 * 0.55
        if self.accum >= 1.0:
            self.accum = 0.0
        # predicted classical delay ~ inversely proportional to intensity
        delay = 60.0 / max(1.0, self.intensity)
        self.r_delay.set(self.t("topic.wave_theory.delay_val", s=f"{delay:.1f}"))
        ke = max(0.0, photo.photon_energy_eV(self.freq) - WORK)
        self.r_actual.set(f"{ke:.2f} eV" if ke > 0 else self.t("topic.wave_theory.none"))

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        midx = w / 2
        c.create_line(midx, 20, midx, h - 20, fill="#334155", dash=(4, 4))
        c.create_text(w * 0.25, 24, text=self.t("topic.wave_theory.left_title"),
                      fill="#f87171", font=self.font("base"))
        c.create_text(w * 0.75, 24, text=self.t("topic.wave_theory.right_title"),
                      fill="#4ade80", font=self.font("base"))

        # ---- classical (left) ----------------------------------------
        # predicted KE grows with intensity, ignores frequency
        classical_ke = self.intensity / 100.0 * 3.0
        self._bar(c, w * 0.16, h * 0.62, self.intensity / 100.0, "#f87171",
                  self.t("topic.wave_theory.pred_ke"))
        c.create_text(w * 0.25, h * 0.70,
                      text=self.t("topic.wave_theory.claim1"),
                      fill=col["canvas_text"], font=self.font("small"))

        # energy-accumulation meter (predicted delay for dim light)
        mx, my = w * 0.34, h * 0.30
        c.create_rectangle(mx, my, mx + 22, my + 120, outline="#f87171")
        fill_h = 120 * self.accum
        c.create_rectangle(mx, my + 120 - fill_h, mx + 22, my + 120,
                           fill="#f87171", outline="")
        c.create_text(w * 0.25, h * 0.30 - 16,
                      text=self.t("topic.wave_theory.accumulate"),
                      fill=col["canvas_text"], font=self.font("small"))
        c.create_text(w * 0.20, h * 0.86,
                      text=self.t("topic.wave_theory.claim3"),
                      fill=col["canvas_text"], font=self.font("small"))

        # ---- experiment (right) --------------------------------------
        ke = max(0.0, photo.photon_energy_eV(self.freq) - WORK)
        self._bar(c, w * 0.66, h * 0.62, min(1.0, ke / 3.0), "#4ade80",
                  self.t("topic.wave_theory.real_ke"))
        c.create_text(w * 0.75, h * 0.70,
                      text=self.t("topic.wave_theory.claim2"),
                      fill=col["canvas_text"], font=self.font("small"))

        # instant photon -> electron
        f14 = self.freq
        pcolor = photo.photon_color(f14)
        py = h * 0.34
        c.create_line(w * 0.60, py, w * 0.72, py, fill=pcolor, width=3, arrow="last")
        if ke > 0:
            c.create_oval(w * 0.73, py - 4, w * 0.73 + 8, py + 4, fill="#67e8f9", outline="")
            c.create_line(w * 0.745, py, w * 0.85, py - 24, fill="#67e8f9", width=2, arrow="last")
            c.create_text(w * 0.80, h * 0.30, text=self.t("topic.wave_theory.instant"),
                          fill=col["canvas_text"], font=self.font("small"))
        else:
            c.create_text(w * 0.80, py, text=self.t("topic.wave_theory.no_eject"),
                          fill="#f87171", font=self.font("small"), anchor="w")
        c.create_text(w * 0.75, h * 0.86,
                      text=self.t("topic.wave_theory.threshold_note"),
                      fill=col["canvas_text"], font=self.font("small"))

    def _bar(self, c, x, base_y, frac, color, label):
        width = 46
        height = 150 * max(0.0, min(1.0, frac))
        c.create_rectangle(x, base_y - 150, x + width, base_y, outline="#334155")
        c.create_rectangle(x, base_y - height, x + width, base_y, fill=color, outline="")
        c.create_text(x + width / 2, base_y + 14, text=label,
                      fill=self.colors["canvas_text"], font=self.font("small"))
