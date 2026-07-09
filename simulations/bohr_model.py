"""Chapter 2, Section 4, Topic 2 - Bohr's atomic model.

Bohr (1913) kept Rutherford's nucleus but added quantisation:

  1. Electrons move in allowed circular orbits with angular momentum L = nħ.
  2. On a stationary orbit the electron does not radiate.
  3. A photon is emitted or absorbed only when the electron jumps between orbits.

Orbit radius r_n = n² a₀ and energy E_n = −13.6 eV / n² follow from these
postulates. Only these discrete orbits are permitted — not the continuum of
classical planetary orbits.
"""
import math

from simulations.base import Simulation
import simulations.atom as atom


class BohrModelSim(Simulation):
    title_key = "topic.bohr_model.title"
    desc_key = "topic.bohr_model.desc"

    def __init__(self, master, app):
        self.n = 3
        self.angle = 0.0
        self.show_all = True
        super().__init__(master, app)

    def build_controls(self, parent):
        from tkinter import ttk
        import tkinter as tk

        self.n_var, _ = self.add_slider(
            parent, self.t("topic.bohr_model.quantum_n"), 1, 6, self.n,
            command=self._on_n, fmt="n = {:.0f}",
        )
        self.show_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text=self.t("topic.bohr_model.show_all"),
                        variable=self.show_var, style="Panel.TCheckbutton").pack(anchor="w", pady=(8, 0))
        self.r_radius = self.add_readout(parent, self.t("topic.bohr_model.radius"))
        self.r_energy = self.add_readout(parent, self.t("topic.bohr_model.energy"))
        self.r_momentum = self.add_readout(parent, self.t("topic.bohr_model.momentum"))
        self.r_speed = self.add_readout(parent, self.t("topic.bohr_model.speed"))

    def _on_n(self, v):
        self.n = int(round(v))

    def reset(self):
        self.n = 3
        self.angle = 0.0
        self.n_var.set(self.n)
        self.show_var.set(True)

    def tick(self, dt):
        if dt > 0:
            self.angle += atom.orbit_angular_speed(self.n) * dt

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        cx, cy = w * 0.42, h * 0.50
        scale = min(w, h) / 520.0 * 18.0

        show_all = self.show_var.get()

        # ghost orbits
        if show_all:
            for gn in range(1, 7):
                if gn == self.n:
                    continue
                r = atom.orbit_radius_px(gn, scale)
                c.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#1e293b", dash=(3, 5))

        # selected orbit
        r = atom.orbit_radius_px(self.n, scale)
        c.create_oval(cx - r, cy - r, cx + r, cy + r, outline=col["accent"], width=2)
        c.create_text(cx, cy - r - 14, text=f"n = {self.n}",
                      fill=col["accent2"], font=self.font("small"))

        # electron
        ex = cx + r * math.cos(self.angle)
        ey = cy + r * math.sin(self.angle)
        c.create_oval(ex - 8, ey - 8, ex + 8, ey + 8, fill="#38bdf8", outline="#7dd3fc")
        c.create_text(ex, ey, text="−", fill="#0b1220", font=self.font("small"))

        # nucleus
        c.create_oval(cx - 10, cy - 10, cx + 10, cy + 10, fill="#ef4444", outline="#fecaca")
        c.create_text(cx, cy, text="+", fill="#fff", font=self.font("base"))

        # postulates panel
        px = w * 0.68
        py = h * 0.14
        for i, key in enumerate(("post1", "post2", "post3"), start=0):
            c.create_text(px, py + i * 52, text=self.t(f"topic.bohr_model.{key}"),
                          fill=col["canvas_text"], font=self.font("small"),
                          anchor="nw", width=w * 0.28, justify="left")

        # formulas
        c.create_text(w * 0.5, h - 36, text=self.t("topic.bohr_model.formulas"),
                      fill=col["muted"], font=self.font("small"))

        rn = atom.bohr_radius(self.n)
        self.r_radius.set(f"r_{self.n} = {rn * 1e11:.2f} ×10⁻¹¹ m")
        self.r_energy.set(f"E_{self.n} = {atom.energy_level_eV(self.n):.3f} eV")
        self.r_momentum.set(f"L = {self.n} ħ")
        v = atom.bohr_orbital_speed(self.n)
        self.r_speed.set(f"v = {v / 1e6:.2f} ×10⁶ m/s")
