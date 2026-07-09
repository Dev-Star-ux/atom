"""Chapter 3, Section 1, Topic 2 - de Broglie waves.

Louis de Broglie (1924) proposed that every moving particle has an associated
matter wave of wavelength

    λ = h / p = h / (mv).

If waves can behave as particles (photons), then particles can behave as waves.
The wavelength is negligible for macroscopic objects but becomes significant for
electrons and other light particles.
"""
import math
import tkinter as tk

from simulations.base import Simulation
import simulations.matter as matter


class DeBroglieSim(Simulation):
    title_key = "topic.de_broglie.title"
    desc_key = "topic.de_broglie.desc"

    def __init__(self, master, app):
        self.particle = "electron"
        self.velocity = 2.0e6   # m/s
        self._phase = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        from tkinter import ttk
        import tkinter as tk

        ttk.Label(parent, text=self.t("topic.de_broglie.particle"),
                  style="Panel.TLabel").pack(anchor="w", pady=(0, 2))
        self._part_keys = list(matter.PARTICLES.keys())
        self.part_var = tk.StringVar()
        combo = ttk.Combobox(
            parent, state="readonly", textvariable=self.part_var,
            values=[self.t("particle." + p) for p in self._part_keys],
        )
        combo.current(0)
        combo.pack(fill="x")
        combo.bind("<<ComboboxSelected>>", self._on_particle)

        # velocity slider in units of 10^6 m/s
        self.v_var, _ = self.add_slider(
            parent, self.t("topic.de_broglie.velocity"), 0.1, 10.0, self.velocity / 1e6,
            command=lambda v: setattr(self, "velocity", v * 1e6), fmt="{:.1f} ×10⁶ m/s",
        )
        self.r_momentum = self.add_readout(parent, self.t("topic.de_broglie.momentum"))
        self.r_lambda = self.add_readout(parent, self.t("topic.de_broglie.wavelength"))
        self.r_compare = self.add_readout(parent, self.t("topic.de_broglie.compare"))

    def _on_particle(self, _e):
        labels = [self.t("particle." + p) for p in self._part_keys]
        self.particle = self._part_keys[labels.index(self.part_var.get())]

    def reset(self):
        self.particle = "electron"
        self.velocity = 2.0e6
        self.part_var.set(self.t("particle.electron"))
        self.v_var.set(self.velocity / 1e6)
        self._phase = 0.0

    def tick(self, dt):
        if dt > 0:
            self._phase = (self._phase + dt * 4.0) % (2 * math.pi)

    def _mass(self):
        return matter.PARTICLES[self.particle]

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        mass = self._mass()
        p = matter.momentum(mass, self.velocity)
        lam = matter.de_broglie_wavelength(mass, self.velocity)
        lam_pm = lam * 1e12
        lam_nm = lam * 1e9

        self.r_momentum.set(f"p = {p:.3e} kg·m/s")
        if lam_pm >= 1.0:
            self.r_lambda.set(f"λ = {lam_pm:.2f} pm")
        elif lam_nm >= 0.001:
            self.r_lambda.set(f"λ = {lam_nm:.3f} nm")
        else:
            self.r_lambda.set(f"λ = {lam:.3e} m")

        if lam_pm < 1.0:
            self.r_compare.set(self.t("topic.de_broglie.tiny"))
        elif lam_pm < 1000:
            self.r_compare.set(self.t("topic.de_broglie.atomic"))
        else:
            self.r_compare.set(self.t("topic.de_broglie.macro"))

        cy = h * 0.45
        px_start = w * 0.12

        # matter wave (sine envelope along path)
        wave_pts = []
        n_pts = 120
        wave_scale = min(80.0, max(8.0, 200.0 / max(lam_pm, 0.01)))
        for i in range(n_pts):
            x = px_start + (w * 0.55) * i / (n_pts - 1)
            kx = 2 * math.pi * (x - px_start) / wave_scale + self._phase
            y = cy + 28 * math.sin(kx)
            wave_pts.extend([x, y])
        if len(wave_pts) >= 4:
            c.create_line(*wave_pts, fill="#38bdf8", width=2)

        # particle (localized packet)
        pkt_x = px_start + (w * 0.55) * (0.35 + 0.3 * math.sin(self._phase * 0.5))
        c.create_oval(pkt_x - 10, cy - 10, pkt_x + 10, cy + 10,
                      fill="#f472b6", outline="#fbcfe8", width=2)
        label = {"electron": "e⁻", "proton": "p⁺", "neutron": "n", "alpha": "α"}.get(self.particle, "?")
        c.create_text(pkt_x, cy, text=label, fill="#0b1220", font=self.font("small"))

        # velocity arrow
        c.create_line(pkt_x + 14, cy, pkt_x + 54, cy,
                      fill=col["accent2"], arrow=tk.LAST, width=2)
        c.create_text(pkt_x + 34, cy - 16, text=self.t("topic.de_broglie.velocity_label"),
                      fill=col["canvas_text"], font=self.font("tiny"))

        # formula panel
        c.create_text(w * 0.72, h * 0.20, text=self.t("topic.de_broglie.formula"),
                      fill=col["accent2"], font=self.font("bold"))
        c.create_text(w * 0.72, h * 0.32,
                      text=self.t("topic.de_broglie.formula_note"),
                      fill=col["canvas_text"], font=self.font("small"), width=200, justify="left")

        # λ scale bar (visual)
        bx, by = w * 0.12, h * 0.72
        bar_len = min(w * 0.5, max(40, wave_scale * 2))
        c.create_line(bx, by, bx + bar_len, by, fill=col["warn"], width=2)
        c.create_text(bx + bar_len / 2, by + 16,
                      text=self.t("topic.de_broglie.one_wavelength"),
                      fill=col["warn"], font=self.font("tiny"))

        c.create_text(w * 0.5, h - 22,
                      text=self.t("topic.de_broglie.note"),
                      fill=col["muted"], font=self.font("small"))
