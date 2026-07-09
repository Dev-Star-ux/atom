"""Section 2, Topic 2 - The nuclear (planetary) model of the atom.

Rutherford's scattering results forced a new picture: almost all the mass and
all the positive charge sit in a tiny central nucleus, with the electrons
orbiting far outside it - like planets around the sun. The nucleus is roughly
10,000-100,000 times smaller than the atom.

The optional "classical radiation" toggle shows the fatal flaw of the purely
classical planetary model: an orbiting (accelerating) electron should radiate
energy and spiral into the nucleus. That failure is what later motivated Bohr's
quantised orbits.
"""
import math
import random

from simulations.base import Simulation


class PlanetarySim(Simulation):
    title_key = "topic.planetary.title"
    desc_key = "topic.planetary.desc"

    def __init__(self, master, app):
        self.n_electrons = 3
        self.base_radius = 130.0
        self.speed = 1.0
        self.radiate = False
        self.electrons = []
        super().__init__(master, app)
        self._spawn()

    # controls -------------------------------------------------------------
    def build_controls(self, parent):
        import tkinter as tk
        from tkinter import ttk
        self.n_var, _ = self.add_slider(
            parent, self.t("topic.planetary.electrons"), 1, 6, self.n_electrons,
            command=self._set_n, fmt="{:.0f}",
        )
        self.r_var, _ = self.add_slider(
            parent, self.t("topic.planetary.radius"), 70, 190, self.base_radius,
            command=self._set_radius, fmt="{:.0f}",
        )
        self.s_var, _ = self.add_slider(
            parent, self.t("topic.planetary.speed"), 0.2, 2.5, self.speed,
            command=lambda v: setattr(self, "speed", v), fmt="{:.1f}x",
        )
        self.radiate_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(parent, text=self.t("topic.planetary.radiate"),
                        variable=self.radiate_var, command=self._toggle_radiate,
                        style="Panel.TCheckbutton").pack(anchor="w", pady=(10, 0))
        self.r_count = self.add_readout(parent, self.t("topic.planetary.electrons"))
        self.r_status = self.add_readout(parent, self.t("topic.planetary.status"))

    def _set_n(self, v):
        self.n_electrons = int(round(v))
        self._spawn()

    def _set_radius(self, v):
        self.base_radius = v
        self._spawn()

    def _toggle_radiate(self):
        self.radiate = self.radiate_var.get()
        if not self.radiate:
            self._spawn()

    def reset(self):
        self.n_electrons = 3
        self.base_radius = 130.0
        self.speed = 1.0
        self.radiate = False
        self.n_var.set(self.n_electrons)
        self.r_var.set(self.base_radius)
        self.s_var.set(self.speed)
        self.radiate_var.set(False)
        self._spawn()

    # setup ----------------------------------------------------------------
    def _spawn(self):
        self.electrons = []
        for i in range(self.n_electrons):
            r = self.base_radius * (0.55 + 0.45 * (i + 1) / max(1, self.n_electrons))
            self.electrons.append({
                "r": r,
                "r0": r,
                "angle": random.uniform(0, 2 * math.pi),
                "tilt": random.uniform(-0.5, 0.5),
                "trail": [],
                "dead": False,
            })

    # physics --------------------------------------------------------------
    def tick(self, dt):
        if dt > 0:
            for e in self.electrons:
                if e["dead"]:
                    continue
                # angular speed ~ r^-1.5 (Kepler-like) for a nicer look
                omega = self.speed * 2.4 * (110.0 / max(20.0, e["r"])) ** 1.5
                e["angle"] += omega * dt
                if self.radiate and e["r"] > 14:
                    e["r"] -= 26.0 * dt * (self.speed)
                    if e["r"] <= 14:
                        e["dead"] = True
        self._update_readouts()

    def _update_readouts(self):
        self.r_count.set(str(self.n_electrons))
        if self.radiate:
            if all(e["dead"] for e in self.electrons):
                self.r_status.set(self.t("topic.planetary.collapsed"))
            else:
                self.r_status.set(self.t("topic.planetary.collapsing"))
        else:
            self.r_status.set(self.t("topic.planetary.stable"))

    # drawing --------------------------------------------------------------
    def render(self):
        c = self.canvas
        w = self.canvas.winfo_width() or 760
        h = self.canvas.winfo_height() or 460
        cx, cy = w / 2, h / 2
        col = self.colors

        # orbit guide paths
        for e in self.electrons:
            rr = e["r0"]
            c.create_oval(cx - rr, cy - rr * (0.72 + 0.14 * abs(e["tilt"])),
                          cx + rr, cy + rr * (0.72 + 0.14 * abs(e["tilt"])),
                          outline="#233047")

        # electrons with fading trails
        for e in self.electrons:
            if e["dead"]:
                continue
            ry = e["r"] * (0.72 + 0.14 * abs(e["tilt"]))
            ex = cx + e["r"] * math.cos(e["angle"])
            ey = cy + ry * math.sin(e["angle"])
            e["trail"].append((ex, ey))
            if len(e["trail"]) > 16:
                e["trail"].pop(0)
            # one comet-tail polyline instead of many shaded chords
            # (plain segments; smooth splines overshoot with few, spread points)
            if len(e["trail"]) >= 4:
                flat = [coord for pt in e["trail"] for coord in pt]
                c.create_line(*flat, fill="#2a6f8f", width=2)
            c.create_oval(ex - 6, ey - 6, ex + 6, ey + 6, fill="#38bdf8", outline="#7dd3fc")
            c.create_text(ex, ey, text="−", fill="#0b1220", font=self.font("small"))

        # nucleus (deliberately tiny relative to the orbits)
        c.create_oval(cx - 9, cy - 9, cx + 9, cy + 9, fill="#ef4444", outline="#fecaca")
        c.create_text(cx, cy, text="+", fill="#ffffff", font=self.font("base"))
        c.create_text(cx, cy + 24, text=self.t("topic.planetary.nucleus"),
                      fill=col["canvas_text"], font=self.font("small"))
        c.create_text(w / 2, h - 18, text=self.t("topic.planetary.scale_note"),
                      fill=col["canvas_text"], font=self.font("small"))
