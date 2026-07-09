"""Chapter 3, Section 1, Topic 1 - Wave–particle duality of light.

Light is neither purely a wave nor purely a particle. In interference and
diffraction experiments it behaves as a wave; in the photoelectric effect and
Compton scattering it behaves as discrete photons. This complementarity — both
descriptions are needed, depending on the experiment — is central to quantum
mechanics.
"""
import math

from simulations.base import Simulation
import simulations.photo as photo

MODES = ("wave", "particle")


class LightDualitySim(Simulation):
    title_key = "topic.light_duality.title"
    desc_key = "topic.light_duality.desc"

    def __init__(self, master, app):
        self.mode = "wave"
        self.freq = 7.0
        self.intensity = 60.0
        self._phase = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        from tkinter import ttk
        import tkinter as tk

        ttk.Label(parent, text=self.t("topic.light_duality.experiment"),
                  style="Panel.TLabel").pack(anchor="w", pady=(0, 2))
        self._mode_keys = list(MODES)
        self.mode_var = tk.StringVar()
        combo = ttk.Combobox(
            parent, state="readonly", textvariable=self.mode_var,
            values=[self.t("duality." + m) for m in self._mode_keys],
        )
        combo.current(0)
        combo.pack(fill="x")
        combo.bind("<<ComboboxSelected>>", self._on_mode)

        self.f_var, _ = self.add_slider(
            parent, self.t("topic.light_duality.frequency"), 3, 15, self.freq,
            command=lambda v: setattr(self, "freq", v), fmt="{:.1f}",
        )
        self.i_var, _ = self.add_slider(
            parent, self.t("topic.light_duality.intensity"), 5, 100, self.intensity,
            command=lambda v: setattr(self, "intensity", v), fmt="{:.0f}%",
        )
        self.r_behaviour = self.add_readout(parent, self.t("topic.light_duality.behaviour"))
        self.r_evidence = self.add_readout(parent, self.t("topic.light_duality.evidence"))

    def _on_mode(self, _e):
        labels = [self.t("duality." + m) for m in self._mode_keys]
        self.mode = self._mode_keys[labels.index(self.mode_var.get())]

    def reset(self):
        self.mode = "wave"
        self.freq = 7.0
        self.intensity = 60.0
        self.mode_var.set(self.t("duality.wave"))
        self.f_var.set(self.freq)
        self.i_var.set(self.intensity)
        self._phase = 0.0

    def tick(self, dt):
        if dt > 0:
            self._phase = (self._phase + dt * 3.0) % (2 * math.pi)

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        lam_nm = photo.freq_to_nm(self.freq)

        if self.mode == "wave":
            self.r_behaviour.set(self.t("topic.light_duality.wave_behaviour"))
            self.r_evidence.set(self.t("topic.light_duality.wave_evidence"))
            self._draw_wave(c, w, h, col, lam_nm)
        else:
            self.r_behaviour.set(self.t("topic.light_duality.particle_behaviour"))
            self.r_evidence.set(self.t("topic.light_duality.particle_evidence"))
            self._draw_particle(c, w, h, col)

    def _draw_wave(self, c, w, h, col, lam_nm):
        c.create_text(w * 0.5, 28, text=self.t("topic.light_duality.wave_title"),
                      fill=col["accent2"], font=self.font("small"))

        # double-slit interference
        slit_x = w * 0.35
        cy = h * 0.42
        c.create_rectangle(slit_x - 4, cy - 50, slit_x + 4, cy - 8, fill="#475569", outline="")
        c.create_rectangle(slit_x - 4, cy + 8, slit_x + 4, cy + 50, fill="#475569", outline="")
        c.create_text(slit_x, cy - 62, text=self.t("topic.light_duality.slits"),
                      fill=col["canvas_text"], font=self.font("tiny"))

        # incoming plane waves
        for i in range(6):
            x = w * 0.08 + i * 28 + math.sin(self._phase + i) * 4
            c.create_line(x, cy - 70, x, cy + 70, fill="#38bdf8", width=1)

        # interference fringes on screen
        screen_x = w * 0.82
        c.create_line(screen_x, cy - 80, screen_x, cy + 80, fill="#64748b")
        c.create_text(screen_x + 12, cy, text=self.t("topic.light_duality.screen"),
                      fill=col["canvas_text"], font=self.font("tiny"), anchor="w")

        k = 2 * math.pi / max(30.0, lam_nm * 0.08)
        for y in range(int(cy - 75), int(cy + 75), 3):
            path_diff = (y - cy) * 0.12
            amp = (math.cos(k * path_diff + self._phase) + 1) * 0.5
            brightness = int(40 + amp * 180)
            c.create_line(screen_x, y, screen_x + 8, y,
                          fill=f"#{brightness:02x}{brightness:02x}{min(255, brightness + 40):02x}")

        c.create_text(w * 0.5, h - 36,
                      text=self.t("topic.light_duality.wave_note"),
                      fill=col["muted"], font=self.font("small"))

    def _draw_particle(self, c, w, h, col):
        c.create_text(w * 0.5, 28, text=self.t("topic.light_duality.particle_title"),
                      fill=col["accent2"], font=self.font("small"))

        mx = w * 0.42
        cy = h * 0.42
        c.create_rectangle(mx, cy - 30, mx + 14, cy + 30, fill="#64748b", outline="")
        c.create_text(mx + 7, cy + 44, text=self.t("topic.light_duality.metal"),
                      fill=col["canvas_text"], font=self.font("tiny"))

        pcolor = photo.photon_color(self.freq)
        n_photons = max(1, int(self.intensity / 20))
        for i in range(n_photons):
            y = cy - 40 + i * (80 / max(1, n_photons - 1)) if n_photons > 1 else cy
            px = w * 0.12 + (i % 3) * 40 + math.sin(self._phase + i) * 8
            c.create_oval(px - 5, y - 5, px + 5, y + 5, fill=pcolor, outline="#67e8f9", width=2)
            c.create_line(px + 5, y, mx - 4, y, fill=pcolor, width=2, dash=(4, 3))

        ke = max(0.0, photo.photon_energy_eV(self.freq) - photo.MATERIALS["sodium"])
        if ke > 0:
            for i in range(min(4, n_photons)):
                ey = cy - 20 + i * 14
                c.create_oval(mx + 20, ey - 3, mx + 26, ey + 3, fill="#67e8f9", outline="")
                c.create_line(mx + 26, ey, mx + 60 + i * 8, ey - 10, fill="#67e8f9", width=1)

        c.create_text(w * 0.5, h * 0.72,
                      text=self.t("topic.light_duality.particle_note"),
                      fill=col["canvas_text"], font=self.font("small"), width=w * 0.85, justify="center")
        c.create_text(w * 0.5, h - 28,
                      text=self.t("topic.light_duality.complement"),
                      fill=col["accent2"], font=self.font("small"))
