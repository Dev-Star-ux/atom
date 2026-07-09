"""Chapter 2, Section 4, Topic 1 - Disadvantages of the planetary model.

Rutherford's nuclear model places electrons in classical orbits around a tiny
nucleus, but classical electrodynamics predicts three fatal problems:

  1. Radiative collapse — an accelerating charge must radiate and spiral inward.
  2. Continuous spectra — any orbit radius is allowed, so all wavelengths
     should appear; atoms instead emit sharp lines.
  3. Wrong stability — there is no reason the electron should sit at one
     particular radius rather than another.

Step through each problem and see why a new theory (Bohr's) was needed.
"""
import math

from simulations.base import Simulation
import simulations.atom as atom

PROBLEMS = ("radiation", "spectrum", "stability")


class PlanetaryDisadvantagesSim(Simulation):
    title_key = "topic.planetary_flaws.title"
    desc_key = "topic.planetary_flaws.desc"

    def __init__(self, master, app):
        self.problem = "radiation"
        self.angle = 0.0
        self.radius = 120.0
        self.energy = 100.0
        self.collapsed = False
        self._spec_phase = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        from tkinter import ttk
        import tkinter as tk

        ttk.Label(parent, text=self.t("topic.planetary_flaws.problem"),
                  style="Panel.TLabel").pack(anchor="w", pady=(0, 2))
        self._prob_keys = list(PROBLEMS)
        self.prob_var = tk.StringVar()
        combo = ttk.Combobox(
            parent, state="readonly", textvariable=self.prob_var,
            values=[self.t("problem." + p) for p in self._prob_keys],
        )
        combo.current(0)
        combo.pack(fill="x")
        combo.bind("<<ComboboxSelected>>", self._on_problem)

        self.r_energy = self.add_readout(parent, self.t("topic.planetary_flaws.energy"))
        self.r_radius = self.add_readout(parent, self.t("topic.planetary_flaws.orbit_radius"))
        self.r_verdict = self.add_readout(parent, self.t("topic.planetary_flaws.verdict"))

    def _on_problem(self, _e):
        labels = [self.t("problem." + p) for p in self._prob_keys]
        self.problem = self._prob_keys[labels.index(self.prob_var.get())]
        self.reset()

    def reset(self):
        self.angle = 0.0
        self.radius = 120.0
        self.energy = 100.0
        self.collapsed = False
        self._spec_phase = 0.0
        self.prob_var.set(self.t("problem." + self.problem))

    def tick(self, dt):
        if dt <= 0:
            return
        self._spec_phase = (self._spec_phase + dt) % (2 * math.pi)
        if self.problem == "radiation" and not self.collapsed:
            self.angle += 2.8 * dt
            self.radius -= 32.0 * dt
            self.energy = max(0.0, self.energy - 28.0 * dt)
            if self.radius <= 16:
                self.collapsed = True
        elif self.problem == "stability":
            self.angle += 1.6 * dt

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        cx, cy = w * 0.36, h * 0.46

        if self.problem == "radiation":
            self._draw_radiation(c, w, h, cx, cy, col)
        elif self.problem == "spectrum":
            self._draw_spectrum(c, w, h, col)
        else:
            self._draw_stability(c, w, h, cx, cy, col)

    def _draw_radiation(self, c, w, h, cx, cy, col):
        if not self.collapsed:
            ex = cx + self.radius * math.cos(self.angle)
            ey = cy + self.radius * 0.75 * math.sin(self.angle)
            c.create_oval(cx - self.radius, cy - self.radius * 0.75,
                          cx + self.radius, cy + self.radius * 0.75, outline="#233047")
            for ring in range(3):
                rr = self.radius + 18 + ring * 14
                c.create_oval(cx - rr, cy - rr * 0.75, cx + rr, cy + rr * 0.75,
                              outline="#7f1d1d", dash=(4, 6))
            c.create_line(cx, cy, ex, ey, fill="#475569", dash=(3, 3))
            c.create_oval(ex - 7, ey - 7, ex + 7, ey + 7, fill="#38bdf8", outline="#7dd3fc")
            c.create_oval(cx - 9, cy - 9, cx + 9, cy + 9, fill="#ef4444", outline="#fecaca")
            c.create_text(cx, cy, text="+", fill="#fff", font=self.font("base"))
        else:
            c.create_oval(cx - 10, cy - 10, cx + 10, cy + 10, fill="#ef4444", outline="#fecaca")
            c.create_text(cx, cy, text="+", fill="#fff", font=self.font("base"))
            c.create_text(cx, cy + 28, text=self.t("topic.planetary_flaws.collapsed"),
                          fill=col["bad"], font=self.font("small"))

        # energy decay bar
        bx0, by = w * 0.62, h * 0.22
        bw, bh = w * 0.28, 18
        c.create_rectangle(bx0, by, bx0 + bw, by + bh, outline="#334155")
        fill = bx0 + bw * self.energy / 100.0
        c.create_rectangle(bx0, by, fill, by + bh, fill=col["accent"], outline="")
        c.create_text(bx0 + bw / 2, by - 14, text=self.t("topic.planetary_flaws.energy_loss"),
                      fill=col["accent2"], font=self.font("small"))

        c.create_text(w * 0.62, h * 0.42, text=self.t("topic.planetary_flaws.rad_note"),
                      fill=col["canvas_text"], font=self.font("small"), width=w * 0.32, justify="left")

        self.r_energy.set(f"{self.energy:.0f} %")
        self.r_radius.set(f"{self.radius:.0f} px" if not self.collapsed else "0")
        self.r_verdict.set(self.t("topic.planetary_flaws.verdict_rad"))

    def _draw_spectrum(self, c, w, h, col):
        mid = w * 0.5
        top, bot = h * 0.18, h * 0.42

        c.create_text(w * 0.25, top - 16, text=self.t("topic.planetary_flaws.classical_pred"),
                      fill=col["warn"], font=self.font("small"))
        c.create_text(w * 0.75, top - 16, text=self.t("topic.planetary_flaws.observed"),
                      fill=col["good"], font=self.font("small"))

        # classical: continuous rainbow
        x0, x1 = w * 0.06, mid - 20
        steps = 80
        for i in range(steps):
            nm = 380 + (700 - 380) * i / steps
            xa = x0 + (x1 - x0) * i / steps
            xb = x0 + (x1 - x0) * (i + 1) / steps
            c.create_rectangle(xa, top, xb, bot, fill=atom.wavelength_to_rgb(nm), outline="")

        # observed: H lines only
        x0, x1 = mid + 20, w * 0.94
        for nm, intensity, label in atom.HYDROGEN_LINES:
            t = (nm - 380) / (700 - 380)
            px = x0 + (x1 - x0) * t
            hw = 2 + int(intensity * 4)
            c.create_rectangle(px - hw, top + 4, px + hw, bot - 4,
                               fill=atom.wavelength_to_rgb(nm), outline="")
            c.create_text(px, bot + 14, text=label, fill=col["canvas_text"], font=self.font("tiny"))

        c.create_text(w * 0.5, h * 0.58, text=self.t("topic.planetary_flaws.spec_note"),
                      fill=col["canvas_text"], font=self.font("small"), width=w * 0.85, justify="center")

        self.r_energy.set("—")
        self.r_radius.set(self.t("topic.planetary_flaws.any_radius"))
        self.r_verdict.set(self.t("topic.planetary_flaws.verdict_spec"))

    def _draw_stability(self, c, w, h, cx, cy, col):
        # many arbitrary orbit sizes — no preferred radius
        for i, r in enumerate((50, 75, 95, 120, 150, 180)):
            phase = self.angle + i * 0.7
            c.create_oval(cx - r, cy - r * 0.72, cx + r, cy + r * 0.72, outline="#334155")
            ex = cx + r * math.cos(phase)
            ey = cy + r * 0.72 * math.sin(phase)
            alpha = 0.4 + 0.1 * i
            ec = "#38bdf8" if i == 3 else "#475569"
            c.create_oval(ex - 5, ey - 5, ex + 5, ey + 5, fill=ec, outline="")

        c.create_oval(cx - 9, cy - 9, cx + 9, cy + 9, fill="#ef4444", outline="#fecaca")
        c.create_text(cx, cy, text="+", fill="#fff", font=self.font("base"))
        c.create_text(w * 0.5, h * 0.78, text=self.t("topic.planetary_flaws.stab_note"),
                      fill=col["canvas_text"], font=self.font("small"), width=w * 0.8, justify="center")

        self.r_energy.set(self.t("topic.planetary_flaws.continuous_energies"))
        self.r_radius.set(self.t("topic.planetary_flaws.no_selection"))
        self.r_verdict.set(self.t("topic.planetary_flaws.verdict_stab"))
