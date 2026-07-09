"""Chapter 3, Section 4, Topic 2 - Particle in an infinite square well.

A particle confined to 0 < x < a by infinitely high walls has normalised
eigenfunctions

    ψ_n(x) = √(2/a) sin(nπx/a)

and quantised energies  E_n = n² π² ħ² / (2m a²).  The wave function must
vanish at the walls; only integer numbers of half-wavelengths fit inside the
box. This is one of the first exactly solvable models of quantum mechanics.
"""
import math

from simulations.base import Simulation
from simulations.plot import Plot
import simulations.wavefunction as wf


class InfiniteWellSim(Simulation):
    title_key = "topic.infinite_well.title"
    desc_key = "topic.infinite_well.desc"

    def __init__(self, master, app):
        self.n = 2
        self.box_a = 1.0e-9   # 1 nm
        self._phase = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        self.n_var, _ = self.add_slider(
            parent, self.t("topic.infinite_well.level"), 1, 6, self.n,
            command=lambda v: setattr(self, "n", int(round(v))), fmt="n = {:.0f}",
        )
        self.a_var, _ = self.add_slider(
            parent, self.t("topic.infinite_well.width"), 0.5, 2.0, self.box_a * 1e9,
            command=lambda v: setattr(self, "box_a", v * 1e-9), fmt="{:.1f} nm",
        )
        self.r_energy = self.add_readout(parent, self.t("topic.infinite_well.energy"))
        self.r_nodes = self.add_readout(parent, self.t("topic.infinite_well.nodes"))
        self.r_ratio = self.add_readout(parent, self.t("topic.infinite_well.ratio"))

    def reset(self):
        self.n = 2
        self.box_a = 1.0e-9
        self.n_var.set(self.n)
        self.a_var.set(self.box_a * 1e9)
        self._phase = 0.0

    def tick(self, dt):
        if dt > 0:
            E = wf.infinite_well_energy_J(self.n, self.box_a)
            self._phase = (self._phase + dt * E / 6.62607015e-34 * 0.02) % (2 * math.pi)

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        a = self.box_a
        E = wf.infinite_well_energy_eV(self.n, a)
        E1 = wf.infinite_well_ground_eV(a)

        self.r_energy.set(f"E_{self.n} = {E:.3f} eV")
        self.r_nodes.set(str(self.n - 1))
        self.r_ratio.set(f"E_{self.n}/E₁ = {self.n * self.n}")

        # potential diagram + box
        vx0, vx1 = w * 0.10, w * 0.58
        vy0, vy1 = h * 0.12, h * 0.52
        wall_h = h * 0.08

        # V(x): infinite walls
        c.create_rectangle(vx0, vy0, vx0 + 8, vy1, fill="#ef4444", outline="#fecaca")
        c.create_rectangle(vx1 - 8, vy0, vx1, vy1, fill="#ef4444", outline="#fecaca")
        c.create_line(vx0 + 8, vy1, vx1 - 8, vy1, fill="#64748b", width=2)
        c.create_text((vx0 + vx1) / 2, vy1 + 16, text="V = 0",
                      fill=col["canvas_text"], font=self.font("tiny"))
        c.create_text(vx0 - 4, vy0 + 10, text="V = ∞", fill="#f87171",
                      font=self.font("tiny"), anchor="e")
        c.create_text(vx1 + 4, vy0 + 10, text="V = ∞", fill="#f87171",
                      font=self.font("tiny"), anchor="w")
        c.create_text((vx0 + vx1) / 2, vy0 - 10,
                      text=self.t("topic.infinite_well.potential"),
                      fill=col["accent2"], font=self.font("small"))

        # ψ(x) inside box
        n_pts = 100
        xs = [a * i / (n_pts - 1) for i in range(n_pts)]
        psis = [wf.infinite_well_psi(self.n, x, a) for x in xs]
        ymax = max(abs(v) for v in psis) or 1.0
        for i, (x, psi) in enumerate(zip(xs, psis)):
            px = vx0 + 8 + (vx1 - vx0 - 16) * x / a
            py = vy1 - (vy1 - vy0 - wall_h) * (psi / ymax + 1) * 0.45
            if i > 0:
                px0 = vx0 + 8 + (vx1 - vx0 - 16) * xs[i - 1] / a
                py0 = vy1 - (vy1 - vy0 - wall_h) * (psis[i - 1] / ymax + 1) * 0.45
                c.create_line(px0, py0, px, py, fill="#38bdf8", width=2)

        c.create_text((vx0 + vx1) / 2, vy1 + 36,
                      text=self.t("topic.infinite_well.psi_in_box", n=self.n),
                      fill=col["canvas_text"], font=self.font("tiny"))

        # energy ladder (right)
        lx0, lx1 = w * 0.66, w * 0.82
        top, bot = h * 0.14, h * 0.50
        for lvl in range(1, 7):
            frac = (lvl - 1) / 5
            y = bot - (bot - top) * frac
            hl = lvl == self.n
            c.create_line(lx0, y, lx1, y,
                          fill=col["accent"] if hl else "#475569",
                          width=2 if hl else 1)
            En = wf.infinite_well_energy_eV(lvl, a)
            c.create_text(lx0 - 6, y, text=f"n={lvl}", anchor="e",
                          fill=col["canvas_text"], font=self.font("tiny"))
            c.create_text(lx1 + 6, y, text=f"{En:.2f} eV", anchor="w",
                          fill=col["muted"] if not hl else col["accent2"],
                          font=self.font("tiny"))

        c.create_text((lx0 + lx1) / 2, top - 10,
                      text=self.t("topic.infinite_well.levels"),
                      fill=col["accent2"], font=self.font("small"))

        # |ψ|² plot (bottom)
        box = (72, h * 0.58, w - 28, h - 40)
        probs = [wf.infinite_well_prob(self.n, x, a) for x in xs]
        p = Plot(c, box, (0, a * 1e9), (0, max(probs) * 1.15 or 1), col, self.font("small"))
        p.axes(self.t("topic.infinite_well.x_axis"),
               self.t("topic.infinite_well.prob_axis"),
               (0, a * 1e9 / 2, a * 1e9))
        p.curve([x * 1e9 for x in xs], probs, "#f472b6", width=2)

        c.create_text(w * 0.5, h * 0.54,
                      text=self.t("topic.infinite_well.formula"),
                      fill=col["muted"], font=self.font("tiny"))
