"""Section 2, Topic 1 - Effective cross-section & mean free path.

A beam of particles is fired into a slab filled with target atoms. Each target
presents an effective cross-section; a beam particle travels in a straight line
until it strikes one. Averaged over many particles, the distance travelled
before a collision is the mean free path

    lambda = 1 / (n * sigma)

where n is the number density of targets and sigma their cross-section. The
fraction of the beam that passes straight through a slab of thickness L falls
off as  exp(-L / lambda).  This Monte-Carlo view lets students compare the
theoretical lambda with the measured average path length.
"""
import math
import random

from simulations.base import Simulation


class CrossSectionSim(Simulation):
    title_key = "topic.cross_section.title"
    desc_key = "topic.cross_section.desc"

    def __init__(self, master, app):
        self.density = 45.0      # controls number of targets
        self.radius = 10.0       # target radius -> cross-section
        self.targets = []
        self.particles = []
        self.hits = []           # recent collision marks (x, y, life)
        self._emit_acc = 0.0
        # running statistics
        self.sum_path = 0.0
        self.n_collided = 0
        self.n_transmitted = 0
        self.n_total = 0
        self._need_targets = True
        self._last_w = None
        super().__init__(master, app)

    # controls -------------------------------------------------------------
    def build_controls(self, parent):
        self.d_var, _ = self.add_slider(
            parent, self.t("topic.cross_section.density"), 5, 120, self.density,
            command=self._set_density, fmt="{:.0f}",
        )
        self.r_var, _ = self.add_slider(
            parent, self.t("topic.cross_section.radius"), 4, 22, self.radius,
            command=self._set_radius, fmt="{:.0f} px",
        )
        self.r_sigma = self.add_readout(parent, self.t("topic.cross_section.sigma"))
        self.r_n = self.add_readout(parent, self.t("topic.cross_section.ndensity"))
        self.r_lambda = self.add_readout(parent, self.t("topic.cross_section.lambda_theory"))
        self.r_measured = self.add_readout(parent, self.t("topic.cross_section.lambda_measured"))
        self.r_trans = self.add_readout(parent, self.t("topic.cross_section.transmission"))

    def _set_density(self, v):
        self.density = v
        self._need_targets = True

    def _set_radius(self, v):
        self.radius = v
        self._need_targets = True

    def reset(self):
        self.density = 45.0
        self.radius = 10.0
        self.d_var.set(self.density)
        self.r_var.set(self.radius)
        self._need_targets = True
        self._reset_stats()

    def _reset_stats(self):
        self.sum_path = 0.0
        self.n_collided = 0
        self.n_transmitted = 0
        self.n_total = 0
        self.particles.clear()
        self.hits.clear()

    # geometry -------------------------------------------------------------
    def _slab(self):
        w, h = self.cwh()
        return w, h, w * 0.22, w * 0.92   # left edge, right edge of slab

    def _make_targets(self):
        w, h, x0, x1 = self._slab()
        count = int(self.density)
        self.targets = []
        for _ in range(count):
            self.targets.append((
                random.uniform(x0 + 10, x1 - 10),
                random.uniform(20, h - 20),
                self.radius,
            ))
        self._need_targets = False
        self._last_w = w
        self._reset_stats()

    # physics --------------------------------------------------------------
    def tick(self, dt):
        w, h, x0, x1 = self._slab()
        if self._need_targets or self._last_w != w:
            self._make_targets()

        if dt > 0:
            speed = 300.0
            self._emit_acc += dt
            while self._emit_acc >= 0.04:
                self._emit_acc -= 0.04
                self.particles.append({"x": x0, "y": random.uniform(20, h - 20),
                                       "vx": speed, "alive": True})

            alive = []
            for p in self.particles:
                p["x"] += p["vx"] * dt
                collided = False
                for (tx, ty, tr) in self.targets:
                    if abs(p["x"] - tx) < tr and (p["x"] - tx) ** 2 + (p["y"] - ty) ** 2 < tr * tr:
                        # collision
                        self.hits.append([p["x"], p["y"], 1.0])
                        self.sum_path += p["x"] - x0
                        self.n_collided += 1
                        self.n_total += 1
                        collided = True
                        break
                if collided:
                    continue
                if p["x"] >= x1:
                    self.n_transmitted += 1
                    self.n_total += 1
                    continue
                alive.append(p)
            self.particles = alive

            for hmark in self.hits:
                hmark[2] -= dt * 1.5
            self.hits = [hm for hm in self.hits if hm[2] > 0]

        self._update_readouts()

    def _update_readouts(self):
        w, h, x0, x1 = self._slab()
        area = (x1 - x0) * h
        sigma = 2.0 * self.radius                # 2-D cross-section (a length)
        n = len(self.targets) / area if area else 0
        lam = 1.0 / (n * sigma) if n * sigma > 0 else float("inf")
        self.r_sigma.set(f"{sigma:.0f} px")
        self.r_n.set(f"{n * 1e4:.2f} /10⁴px²")
        self.r_lambda.set("∞" if math.isinf(lam) else f"{lam:.0f} px")
        if self.n_collided:
            self.r_measured.set(f"{self.sum_path / self.n_collided:.0f} px")
        else:
            self.r_measured.set("-")
        if self.n_total:
            self.r_trans.set(f"{100.0 * self.n_transmitted / self.n_total:.0f} %")
        else:
            self.r_trans.set("-")

    # drawing --------------------------------------------------------------
    def render(self):
        c = self.canvas
        w, h, x0, x1 = self._slab()
        col = self.colors

        c.create_rectangle(x0, 8, x1, h - 8, outline="#334155", dash=(3, 5))
        c.create_text((x0 + x1) / 2, 20, text=self.t("topic.cross_section.slab"),
                      fill=col["canvas_text"], font=self.font("small"))
        c.create_text(x0 - 42, h / 2, text=self.t("topic.cross_section.beam"),
                      fill=col["canvas_text"], font=self.font("small"), angle=90)

        for (tx, ty, tr) in self.targets:
            c.create_oval(tx - tr, ty - tr, tx + tr, ty + tr,
                          fill="#1e3a5f", outline="#3b82f6")

        for p in self.particles:
            c.create_oval(p["x"] - 2.5, p["y"] - 2.5, p["x"] + 2.5, p["y"] + 2.5,
                          fill="#fde047", outline="")

        for (hx, hy, life) in self.hits:
            r = 4 + 8 * (1 - life)
            c.create_oval(hx - r, hy - r, hx + r, hy + r, outline="#f87171", width=2)
