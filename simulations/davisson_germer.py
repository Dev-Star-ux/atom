"""Chapter 3, Section 1, Topic 3 - Davisson–Germer experiment.

Davisson and Germer (1927) fired low-energy electrons at a nickel crystal and
observed diffraction peaks — direct proof that electrons behave as waves. The
peak angles satisfy the same Bragg condition as X-rays, with the electron
wavelength given by de Broglie:  λ = h / √(2m eV).
"""
import math
import tkinter as tk

from simulations.base import Simulation
from simulations.plot import Plot
import simulations.matter as matter

NI_SPACING_PM = 218.0   # effective Ni plane spacing (pm); nλ = d sin θ → peak ≈ 50° at 54 V


class DavissonGermerSim(Simulation):
    title_key = "topic.davisson_germer.title"
    desc_key = "topic.davisson_germer.desc"

    def __init__(self, master, app):
        self.voltage = 54.0    # V — near the famous 54 V peak
        self.angle = 50.0      # detector angle (degrees)
        self._electrons = []
        self._emit = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        self.v_var, _ = self.add_slider(
            parent, self.t("topic.davisson_germer.voltage"), 20, 120, self.voltage,
            command=lambda v: setattr(self, "voltage", v), fmt="{:.0f} V",
        )
        self.a_var, _ = self.add_slider(
            parent, self.t("topic.davisson_germer.angle"), 20, 80, self.angle,
            command=lambda v: setattr(self, "angle", v), fmt="{:.0f}°",
        )
        self.r_lambda = self.add_readout(parent, self.t("topic.davisson_germer.wavelength"))
        self.r_peak = self.add_readout(parent, self.t("topic.davisson_germer.peak_angle"))
        self.r_intensity = self.add_readout(parent, self.t("topic.davisson_germer.intensity"))

    def reset(self):
        self.voltage = 54.0
        self.angle = 50.0
        self.v_var.set(self.voltage)
        self.a_var.set(self.angle)
        self._electrons.clear()
        self._emit = 0.0

    def _peak_angle(self):
        return matter.davisson_peak_angle_deg(self.voltage, NI_SPACING_PM, n=1)

    def _intensity_at(self, theta_deg):
        """Model diffraction intensity with peaks at Bragg angles."""
        peak = self._peak_angle()
        if peak is None:
            return 0.1
        total = 0.08
        for n in range(1, 4):
            pa = matter.davisson_peak_angle_deg(self.voltage, NI_SPACING_PM, n=n)
            if pa is not None:
                width = 4.0
                total += math.exp(-((theta_deg - pa) ** 2) / (2 * width * width))
        return total

    def tick(self, dt):
        if dt <= 0:
            return
        w, h = self.cwh()
        gun_x, crystal_x = w * 0.14, w * 0.38
        self._emit += dt * 5.0
        while self._emit >= 1.0:
            self._emit -= 1.0
            self._electrons.append({"x": gun_x, "y": h * 0.42, "scattered": False})

        for e in self._electrons:
            if not e["scattered"]:
                e["x"] += 280.0 * dt
                if e["x"] >= crystal_x:
                    e["scattered"] = True
                    theta = math.radians(self.angle)
                    speed = 200.0
                    e["vx"] = speed * math.cos(theta)
                    e["vy"] = -speed * math.sin(theta)
            else:
                e["x"] += e["vx"] * dt
                e["y"] += e["vy"] * dt
        self._electrons = [e for e in self._electrons if -20 < e["x"] < w + 20 and -20 < e["y"] < h + 20]

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        lam_pm = matter.electron_wavelength_pm(self.voltage)
        peak = self._peak_angle()
        intensity = self._intensity_at(self.angle)

        self.r_lambda.set(f"λ = {lam_pm:.1f} pm")
        self.r_peak.set(f"{peak:.1f}°" if peak is not None else "—")
        self.r_intensity.set(f"{intensity:.2f} (rel.)")

        gun_x, crystal_x = w * 0.14, w * 0.38
        cy = h * 0.42

        # electron gun
        c.create_rectangle(gun_x - 16, cy - 20, gun_x + 8, cy + 20,
                           fill="#334155", outline="#64748b")
        c.create_text(gun_x - 20, cy, text=self.t("topic.davisson_germer.gun"),
                      fill=col["canvas_text"], font=self.font("tiny"), anchor="e")

        # nickel crystal
        c.create_rectangle(crystal_x - 8, cy - 45, crystal_x + 8, cy + 45,
                           fill="#94a3b8", outline="#cbd5e1")
        for i in range(-3, 4):
            c.create_line(crystal_x - 30, cy + i * 12, crystal_x + 30, cy + i * 12,
                          fill="#64748b", width=1)
        c.create_text(crystal_x, cy + 58, text=self.t("topic.davisson_germer.crystal"),
                      fill=col["canvas_text"], font=self.font("small"))

        # incident beam
        c.create_line(gun_x + 8, cy, crystal_x - 8, cy, fill=col["accent2"], width=2)

        # scattered electrons
        for e in self._electrons:
            ec = col["accent"] if e.get("scattered") else col["accent2"]
            c.create_oval(e["x"] - 3, e["y"] - 3, e["x"] + 3, e["y"] + 3, fill=ec, outline="")

        # detector arm at angle θ
        det_len = 100
        theta = math.radians(self.angle)
        dx = crystal_x + det_len * math.cos(theta)
        dy = cy - det_len * math.sin(theta)
        c.create_line(crystal_x, cy, dx, dy, fill=col["good"] if intensity > 0.5 else "#475569", width=2)
        c.create_text(dx + 10, dy, text=self.t("topic.davisson_germer.detector"),
                      fill=col["canvas_text"], font=self.font("tiny"))

        c.create_arc(crystal_x - 50, cy - 50, crystal_x + 50, cy + 50,
                     start=0, extent=-self.angle, outline=col["warn"], style=tk.ARC)
        c.create_text(crystal_x + 55, cy - 18, text=f"θ = {self.angle:.0f}°",
                      fill=col["warn"], font=self.font("small"))

        # I(θ) plot
        box = (60, h * 0.58, w - 28, h - 40)
        thetas = list(range(20, 81))
        intensities = [self._intensity_at(t) for t in thetas]
        ymax = max(intensities) * 1.15 or 1.0
        p = Plot(c, box, (20, 80), (0, ymax), col, self.font("small"))
        p.axes(self.t("topic.davisson_germer.theta_axis"),
               self.t("topic.davisson_germer.intensity_axis"),
               (20, 40, 60, 80))
        p.curve(thetas, intensities, col["accent"], width=2)
        if peak is not None:
            p.vline(peak, col["warn"], dash=(3, 3))
        p.label(self.angle, intensity, "●", col["good"], anchor="n")

        c.create_text(w * 0.5, h * 0.54,
                      text=self.t("topic.davisson_germer.note", d=f"{NI_SPACING_PM:.0f}"),
                      fill=col["muted"], font=self.font("tiny"))
