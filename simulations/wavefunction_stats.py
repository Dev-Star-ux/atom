"""Chapter 3, Section 3, Topic 2 - Statistical analysis of the wave function.

Born's rule: the probability of finding a particle in a small interval dx is
|ψ(x)|² dx. The wave function itself is not directly observable — only the
statistical distribution of many position measurements. Fire many 'detections'
and watch the histogram converge to |ψ|².
"""
import math

from simulations.base import Simulation
from simulations.plot import Plot
import simulations.wavefunction as wf


class WavefunctionStatsSim(Simulation):
    title_key = "topic.wavefunction_stats.title"
    desc_key = "topic.wavefunction_stats.desc"

    def __init__(self, master, app):
        self.n_level = 2
        self.box_a = 1.0e-9   # 1 nm box
        self.hits = []
        self._burst = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        self.n_var, _ = self.add_slider(
            parent, self.t("topic.wavefunction_stats.level"), 1, 5, self.n_level,
            command=lambda v: setattr(self, "n_level", int(round(v))), fmt="n = {:.0f}",
        )
        self.r_total = self.add_readout(parent, self.t("topic.wavefunction_stats.total"))
        self.r_norm = self.add_readout(parent, self.t("topic.wavefunction_stats.normalised"))

        from tkinter import ttk
        ttk.Button(parent, text=self.t("topic.wavefunction_stats.fire"),
                   command=self._fire_batch).pack(fill="x", pady=(10, 0))

    def _prob(self, x):
        return wf.infinite_well_prob(self.n_level, x, self.box_a)

    def _fire_batch(self):
        for _ in range(25):
            self.hits.append(wf.sample_from_prob(self._prob, 0, self.box_a))

    def reset(self):
        self.n_level = 2
        self.hits.clear()
        self.n_var.set(self.n_level)

    def tick(self, dt):
        pass

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        a = self.box_a

        self.r_total.set(str(len(self.hits)))
        self.r_norm.set(self.t("topic.wavefunction_stats.yes"))

        # |ψ|² theory (top)
        box1 = (72, 28, w - 28, h * 0.38)
        xs = [a * i / 99 for i in range(100)]
        ps = [self._prob(x) for x in xs]
        ymax = max(ps) or 1.0
        p1 = Plot(c, box1, (0, a * 1e9), (0, ymax * 1.15), col, self.font("small"))
        p1.axes(self.t("topic.wavefunction_stats.x_axis"),
                self.t("topic.wavefunction_stats.psi2_axis"),
                (0, a * 1e9 / 2, a * 1e9))
        p1.curve([x * 1e9 for x in xs], ps, "#38bdf8", width=2)

        c.create_text((box1[0] + box1[2]) / 2, 14,
                      text=self.t("topic.wavefunction_stats.theory_title"),
                      fill=col["accent2"], font=self.font("small"))

        # histogram of detections (bottom)
        box2 = (72, h * 0.48, w - 28, h - 44)
        bins = 20
        hist = [0] * bins
        for x in self.hits:
            b = min(bins - 1, int(x / a * bins))
            hist[b] += 1
        hmax = max(hist) or 1
        bx = [a * (i + 0.5) / bins * 1e9 for i in range(bins)]
        p2 = Plot(c, box2, (0, a * 1e9), (0, hmax * 1.15), col, self.font("small"))
        p2.axes(self.t("topic.wavefunction_stats.x_axis"),
                self.t("topic.wavefunction_stats.count_axis"),
                (0, a * 1e9 / 2, a * 1e9))
        # bar chart via vertical lines
        for i, count in enumerate(hist):
            if count > 0:
                x_nm = a * (i + 0.5) / bins * 1e9
                half_w = a * 1e9 / bins / 2
                c.create_rectangle(
                    p2.X(x_nm - half_w), p2.Y(count),
                    p2.X(x_nm + half_w), p2.Y(0),
                    fill="#4ade80", outline="")

        c.create_text((box2[0] + box2[2]) / 2, h * 0.44,
                      text=self.t("topic.wavefunction_stats.hist_title"),
                      fill=col["accent2"], font=self.font("small"))

        c.create_text(w * 0.5, h - 14,
                      text=self.t("topic.wavefunction_stats.note"),
                      fill=col["muted"], font=self.font("tiny"))
