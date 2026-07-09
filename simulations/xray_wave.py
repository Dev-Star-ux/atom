"""Chapter 2, Section 5, Topic 2 - Wave property of X-rays. they interfere and diffract. Bragg's law
    n λ = 2 d sin θ
describes constructive reflection from crystal planes separated by distance d.
When the path difference between rays reflected from adjacent planes equals an
integer number of wavelengths, a bright spot appears — the basis of X-ray
crystallography (von Laue, 1912; Bragg, 1913).
"""
import math
import tkinter as tk

from simulations.base import Simulation
import simulations.xray as xr


class XrayWaveSim(Simulation):
    title_key = "topic.xray_wave.title"
    desc_key = "topic.xray_wave.desc"

    def __init__(self, master, app):
        self.lam = 100.0     # pm
        self.d = 200.0       # pm plane spacing
        self.theta = 30.0    # degrees
        self._phase = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        self.l_var, _ = self.add_slider(
            parent, self.t("topic.xray_wave.wavelength"), 50, 250, self.lam,
            command=lambda v: setattr(self, "lam", v), fmt="{:.0f} pm",
        )
        self.d_var, _ = self.add_slider(
            parent, self.t("topic.xray_wave.spacing"), 100, 400, self.d,
            command=lambda v: setattr(self, "d", v), fmt="{:.0f} pm",
        )
        self.t_var, _ = self.add_slider(
            parent, self.t("topic.xray_wave.angle"), 5, 80, self.theta,
            command=lambda v: setattr(self, "theta", v), fmt="{:.1f}°",
        )
        self.r_order = self.add_readout(parent, self.t("topic.xray_wave.order"))
        self.r_path = self.add_readout(parent, self.t("topic.xray_wave.path_diff"))
        self.r_result = self.add_readout(parent, self.t("topic.xray_wave.result"))

    def reset(self):
        self.lam = 100.0
        self.d = 200.0
        self.theta = 30.0
        self.l_var.set(self.lam)
        self.d_var.set(self.d)
        self.t_var.set(self.theta)
        self._phase = 0.0

    def tick(self, dt):
        if dt > 0:
            self._phase = (self._phase + dt * 4.0) % (2 * math.pi)

    def _nearest_order(self):
        ratio = 2.0 * self.d * math.sin(math.radians(self.theta)) / self.lam
        return round(ratio)

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        order = self._nearest_order()
        path_n = xr.bragg_constructive(order, self.d, self.lam, self.theta)
        residual = abs(path_n - round(path_n))
        bright = residual < 0.08

        self.r_order.set(f"n = {order}")
        self.r_path.set(f"{path_n:.2f} λ")
        self.r_result.set(self.t("topic.xray_wave.constructive") if bright
                          else self.t("topic.xray_wave.destructive"))

        cx, cy = w * 0.42, h * 0.48
        plane_len = 140
        theta = math.radians(self.theta)

        # crystal block
        c.create_rectangle(cx - 60, cy - 70, cx + 80, cy + 70,
                           fill="#1e293b", outline="#475569")

        # two atomic planes
        for offset in (-self.d * 0.18, self.d * 0.18):
            py = cy + offset
            c.create_line(cx - plane_len, py, cx + plane_len, py,
                          fill="#94a3b8", width=3)
            for dot in range(-5, 6):
                c.create_oval(cx + dot * 22 - 3, py - 3, cx + dot * 22 + 3, py + 3,
                              fill="#cbd5e1", outline="")

        c.create_text(cx + 10, cy + 90, text=self.t("topic.xray_wave.crystal"),
                      fill=col["canvas_text"], font=self.font("small"))

        # incident wave (from upper left)
        inc_color = "#38bdf8"
        for i in range(5):
            phase = self._phase + i * 0.8
            x0 = cx - 180 + i * 28
            y0 = cy - 120 + math.sin(phase) * 6
            c.create_line(x0, y0, x0 + 60, y0 + 40, fill=inc_color, width=1)

        # reflected wave at angle θ
        refl_color = "#4ade80" if bright else "#64748b"
        refl_len = 100
        rx = cx + 40
        ry = cy - self.d * 0.18
        rdx = refl_len * math.cos(theta)
        rdy = -refl_len * math.sin(theta)
        c.create_line(rx, ry, rx + rdx, ry + rdy, fill=refl_color, width=3, arrow=tk.LAST)

        # path difference sketch
        c.create_line(cx - 80, cy - self.d * 0.18 - 50, cx - 80, cy + self.d * 0.18 - 50,
                      fill=col["warn"], dash=(4, 4))
        c.create_text(cx - 90, cy, text="d", fill=col["warn"], font=self.font("small"))

        # angle arc
        c.create_arc(cx - 30, cy - 50, cx + 30, cy + 10,
                     start=0, extent=-self.theta, outline=col["accent2"], style=tk.ARC)
        c.create_text(cx + 40, cy - 20, text=f"θ = {self.theta:.1f}°",
                      fill=col["accent2"], font=self.font("small"))

        # formula panel
        c.create_text(w * 0.72, h * 0.22, text=self.t("topic.xray_wave.bragg"),
                      fill=col["accent2"], font=self.font("bold"))
        c.create_text(w * 0.72, h * 0.32,
                      text=self.t("topic.xray_wave.bragg_val",
                                  n=order, lam=f"{self.lam:.0f}",
                                  d=f"{self.d:.0f}", theta=f"{self.theta:.1f}"),
                      fill=col["canvas_text"], font=self.font("small"), width=200, justify="left")

        if bright:
            c.create_text(w * 0.72, h * 0.48, text="✓ " + self.t("topic.xray_wave.constructive"),
                          fill=col["good"], font=self.font("small"))
