"""Chapter 3, Section 4, Topic 1 - Discovery of the Schrödinger equation.

In 1926 Erwin Schrödinger published a wave equation governing the time
evolution of the matter-wave amplitude ψ. The time-dependent form is

    iħ ∂ψ/∂t = Ĥψ     (Ĥ = −ħ²/2m ∇² + V)

For a particle confined in a box, solutions are standing waves ψ_n(x). A
superposition ψ = c₁ψ₁ + c₂ψ₂ evolves in time: |ψ(x,t)|² oscillates,
showing that the Schrödinger equation predicts dynamical probability flow.
"""
import math

from simulations.base import Simulation
from simulations.plot import Plot
import simulations.wavefunction as wf


class SchrodingerDiscoverySim(Simulation):
    title_key = "topic.schrodinger_discovery.title"
    desc_key = "topic.schrodinger_discovery.desc"

    def __init__(self, master, app):
        self.n1 = 1
        self.n2 = 2
        self.box_a = 1.0e-9
        self._t = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        self.n1_var, _ = self.add_slider(
            parent, self.t("topic.schrodinger_discovery.level1"), 1, 4, self.n1,
            command=lambda v: setattr(self, "n1", int(round(v))), fmt="n₁ = {:.0f}",
        )
        self.n2_var, _ = self.add_slider(
            parent, self.t("topic.schrodinger_discovery.level2"), 2, 5, self.n2,
            command=lambda v: setattr(self, "n2", max(self.n1 + 1, int(round(v)))),
            fmt="n₂ = {:.0f}",
        )
        self.r_e1 = self.add_readout(parent, self.t("topic.schrodinger_discovery.energy1"))
        self.r_e2 = self.add_readout(parent, self.t("topic.schrodinger_discovery.energy2"))
        self.r_time = self.add_readout(parent, self.t("topic.schrodinger_discovery.time"))

    def reset(self):
        self.n1 = 1
        self.n2 = 2
        self._t = 0.0
        self.n1_var.set(self.n1)
        self.n2_var.set(self.n2)

    def tick(self, dt):
        if dt > 0:
            self._t += dt * 0.4

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        a = self.box_a
        if self.n2 <= self.n1:
            self.n2 = self.n1 + 1

        E1 = wf.infinite_well_energy_eV(self.n1, a)
        E2 = wf.infinite_well_energy_eV(self.n2, a)
        self.r_e1.set(f"E_{self.n1} = {E1:.3f} eV")
        self.r_e2.set(f"E_{self.n2} = {E2:.3f} eV")
        self.r_time.set(f"t = {self._t:.2f} (arb.)")

        # equation panel
        c.create_text(w * 0.5, 22, text=self.t("topic.schrodinger_discovery.equation"),
                      fill=col["accent2"], font=self.font("bold"))
        c.create_text(w * 0.5, 44, text=self.t("topic.schrodinger_discovery.hint"),
                      fill=col["muted"], font=self.font("tiny"))

        # ψ(x,t) real part
        box1 = (72, 58, w - 28, h * 0.44)
        xs = [a * i / 99 for i in range(100)]
        psis = [wf.psi_superposition(x, a, self.n1, self.n2, self._t, 0.15) for x in xs]
        ymax = max(abs(v) for v in psis) or 1.0
        p1 = Plot(c, box1, (0, a * 1e9), (-ymax * 1.1, ymax * 1.1), col, self.font("small"))
        p1.axes(self.t("topic.schrodinger_discovery.x_axis"),
                self.t("topic.schrodinger_discovery.psi_axis"),
                (0, a * 1e9 / 2, a * 1e9))
        p1.curve([x * 1e9 for x in xs], psis, "#38bdf8", width=2)
        c.create_line(p1.X(0), p1.Y(0), p1.X(a * 1e9), p1.Y(0), fill="#334155")

        c.create_text((box1[0] + box1[2]) / 2, 52,
                      text=self.t("topic.schrodinger_discovery.psi_title"),
                      fill=col["accent2"], font=self.font("small"))

        # |ψ|² at time t
        box2 = (72, h * 0.54, w - 28, h - 44)
        probs = [wf.prob_superposition(x, a, self.n1, self.n2, self._t, 0.15) for x in xs]
        ymax2 = max(probs) or 1.0
        p2 = Plot(c, box2, (0, a * 1e9), (0, ymax2 * 1.15), col, self.font("small"))
        p2.axes(self.t("topic.schrodinger_discovery.x_axis"),
                self.t("topic.schrodinger_discovery.prob_axis"),
                (0, a * 1e9 / 2, a * 1e9))
        p2.curve([x * 1e9 for x in xs], probs, "#f472b6", width=2)

        c.create_text((box2[0] + box2[2]) / 2, h * 0.50,
                      text=self.t("topic.schrodinger_discovery.prob_title"),
                      fill=col["accent2"], font=self.font("small"))
        c.create_text(w * 0.5, h - 12,
                      text=self.t("topic.schrodinger_discovery.note"),
                      fill=col["muted"], font=self.font("tiny"))
