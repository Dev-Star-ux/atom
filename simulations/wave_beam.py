"""Chapter 3, Section 2, Topic 1 - Wave beam.

A matter wave can be pictured as a beam or wave packet: oscillations of
wavelength λ = h/p inside an envelope that limits where the particle is likely
to be found. A narrower beam (better localised in space) requires a wider
spread of wavelengths and momenta — the seed of the uncertainty principle.
"""
import math
import tkinter as tk

from simulations.base import Simulation
import simulations.uncertainty as unc


class WaveBeamSim(Simulation):
    title_key = "topic.wave_beam.title"
    desc_key = "topic.wave_beam.desc"

    def __init__(self, master, app):
        self.sigma = 40.0      # beam width (px scale → arb. metres)
        self.wavelength = 28.0  # carrier wavelength (px)
        self._phase = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        self.s_var, _ = self.add_slider(
            parent, self.t("topic.wave_beam.width"), 10, 100, self.sigma,
            command=lambda v: setattr(self, "sigma", v), fmt="{:.0f}",
        )
        self.w_var, _ = self.add_slider(
            parent, self.t("topic.wave_beam.wavelength"), 10, 60, self.wavelength,
            command=lambda v: setattr(self, "wavelength", v), fmt="{:.0f} px",
        )
        self.r_spread = self.add_readout(parent, self.t("topic.wave_beam.spread"))
        self.r_k = self.add_readout(parent, self.t("topic.wave_beam.k_spread"))

    def reset(self):
        self.sigma = 40.0
        self.wavelength = 28.0
        self.s_var.set(self.sigma)
        self.w_var.set(self.wavelength)
        self._phase = 0.0

    def tick(self, dt):
        if dt > 0:
            self._phase = (self._phase + dt * 3.0) % (2 * math.pi)

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        cy = h * 0.40
        sigma_m = self.sigma * 1e-10   # arb. scale for readouts

        self.r_spread.set(f"Δx ≈ {sigma_m:.2e} m")
        self.r_k.set(f"Δk ≈ {unc.gaussian_dk(sigma_m):.2e} m⁻¹")

        c.create_text(w * 0.5, 24, text=self.t("topic.wave_beam.title_canvas"),
                      fill=col["accent2"], font=self.font("small"))

        # envelope (|ψ|²)
        pts_top, pts_bot = [], []
        n = 160
        for i in range(n):
            x = w * 0.08 + (w * 0.84) * i / (n - 1)
            rel = (x - w * 0.5) / self.sigma
            amp = math.exp(-rel * rel / 2)
            pts_top.append(x)
            pts_top.append(cy - 70 * amp)
            pts_bot.append(x)
            pts_bot.append(cy + 70 * amp)
        if len(pts_top) >= 4:
            c.create_line(*pts_top, fill="#475569", width=1, smooth=True)
            c.create_line(*pts_bot, fill="#475569", width=1, smooth=True)
            fill_pts = pts_top + list(reversed(pts_bot))
            c.create_polygon(*fill_pts, fill="#1e3a5f", outline="")

        # carrier wave inside envelope
        k = 2 * math.pi / max(4.0, self.wavelength)
        wave_pts = []
        for i in range(n):
            x = w * 0.08 + (w * 0.84) * i / (n - 1)
            rel = (x - w * 0.5) / self.sigma
            amp = math.exp(-rel * rel / 2)
            y = cy + 35 * amp * math.sin(k * (x - w * 0.5) + self._phase)
            wave_pts.extend([x, y])
        if len(wave_pts) >= 4:
            c.create_line(*wave_pts, fill="#38bdf8", width=2)

        # propagation arrow
        c.create_line(w * 0.12, cy + 100, w * 0.38, cy + 100,
                      fill=col["accent2"], arrow=tk.LAST, width=2)
        c.create_text(w * 0.25, cy + 118, text=self.t("topic.wave_beam.propagation"),
                      fill=col["canvas_text"], font=self.font("tiny"))

        # labels
        c.create_text(w * 0.5, cy - 88, text=self.t("topic.wave_beam.envelope"),
                      fill=col["muted"], font=self.font("tiny"))
        c.create_line(w * 0.5 - self.sigma, cy - 78, w * 0.5 + self.sigma, cy - 78,
                      fill=col["warn"], arrow=tk.BOTH)
        c.create_text(w * 0.5, cy - 92, text="Δx", fill=col["warn"], font=self.font("tiny"))

        c.create_text(w * 0.5, h - 30,
                      text=self.t("topic.wave_beam.note"),
                      fill=col["muted"], font=self.font("small"))
