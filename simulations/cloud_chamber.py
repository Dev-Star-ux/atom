"""Section 2, Topic 3 - Alpha-particle tracks in a cloud (mist) chamber.

This is the *qualitative* gold-foil experiment. Alpha particles are fired at a
thin gold foil (a row of nuclei) and leave persistent tracks, just like the
condensation trails in a Wilson cloud chamber. The tracks are colour-coded:

    * pale blue : passed almost straight through  -> the atom is mostly EMPTY
    * amber     : deflected by a moderate angle
    * red       : bounced back (theta > 90 deg)    -> hit a tiny dense NUCLEUS

Live counters show how overwhelmingly common the straight-through tracks are
and how rare the back-scattered ones are - Rutherford's key conclusion. The
quantitative angular law is explored in the next topic, the Rutherford
scattering formula.
"""
import math
import random

from simulations.base import Simulation

BG = (11, 18, 32)  # canvas background, for fading tracks toward it


def _blend(hex_color, t):
    """Blend hex_color toward the background. t=1 full colour, t=0 background."""
    r = int(int(hex_color[1:3], 16) * t + BG[0] * (1 - t))
    g = int(int(hex_color[3:5], 16) * t + BG[1] * (1 - t))
    b = int(int(hex_color[5:7], 16) * t + BG[2] * (1 - t))
    return f"#{r:02x}{g:02x}{b:02x}"


class CloudChamberSim(Simulation):
    title_key = "topic.cloud_chamber.title"
    desc_key = "topic.cloud_chamber.desc"

    N_NUCLEI = 5
    MAX_TRACKS = 110

    COL_THROUGH = "#7dd3fc"
    COL_WIDE = "#fbbf24"
    COL_BACK = "#f87171"

    def __init__(self, master, app):
        self.energy = 55.0
        self.zcharge = 79.0      # gold
        self.persist = True
        self.alphas = []
        self.tracks = []
        self.nuclei = []
        self.n_total = self.n_through = self.n_wide = self.n_back = 0
        self._emit_acc = 0.0
        self._last_w = None
        super().__init__(master, app)

    # controls -------------------------------------------------------------
    def build_controls(self, parent):
        import tkinter as tk
        from tkinter import ttk
        self.e_var, _ = self.add_slider(
            parent, self.t("topic.cloud_chamber.energy"), 20, 120, self.energy,
            command=lambda v: setattr(self, "energy", v), fmt="{:.0f}",
        )
        self.z_var, _ = self.add_slider(
            parent, self.t("topic.cloud_chamber.zcharge"), 10, 92, self.zcharge,
            command=lambda v: setattr(self, "zcharge", v), fmt="{:.0f}",
        )
        self.persist_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text=self.t("topic.cloud_chamber.persist"),
                        variable=self.persist_var,
                        command=lambda: setattr(self, "persist", self.persist_var.get()),
                        style="Panel.TCheckbutton").pack(anchor="w", pady=(10, 0))
        self.r_total = self.add_readout(parent, self.t("topic.cloud_chamber.fired"))
        self.r_through = self.add_readout(parent, self.t("topic.cloud_chamber.through"))
        self.r_wide = self.add_readout(parent, self.t("topic.cloud_chamber.wide"))
        self.r_back = self.add_readout(parent, self.t("topic.cloud_chamber.backscatter"))

    def reset(self):
        self.energy = 55.0
        self.zcharge = 79.0
        self.persist = True
        self.e_var.set(self.energy)
        self.z_var.set(self.zcharge)
        self.persist_var.set(True)
        self.alphas.clear()
        self.tracks.clear()
        self.n_total = self.n_through = self.n_wide = self.n_back = 0
        self._last_w = None

    # geometry -------------------------------------------------------------
    def _geom(self):
        w, h = self.cwh()
        return w, h, h - 20, w * 0.44   # width, height, scene_bottom, foil_x

    def _make_nuclei(self):
        w, h, sb, fx = self._geom()
        top, bot = h * 0.12, sb - 16
        self.nuclei = [(fx, top + (bot - top) * (i + 0.5) / self.N_NUCLEI)
                       for i in range(self.N_NUCLEI)]
        self._last_w = w

    # physics --------------------------------------------------------------
    def tick(self, dt):
        w, h, sb, fx = self._geom()
        if self._last_w != w:
            self._make_nuclei()

        if dt > 0:
            v0 = 130.0 + self.energy * 2.0
            self._emit_acc += dt
            rate = 0.10 if self.persist else 0.05
            while self._emit_acc >= rate and len(self.alphas) < 40:
                self._emit_acc -= rate
                y = random.uniform(h * 0.10, sb - 10)
                self.alphas.append({"x": 6.0, "y": y, "vx": v0, "vy": 0.0, "pts": [6.0, y]})

            coulomb = 320.0 * self.zcharge
            soft = 1.5
            for a in self.alphas:
                steps = 12
                sdt = dt / steps
                for _ in range(steps):
                    ax = ay = 0.0
                    for (nx, ny) in self.nuclei:
                        dx = a["x"] - nx
                        dy = a["y"] - ny
                        r2 = dx * dx + dy * dy + soft * soft
                        f = coulomb / (r2 * math.sqrt(r2))
                        ax += f * dx
                        ay += f * dy
                    a["vx"] += ax * sdt
                    a["vy"] += ay * sdt
                    a["x"] += a["vx"] * sdt
                    a["y"] += a["vy"] * sdt
                a["pts"].extend((a["x"], a["y"]))
                if not (0 <= a["x"] <= w and 0 <= a["y"] <= h):
                    self._finish(a)
            self.alphas = [a for a in self.alphas if 0 <= a["x"] <= w and 0 <= a["y"] <= h]

            for tr in self.tracks:
                tr["life"] -= dt
            self.tracks = [tr for tr in self.tracks if tr["life"] > 0]

        self._update_readouts()

    def _finish(self, a):
        speed = math.hypot(a["vx"], a["vy"]) or 1.0
        theta = math.degrees(math.acos(max(-1.0, min(1.0, a["vx"] / speed))))
        self.n_total += 1
        if theta < 12:
            color = self.COL_THROUGH
            self.n_through += 1
        elif theta <= 90:
            color = self.COL_WIDE
            self.n_wide += 1
        else:
            color = self.COL_BACK
            self.n_back += 1
        life = 26.0 if self.persist else 2.2
        self.tracks.append({"pts": a["pts"], "color": color, "life": life, "max": life})
        if len(self.tracks) > self.MAX_TRACKS:
            self.tracks.pop(0)

    def _update_readouts(self):
        self.r_total.set(str(self.n_total))
        tot = self.n_total or 1
        self.r_through.set(f"{self.n_through}  ({100.0 * self.n_through / tot:.0f}%)")
        self.r_wide.set(f"{self.n_wide}  ({100.0 * self.n_wide / tot:.0f}%)")
        self.r_back.set(f"{self.n_back}  ({100.0 * self.n_back / tot:.1f}%)")

    # drawing --------------------------------------------------------------
    def render(self):
        c = self.canvas
        w, h, sb, fx = self._geom()
        col = self.colors

        c.create_rectangle(fx - 6, h * 0.08, fx + 6, sb, fill="#4a3a12", outline="#a97d1e")
        c.create_text(fx, h * 0.08 - 12, text=self.t("topic.cloud_chamber.foil"),
                      fill="#d4af37", font=self.font("small"))
        c.create_rectangle(0, h * 0.10, 8, sb, fill="#1e293b", outline="")
        c.create_text(42, h * 0.06, text=self.t("topic.cloud_chamber.source"),
                      fill=col["canvas_text"], font=self.font("small"))

        for tr in self.tracks:
            if len(tr["pts"]) >= 4:
                t = max(0.15, tr["life"] / tr["max"])
                c.create_line(*tr["pts"], fill=_blend(tr["color"], t), width=2, smooth=True)

        for (nx, ny) in self.nuclei:
            c.create_oval(nx - 7, ny - 7, nx + 7, ny + 7, fill="#fbbf24", outline="#fde68a")

        for a in self.alphas:
            if len(a["pts"]) >= 4:
                c.create_line(*a["pts"], fill="#fecaca", width=2, smooth=True)
            c.create_oval(a["x"] - 3, a["y"] - 3, a["x"] + 3, a["y"] + 3, fill="#ef4444", outline="")

        self._draw_legend(c, w, h)

    def _draw_legend(self, c, w, h):
        x, y = w - 252, h * 0.07
        for color, key in ((self.COL_THROUGH, "legend_through"),
                           (self.COL_WIDE, "legend_wide"),
                           (self.COL_BACK, "legend_back")):
            c.create_line(x, y, x + 22, y, fill=color, width=3)
            c.create_text(x + 30, y, text=self.t("topic.cloud_chamber." + key), anchor="w",
                          fill=self.colors["canvas_text"], font=self.font("small"))
            y += 18
