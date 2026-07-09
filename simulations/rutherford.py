"""Section 2, Topic 4 - The Rutherford scattering formula.

Where the cloud-chamber view is qualitative, this one is quantitative. A single
nucleus scatters alpha particles and we test the scattering law directly:

    tan(theta / 2) = k Z / (E b)

- SINGLE mode: choose the impact parameter b and watch one hyperbolic orbit.
  The measured deflection angle is compared, live, with the value the formula
  predicts - they agree, which validates the law.
- BEAM mode: many alphas with random impact parameters rain onto the nucleus
  and the detector histogram builds up the Rutherford angular distribution,
  proportional to 1 / sin^4(theta / 2)  (overlaid as a smooth curve).

The motion is produced by integrating the Coulomb force in the same scaled
units used throughout, so "k Z / E" here is the constant coulomb / v0^2.
"""
import math
import random

from simulations.base import Simulation


class RutherfordSim(Simulation):
    title_key = "topic.rutherford.title"
    desc_key = "topic.rutherford.desc"

    N_BINS = 18   # 0..180 deg

    def __init__(self, master, app):
        self.energy = 55.0
        self.zcharge = 79.0
        self.impact = 26.0        # impact parameter b (px), single mode
        self.beam_mode = False
        self.alpha = None         # single-mode current particle
        self.last_path = None     # completed single-mode trail (faded)
        self.last_theta = None
        self.beam_alphas = []
        self.hist = [0] * self.N_BINS
        self.n_total = 0
        self.n_back = 0
        self._emit_acc = 0.0
        super().__init__(master, app)

    # controls -------------------------------------------------------------
    def build_controls(self, parent):
        import tkinter as tk
        from tkinter import ttk
        self.e_var, _ = self.add_slider(
            parent, self.t("topic.rutherford.energy"), 20, 120, self.energy,
            command=lambda v: setattr(self, "energy", v), fmt="{:.0f}",
        )
        self.z_var, _ = self.add_slider(
            parent, self.t("topic.rutherford.zcharge"), 10, 92, self.zcharge,
            command=lambda v: setattr(self, "zcharge", v), fmt="{:.0f}",
        )
        self.b_var, _ = self.add_slider(
            parent, self.t("topic.rutherford.impact"), 3, 90, self.impact,
            command=self._set_b, fmt="{:.0f} px",
        )
        self.beam_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(parent, text=self.t("topic.rutherford.beam_mode"),
                        variable=self.beam_var, command=self._toggle_mode,
                        style="Panel.TCheckbutton").pack(anchor="w", pady=(10, 0))

        self.r_theta = self.add_readout(parent, self.t("topic.rutherford.theta_measured"))
        self.r_pred = self.add_readout(parent, self.t("topic.rutherford.theta_formula"))
        self.r_total = self.add_readout(parent, self.t("topic.rutherford.fired"))
        self.r_back = self.add_readout(parent, self.t("topic.rutherford.backscatter"))

    def _set_b(self, v):
        self.impact = v
        self.alpha = None  # re-fire with the new impact parameter

    def _toggle_mode(self):
        self.beam_mode = self.beam_var.get()
        self.alpha = None
        self.last_path = None
        self.last_theta = None
        self.beam_alphas.clear()

    def reset(self):
        self.energy = 55.0
        self.zcharge = 79.0
        self.impact = 26.0
        self.beam_mode = False
        self.e_var.set(self.energy)
        self.z_var.set(self.zcharge)
        self.b_var.set(self.impact)
        self.beam_var.set(False)
        self.alpha = None
        self.last_path = None
        self.last_theta = None
        self.beam_alphas.clear()
        self.hist = [0] * self.N_BINS
        self.n_total = self.n_back = 0

    # geometry / physics helpers ------------------------------------------
    def _nucleus(self):
        w, h = self.cwh()
        return w, h, w * 0.44, h * 0.46

    def _v0(self):
        return 130.0 + self.energy * 2.0

    def _coulomb(self):
        return 320.0 * self.zcharge

    def _predicted_theta(self, b):
        """Rutherford formula:  tan(theta/2) = coulomb / (v0^2 * b)."""
        if b <= 0:
            return 180.0
        return math.degrees(2.0 * math.atan(self._coulomb() / (self._v0() ** 2 * b)))

    def _step_particle(self, a, nx, ny, dt):
        coulomb = self._coulomb()
        soft = 1.5
        steps = 12
        sdt = dt / steps
        for _ in range(steps):
            dx = a["x"] - nx
            dy = a["y"] - ny
            r2 = dx * dx + dy * dy + soft * soft
            f = coulomb / (r2 * math.sqrt(r2))
            a["vx"] += f * dx * sdt
            a["vy"] += f * dy * sdt
            a["x"] += a["vx"] * sdt
            a["y"] += a["vy"] * sdt
        a["pts"].extend((a["x"], a["y"]))

    @staticmethod
    def _theta_of(a):
        speed = math.hypot(a["vx"], a["vy"]) or 1.0
        return math.degrees(math.acos(max(-1.0, min(1.0, a["vx"] / speed))))

    # physics --------------------------------------------------------------
    def tick(self, dt):
        w, h, nx, ny = self._nucleus()
        if dt <= 0:
            self._update_readouts()
            return
        if self.beam_mode:
            self._tick_beam(dt, w, h, nx, ny)
        else:
            self._tick_single(dt, w, h, nx, ny)
        self._update_readouts()

    def _tick_single(self, dt, w, h, nx, ny):
        if self.alpha is None:
            y0 = ny - self.impact
            self.alpha = {"x": 6.0, "y": y0, "vx": self._v0(), "vy": 0.0, "pts": [6.0, y0]}
        a = self.alpha
        self._step_particle(a, nx, ny, dt)
        if not (0 <= a["x"] <= w and 0 <= a["y"] <= h):
            self.last_path = a["pts"]
            self.last_theta = self._theta_of(a)
            self.alpha = None

    def _tick_beam(self, dt, w, h, nx, ny):
        self._emit_acc += dt
        while self._emit_acc >= 0.05 and len(self.beam_alphas) < 50:
            self._emit_acc -= 0.05
            b = random.uniform(-90, 90)
            self.beam_alphas.append({"x": 6.0, "y": ny - b, "vx": self._v0(),
                                     "vy": 0.0, "pts": [6.0, ny - b]})
        for a in self.beam_alphas:
            self._step_particle(a, nx, ny, dt)
            if not (0 <= a["x"] <= w and 0 <= a["y"] <= h):
                theta = self._theta_of(a)
                idx = min(self.N_BINS - 1, int(theta / 180.0 * self.N_BINS))
                self.hist[idx] += 1
                self.n_total += 1
                if theta > 90:
                    self.n_back += 1
        self.beam_alphas = [a for a in self.beam_alphas if 0 <= a["x"] <= w and 0 <= a["y"] <= h]

    def _update_readouts(self):
        if self.beam_mode:
            self.r_theta.set("-")
            self.r_pred.set("-")
            self.r_total.set(str(self.n_total))
            tot = self.n_total or 1
            self.r_back.set(f"{self.n_back}  ({100.0 * self.n_back / tot:.1f}%)")
        else:
            self.r_theta.set(f"{self.last_theta:.0f}°" if self.last_theta is not None else "…")
            self.r_pred.set(f"{self._predicted_theta(self.impact):.0f}°")
            self.r_total.set("-")
            self.r_back.set("-")

    # drawing --------------------------------------------------------------
    def draw(self):
        c = self.canvas
        c.delete("all")
        w, h, nx, ny = self._nucleus()
        col = self.colors

        # beam axis
        c.create_line(0, ny, nx, ny, fill="#233047", dash=(4, 4))

        if self.beam_mode:
            self._draw_beam(c, w, h, nx, ny)
        else:
            self._draw_single(c, w, h, nx, ny)

        # nucleus
        c.create_oval(nx - 10, ny - 10, nx + 10, ny + 10, fill="#fbbf24", outline="#fde68a")
        c.create_text(nx, ny, text="+Ze", fill="#78350f", font=self.font("small"))

        # the formula, always on show
        c.create_text(20, h - 16, anchor="w",
                      text=self.t("topic.rutherford.formula"),
                      fill="#7dd3fc", font=self.font("base"))

    def _draw_single(self, c, w, h, nx, ny):
        # impact-parameter guide
        y_in = ny - self.impact
        c.create_line(0, y_in, nx, y_in, fill="#3b4a63", dash=(2, 4))
        c.create_line(nx, ny, nx, y_in, fill="#64748b")
        c.create_text(nx + 8, (ny + y_in) / 2, text="b", anchor="w",
                      fill=self.colors["canvas_text"], font=self.font("small"))
        c.create_text(46, y_in - 12, text=self.t("topic.rutherford.beam"),
                      fill=self.colors["canvas_text"], font=self.font("small"))

        if self.last_path and len(self.last_path) >= 4:
            c.create_line(*self.last_path, fill="#334a63", width=2, smooth=True)
        a = self.alpha
        if a and len(a["pts"]) >= 4:
            c.create_line(*a["pts"], fill="#fca5a5", width=2, smooth=True)
        if a:
            c.create_oval(a["x"] - 4, a["y"] - 4, a["x"] + 4, a["y"] + 4,
                          fill="#ef4444", outline="")

    def _draw_beam(self, c, w, h, nx, ny):
        for a in self.beam_alphas:
            if len(a["pts"]) >= 4:
                c.create_line(*a["pts"], fill="#7f1d1d", width=1)
            c.create_oval(a["x"] - 2, a["y"] - 2, a["x"] + 2, a["y"] + 2,
                          fill="#ef4444", outline="")
        self._draw_histogram(c, w, h)

    def _draw_histogram(self, c, w, h):
        base_y = h - 40
        left = 30
        width = w - 60
        bw = width / self.N_BINS
        peak = max(self.hist) or 1
        c.create_text(left, base_y - 96, anchor="w",
                      text=self.t("topic.rutherford.hist_title"),
                      fill=self.colors["canvas_text"], font=self.font("small"))
        c.create_line(left, base_y, left + width, base_y, fill="#334155")

        # measured bars
        for i, count in enumerate(self.hist):
            if not count:
                continue
            bh = 84 * count / peak
            x0 = left + i * bw + 2
            x1 = left + (i + 1) * bw - 2
            deg = (i + 0.5) / self.N_BINS * 180
            color = "#f87171" if deg > 90 else "#38bdf8"
            c.create_rectangle(x0, base_y - bh, x1, base_y, fill=color, outline="")

        # theory curve  1/sin^4(theta/2), scaled to the tallest measured bar
        pts = []
        theory_ref = None
        for i in range(self.N_BINS):
            deg = (i + 0.5) / self.N_BINS * 180
            s = math.sin(math.radians(deg) / 2)
            val = 1.0 / (s ** 4) if s > 1e-3 else 0.0
            if self.hist[i] and theory_ref is None:
                theory_ref = val / self.hist[i]  # match curve to data scale
            pts.append((i, val))
        if theory_ref:
            flat = []
            for i, val in pts:
                x = left + (i + 0.5) * bw
                y = base_y - min(84.0, 84.0 * (val / theory_ref) / peak)
                flat.extend((x, y))
            if len(flat) >= 4:
                c.create_line(*flat, fill="#fde047", width=2, smooth=True)
            c.create_text(left + width, base_y - 92, anchor="e",
                          text=self.t("topic.rutherford.theory"),
                          fill="#fde047", font=self.font("small"))
