"""Chapter 3, Section 3, Topic 1 - Wave–particle neutrality and probability.

Quantum objects are neither classical waves nor classical particles. The wave
function ψ does not describe a definite trajectory; |ψ|² gives the
*probability density* of finding the particle at each point. Many measurements
on identically prepared systems build up a statistical pattern — individual
outcomes are unpredictable, but the ensemble follows |ψ|².
"""
import math
import random

from simulations.base import Simulation
import simulations.uncertainty as unc
import simulations.wavefunction as wf


class WaveParticleProbabilitySim(Simulation):
    title_key = "topic.wave_particle_prob.title"
    desc_key = "topic.wave_particle_prob.desc"

    def __init__(self, master, app):
        self.mode = "wave"
        self.sigma = 50.0
        self.rate = 50.0
        self.hits = []
        self._phase = 0.0
        self._emit = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        from tkinter import ttk
        import tkinter as tk

        ttk.Label(parent, text=self.t("topic.wave_particle_prob.view"),
                  style="Panel.TLabel").pack(anchor="w", pady=(0, 2))
        self._modes = ("wave", "probability", "detections")
        self.mode_var = tk.StringVar()
        combo = ttk.Combobox(
            parent, state="readonly", textvariable=self.mode_var,
            values=[self.t("wpview." + m) for m in self._modes],
        )
        combo.current(0)
        combo.pack(fill="x")
        combo.bind("<<ComboboxSelected>>", self._on_mode)

        self.s_var, _ = self.add_slider(
            parent, self.t("topic.wave_particle_prob.width"), 20, 90, self.sigma,
            command=lambda v: setattr(self, "sigma", v), fmt="{:.0f}",
        )
        self.r_var, _ = self.add_slider(
            parent, self.t("topic.wave_particle_prob.rate"), 10, 100, self.rate,
            command=lambda v: setattr(self, "rate", v), fmt="{:.0f}%",
        )
        self.r_count = self.add_readout(parent, self.t("topic.wave_particle_prob.detections"))
        self.r_meaning = self.add_readout(parent, self.t("topic.wave_particle_prob.interpretation"))

    def _on_mode(self, _e):
        labels = [self.t("wpview." + m) for m in self._modes]
        self.mode = self._modes[labels.index(self.mode_var.get())]

    def _sigma_m(self):
        return self.sigma * 1e-10

    def reset(self):
        self.mode = "wave"
        self.sigma = 50.0
        self.rate = 50.0
        self.hits.clear()
        self.mode_var.set(self.t("wpview.wave"))
        self.s_var.set(self.sigma)
        self.r_var.set(self.rate)
        self._phase = 0.0

    def tick(self, dt):
        if dt <= 0:
            return
        self._phase = (self._phase + dt * 2.5) % (2 * math.pi)
        if self.mode == "detections" and self.rate > 0:
            self._emit += dt * self.rate * 0.08
            while self._emit >= 1.0:
                self._emit -= 1.0
                sm = self._sigma_m()
                x = random.gauss(0.0, sm)
                self.hits.append(x)
                if len(self.hits) > 600:
                    self.hits = self.hits[-600:]

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        cy = h * 0.45
        sm = self._sigma_m()

        self.r_count.set(str(len(self.hits)))
        if self.mode == "wave":
            self.r_meaning.set(self.t("topic.wave_particle_prob.mean_wave"))
            self._draw_wave(c, w, h, cy, col, sm)
        elif self.mode == "probability":
            self.r_meaning.set(self.t("topic.wave_particle_prob.mean_prob"))
            self._draw_probability(c, w, h, cy, col, sm)
        else:
            self.r_meaning.set(self.t("topic.wave_particle_prob.mean_detect"))
            self._draw_detections(c, w, h, cy, col, sm)

    def _x_pix(self, w, x_m, sm):
        return w * 0.5 + x_m / sm * (w * 0.35)

    def _draw_wave(self, c, w, h, cy, col, sm):
        pts = []
        for i in range(200):
            x_m = -3.5 * sm + 7.0 * sm * i / 199
            psi = unc.psi_gaussian(x_m, sm, k0=5e9)
            px = self._x_pix(w, x_m, sm)
            pts.extend([px, cy - 60 * psi / unc.psi_gaussian(0, sm, 5e9)])
        if len(pts) >= 4:
            c.create_line(*pts, fill="#38bdf8", width=2)
        c.create_text(w * 0.5, 28, text=self.t("topic.wave_particle_prob.wave_label"),
                      fill=col["accent2"], font=self.font("small"))
        c.create_text(w * 0.5, h - 28, text=self.t("topic.wave_particle_prob.wave_note"),
                      fill=col["muted"], font=self.font("small"))

    def _draw_probability(self, c, w, h, cy, col, sm):
        pts = []
        ymax = unc.prob_gaussian(0, sm)
        for i in range(200):
            x_m = -3.5 * sm + 7.0 * sm * i / 199
            p = unc.prob_gaussian(x_m, sm)
            px = self._x_pix(w, x_m, sm)
            pts.extend([px, cy + 80 - 75 * p / ymax])
        if len(pts) >= 4:
            c.create_line(*pts, fill="#f472b6", width=2)
        c.create_text(w * 0.5, 28, text=self.t("topic.wave_particle_prob.prob_label"),
                      fill=col["accent2"], font=self.font("small"))
        c.create_text(w * 0.5, cy + 100, text="P(x) = |ψ(x)|²",
                      fill=col["warn"], font=self.font("small"))
        c.create_text(w * 0.5, h - 28, text=self.t("topic.wave_particle_prob.prob_note"),
                      fill=col["muted"], font=self.font("small"))

    def _draw_detections(self, c, w, h, cy, col, sm):
        # theoretical curve (faint)
        for i in range(100):
            x_m = -3.5 * sm + 7.0 * sm * i / 99
            p = unc.prob_gaussian(x_m, sm)
            px = self._x_pix(w, x_m, sm)
            c.create_line(px, cy + 40, px, cy + 40 - int(35 * p / unc.prob_gaussian(0, sm)),
                          fill="#334155")

        for x_m in self.hits:
            px = self._x_pix(w, x_m, sm)
            py = cy - random.uniform(10, 50)
            c.create_oval(px - 3, py - 3, px + 3, py + 3, fill="#4ade80", outline="")

        c.create_text(w * 0.5, 28, text=self.t("topic.wave_particle_prob.detect_label"),
                      fill=col["accent2"], font=self.font("small"))
        c.create_text(w * 0.5, h - 28, text=self.t("topic.wave_particle_prob.detect_note"),
                      fill=col["muted"], font=self.font("small"))
