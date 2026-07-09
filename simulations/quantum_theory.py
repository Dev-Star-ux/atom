"""Chapter 2, Section 2, Topic 3 - Quantum theory of light and the photoelectric effect.

Einstein: light arrives as photons of energy E = h nu. One photon gives all its
energy to one electron, so

    KE_max = h nu - W

where W is the work function. Below the threshold nu0 = W/h no electrons come
out, no matter how bright the light. Plotting KE_max against frequency gives a
straight line of slope h and intercept nu0 - exactly what experiments show.
"""
import math
import random

from simulations.base import Simulation
from simulations.plot import Plot
import simulations.photo as photo

FMAX = 15.0   # x-axis max in 1e14 Hz


class QuantumTheorySim(Simulation):
    title_key = "topic.quantum_theory.title"
    desc_key = "topic.quantum_theory.desc"

    def __init__(self, master, app):
        self.freq = 8.0
        self.material = "sodium"
        self.photons = []
        self.electrons = []
        self._emit = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        from tkinter import ttk
        import tkinter as tk
        self.f_var, _ = self.add_slider(
            parent, self.t("topic.quantum_theory.frequency"), 3, FMAX, self.freq,
            command=lambda v: setattr(self, "freq", v), fmt="{:.1f}",
        )
        ttk.Label(parent, text=self.t("topic.quantum_theory.material"),
                  style="Panel.TLabel").pack(anchor="w", pady=(8, 0))
        self._mats = list(photo.MATERIALS.keys())
        self.mat_var = tk.StringVar()
        combo = ttk.Combobox(parent, state="readonly", textvariable=self.mat_var,
                             values=[self.t("material." + m) for m in self._mats])
        combo.current(self._mats.index(self.material))
        combo.pack(fill="x", pady=(2, 0))
        combo.bind("<<ComboboxSelected>>", self._on_mat)

        self.r_energy = self.add_readout(parent, self.t("topic.quantum_theory.photon_energy"))
        self.r_work = self.add_readout(parent, self.t("topic.quantum_theory.work"))
        self.r_ke = self.add_readout(parent, self.t("topic.quantum_theory.ke_max"))
        self.r_thresh = self.add_readout(parent, self.t("topic.quantum_theory.threshold"))

    def _on_mat(self, _e):
        labels = [self.t("material." + m) for m in self._mats]
        self.material = self._mats[labels.index(self.mat_var.get())]

    def reset(self):
        self.freq = 8.0
        self.material = "sodium"
        self.f_var.set(self.freq)
        self.mat_var.set(self.t("material.sodium"))
        self.photons.clear()
        self.electrons.clear()

    def _work(self):
        return photo.MATERIALS[self.material]

    def _ke_max(self):
        return photo.photon_energy_eV(self.freq) - self._work()

    # geometry -------------------------------------------------------------
    def _geom(self):
        w, h = self.cwh()
        anim_bottom = h * 0.44
        metal_x = w * 0.5
        return w, h, anim_bottom, metal_x

    # physics --------------------------------------------------------------
    def tick(self, dt):
        w, h, ab, mx = self._geom()
        ke = self._ke_max()
        if dt > 0:
            self._emit += dt * 3.0
            while self._emit >= 1.0:
                self._emit -= 1.0
                y = random.uniform(ab * 0.25, ab * 0.85)
                self.photons.append({"x": 20.0, "y": y, "hit": False})
            color_speed = 260.0
            for p in self.photons:
                if not p["hit"]:
                    p["x"] += color_speed * dt
                    if p["x"] >= mx:
                        p["hit"] = True
                        if ke > 0:
                            ang = random.uniform(-0.9, 0.9)
                            v = 150.0 + 60.0 * math.sqrt(max(0.0, ke))
                            self.electrons.append({"x": mx, "y": p["y"],
                                                   "vx": -abs(math.cos(ang)) * v,  # away from metal
                                                   "vy": math.sin(ang) * v})
            self.photons = [p for p in self.photons if not p["hit"]]
            for e in self.electrons:
                e["x"] += e["vx"] * dt
                e["y"] += e["vy"] * dt
            self.electrons = [e for e in self.electrons if -20 < e["x"] < w and -20 < e["y"] < h]
        self._update_readouts(ke)

    def _update_readouts(self, ke):
        self.r_energy.set(f"{photo.photon_energy_eV(self.freq):.2f} eV")
        self.r_work.set(f"{self._work():.2f} eV")
        self.r_ke.set(f"{ke:.2f} eV" if ke > 0 else self.t("topic.quantum_theory.no_emit"))
        self.r_thresh.set(f"{photo.threshold_f14(self._work()):.1f} ×10¹⁴ Hz")

    # drawing --------------------------------------------------------------
    def draw(self):
        c = self.canvas
        c.delete("all")
        w, h, ab, mx = self._geom()
        col = self.colors
        pcolor = photo.photon_color(self.freq)

        # --- animation region (top) ---
        c.create_rectangle(mx, 12, mx + 12, ab, fill="#64748b", outline="")
        c.create_text(mx + 6, ab + 4, text=self.t("material." + self.material),
                      fill=col["canvas_text"], font=self.font("small"))
        for p in self.photons:
            c.create_line(p["x"] - 12, p["y"], p["x"], p["y"], fill=pcolor, width=3)
        for e in self.electrons:
            c.create_oval(e["x"] - 3, e["y"] - 3, e["x"] + 3, e["y"] + 3,
                          fill="#67e8f9", outline="")
        if self._ke_max() <= 0:
            c.create_text(mx * 0.5, ab * 0.5, text=self.t("topic.quantum_theory.below"),
                          fill="#f87171", font=self.font("small"))

        # --- KE_max vs frequency plot (bottom) ---
        box = (72, ab + 30, w - 26, h - 44)
        p = Plot(c, box, (0, FMAX), (0, 6), self.colors, self.font("small"))
        p.axes(self.t("topic.quantum_theory.xlabel"),
               self.t("topic.quantum_theory.ylabel"),
               (0, 3, 6, 9, 12, 15))
        # the line KE = h nu - W (only where positive)
        f0 = photo.threshold_f14(self._work())
        xs = [f0, FMAX]
        ys = [0.0, photo.photon_energy_eV(FMAX) - self._work()]
        p.curve(xs, ys, "#38bdf8", width=2)
        p.vline(f0, "#fbbf24", label=self.t("topic.quantum_theory.threshold_mark"))
        # current operating point
        ke = self._ke_max()
        if ke > 0:
            px, py = p.X(self.freq), p.Y(ke)
            c.create_oval(px - 4, py - 4, px + 4, py + 4, fill="#f472b6", outline="")
