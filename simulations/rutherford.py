"""Section 2, Topic 3 - The Rutherford scattering formula.

Alpha particles are fired at a heavy nucleus and repelled by the Coulomb force.
Each alpha follows a hyperbola; its scattering angle depends on the impact
parameter b, the nuclear charge Z and the alpha's kinetic energy E:

    tan(theta / 2) = (Z1 Z2 e^2) / (4 pi eps0 * 2 E * b)

Small impact parameters give large deflections, so a few alphas bounce almost
straight back - the observation that revealed the tiny, dense nucleus. The
histogram building up at the bottom follows the Rutherford distribution,
which is proportional to 1 / sin^4(theta / 2).

The trajectories are produced by directly integrating the Coulomb force, in
scaled units chosen so the deflections look right on screen.
"""
import math
import random

from simulations.base import Simulation


class RutherfordSim(Simulation):
    title_key = "topic.rutherford.title"
    desc_key = "topic.rutherford.desc"

    N_BINS = 12  # angular histogram bins over 0..180 degrees

    def __init__(self, master, app):
        self.energy = 50.0       # arbitrary energy units -> initial speed
        self.zcharge = 79.0      # gold
        self.spread = 60.0       # max impact parameter (px)
        self.alphas = []
        self.hist = [0] * self.N_BINS
        self.n_back = 0
        self.n_total = 0
        self._emit_acc = 0.0
        super().__init__(master, app)

    # controls -------------------------------------------------------------
    def build_controls(self, parent):
        self.e_var, _ = self.add_slider(
            parent, self.t("topic.rutherford.energy"), 20, 120, self.energy,
            command=lambda v: setattr(self, "energy", v), fmt="{:.0f}",
        )
        self.z_var, _ = self.add_slider(
            parent, self.t("topic.rutherford.zcharge"), 10, 92, self.zcharge,
            command=lambda v: setattr(self, "zcharge", v), fmt="{:.0f}",
        )
        self.s_var, _ = self.add_slider(
            parent, self.t("topic.rutherford.spread"), 10, 120, self.spread,
            command=lambda v: setattr(self, "spread", v), fmt="{:.0f} px",
        )
        self.r_total = self.add_readout(parent, self.t("topic.rutherford.fired"))
        self.r_back = self.add_readout(parent, self.t("topic.rutherford.backscatter"))
        self.r_pct = self.add_readout(parent, self.t("topic.rutherford.back_pct"))

    def reset(self):
        self.energy = 50.0
        self.zcharge = 79.0
        self.spread = 60.0
        self.e_var.set(self.energy)
        self.z_var.set(self.zcharge)
        self.s_var.set(self.spread)
        self.alphas.clear()
        self.hist = [0] * self.N_BINS
        self.n_back = 0
        self.n_total = 0

    # geometry -------------------------------------------------------------
    def _nucleus(self):
        w = self.canvas.winfo_width() or 760
        h = self.canvas.winfo_height() or 460
        return w, h, w * 0.5, h * 0.42

    # physics --------------------------------------------------------------
    def tick(self, dt):
        w, h, nx, ny = self._nucleus()
        if dt > 0:
            v0 = 120.0 + self.energy * 2.2
            self._emit_acc += dt
            while self._emit_acc >= 0.06 and len(self.alphas) < 60:
                self._emit_acc -= 0.06
                b = random.uniform(-self.spread, self.spread)
                self.alphas.append({
                    "x": 10.0, "y": ny + b,
                    "vx": v0, "vy": 0.0,
                    "trail": [], "done": False,
                })

            coulomb = 9.0 * self.zcharge   # scaled Z1*Z2*k
            soft = 6.0
            for a in self.alphas:
                if a["done"]:
                    continue
                # sub-step the integration for accuracy near the nucleus
                steps = 5
                sdt = dt / steps
                for _ in range(steps):
                    dx = a["x"] - nx
                    dy = a["y"] - ny
                    r2 = dx * dx + dy * dy + soft * soft
                    r = math.sqrt(r2)
                    f = coulomb / r2
                    a["vx"] += f * (dx / r) * sdt
                    a["vy"] += f * (dy / r) * sdt
                    a["x"] += a["vx"] * sdt
                    a["y"] += a["vy"] * sdt
                a["trail"].append((a["x"], a["y"]))
                if len(a["trail"]) > 60:
                    a["trail"].pop(0)
                if a["x"] < 0 or a["x"] > w or a["y"] < 0 or a["y"] > h:
                    self._record(a)
                    a["done"] = True

            self.alphas = [a for a in self.alphas if not a["done"] or a["trail"]]
            # fade finished trails away
            for a in self.alphas:
                if a["done"] and a["trail"]:
                    a["trail"] = a["trail"][3:]
            self.alphas = [a for a in self.alphas if a["trail"]]

        self._update_readouts()

    def _record(self, a):
        # scattering angle measured from the original (+x) beam direction:
        # 0 deg = undeflected, 180 deg = straight back
        speed = math.hypot(a["vx"], a["vy"]) or 1.0
        theta = math.degrees(math.acos(max(-1.0, min(1.0, a["vx"] / speed))))
        idx = min(self.N_BINS - 1, int(theta / 180.0 * self.N_BINS))
        self.hist[idx] += 1
        self.n_total += 1
        if theta > 90.0:
            self.n_back += 1

    def _update_readouts(self):
        self.r_total.set(str(self.n_total))
        self.r_back.set(str(self.n_back))
        if self.n_total:
            self.r_pct.set(f"{100.0 * self.n_back / self.n_total:.1f} %")
        else:
            self.r_pct.set("-")

    # drawing --------------------------------------------------------------
    def draw(self):
        c = self.canvas
        c.delete("all")
        w, h, nx, ny = self._nucleus()
        col = self.colors

        # incoming-beam guide line
        c.create_line(0, ny, nx, ny, fill="#233047", dash=(4, 4))
        c.create_text(46, ny - 14, text=self.t("topic.rutherford.beam"),
                      fill=col["canvas_text"], font=self.font("small"))

        # alpha tracks
        for a in self.alphas:
            tr = a["trail"]
            for i in range(1, len(tr)):
                c.create_line(tr[i - 1][0], tr[i - 1][1], tr[i][0], tr[i][1],
                              fill="#fca5a5")
            if not a["done"]:
                x, y = tr[-1]
                c.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#ef4444", outline="")

        # nucleus
        c.create_oval(nx - 11, ny - 11, nx + 11, ny + 11, fill="#fbbf24", outline="#fde68a")
        c.create_text(nx, ny, text="+Ze", fill="#78350f", font=self.font("small"))
        c.create_text(nx, ny - 24, text=self.t("topic.rutherford.nucleus"),
                      fill=col["canvas_text"], font=self.font("small"))

        self._draw_histogram(c, w, h)

    def _draw_histogram(self, c, w, h):
        base_y = h - 24
        left = 30
        width = w - 60
        bw = width / self.N_BINS
        peak = max(self.hist) or 1
        c.create_text(left, base_y - 96, text=self.t("topic.rutherford.hist_title"),
                      anchor="w", fill=self.colors["canvas_text"], font=self.font("small"))
        c.create_line(left, base_y, left + width, base_y, fill="#334155")
        for i, count in enumerate(self.hist):
            bh = 80 * count / peak
            x0 = left + i * bw + 2
            x1 = left + (i + 1) * bw - 2
            deg = (i + 0.5) / self.N_BINS * 180
            color = "#f87171" if deg > 90 else "#38bdf8"
            if count:
                c.create_rectangle(x0, base_y - bh, x1, base_y, fill=color, outline="")
            if i % 2 == 0:
                c.create_text((x0 + x1) / 2, base_y + 10, text=f"{int(deg)}°",
                              fill=self.colors["canvas_text"], font=self.font("small"))
