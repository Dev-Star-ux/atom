"""Chapter 2, Section 3, Topic 2 - Frank–Hertz experiment.

Electrons are accelerated through a low-pressure gas. When their kinetic energy
reaches the first excitation energy of the atoms, inelastic collisions drain
energy and fewer electrons reach the collector — a dip in the current. Repeating
dips at 2E₀, 3E₀, … prove that atomic excitation is quantised.
"""
import math
import random

from simulations.base import Simulation
from simulations.plot import Plot
import simulations.atom as atom

GASES = ("mercury", "neon")
V_MAX = 25.0


class FrankHertzSim(Simulation):
    title_key = "topic.frank_hertz.title"
    desc_key = "topic.frank_hertz.desc"

    def __init__(self, master, app):
        self.gas = "mercury"
        self.voltage = 6.0
        self.electrons = []
        self._spawn = 0.0
        self._history = []   # (V, I) points for the I–V trace
        super().__init__(master, app)

    def build_controls(self, parent):
        from tkinter import ttk
        import tkinter as tk

        ttk.Label(parent, text=self.t("topic.frank_hertz.gas"),
                  style="Panel.TLabel").pack(anchor="w", pady=(0, 2))
        self._gas_keys = list(GASES)
        self.gas_var = tk.StringVar()
        combo = ttk.Combobox(
            parent, state="readonly", textvariable=self.gas_var,
            values=[self.t("gas." + g) for g in self._gas_keys],
        )
        combo.current(self._gas_keys.index(self.gas))
        combo.pack(fill="x")
        combo.bind("<<ComboboxSelected>>", self._on_gas)

        self.v_var, _ = self.add_slider(
            parent, self.t("topic.frank_hertz.voltage"), 0, V_MAX, self.voltage,
            command=self._on_voltage, fmt="{:.1f} V",
        )
        self.r_exc = self.add_readout(parent, self.t("topic.frank_hertz.excitation"))
        self.r_current = self.add_readout(parent, self.t("topic.frank_hertz.current"))
        self.r_peak = self.add_readout(parent, self.t("topic.frank_hertz.next_dip"))

    def _on_gas(self, _e):
        labels = [self.t("gas." + g) for g in self._gas_keys]
        self.gas = self._gas_keys[labels.index(self.gas_var.get())]
        self._history.clear()

    def _on_voltage(self, v):
        self.voltage = v
        I = atom.frank_hertz_current(v, atom.GASES[self.gas])
        self._history.append((v, I))
        if len(self._history) > 400:
            self._history = self._history[-400:]

    def _E0(self):
        return atom.GASES[self.gas]

    def reset(self):
        self.gas = "mercury"
        self.voltage = 6.0
        self.gas_var.set(self.t("gas.mercury"))
        self.v_var.set(self.voltage)
        self.electrons.clear()
        self._history.clear()

    def tick(self, dt):
        w, h = self.cwh()
        if dt <= 0:
            return
        E0 = self._E0()
        cath_x = w * 0.14
        grid_x = w * 0.28
        coll_x = w * 0.42
        cy = h * 0.28
        tube_len = coll_x - cath_x

        self._spawn += dt * 4.0
        while self._spawn >= 1.0:
            self._spawn -= 1.0
            self.electrons.append({
                "x": 0.0, "y": cy + random.uniform(-18, 18),
                "ke": 0.0, "inelastic": 0,
            })

        speed_scale = 90.0
        for e in self.electrons:
            frac = e["x"] / tube_len
            ke = self.voltage * frac
            # inelastic collision when KE crosses n·E₀
            n_max = int(ke / E0) if E0 > 0 else 0
            if n_max > e["inelastic"] and random.random() < 0.35:
                e["inelastic"] = n_max
                ke -= E0
            e["ke"] = max(0.05, ke)
            e["x"] += speed_scale * math.sqrt(e["ke"]) * dt
        self.electrons = [e for e in self.electrons if e["x"] < tube_len + 20]

    def _next_dip(self):
        E0 = self._E0()
        n = max(1, int(self.voltage / E0) + 1)
        return n * E0

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        E0 = self._E0()
        I = atom.frank_hertz_current(self.voltage, E0)

        self.r_exc.set(f"{E0:.2f} eV")
        self.r_current.set(f"{I:.2f} (rel.)")
        self.r_peak.set(f"{self._next_dip():.1f} V")

        # --- tube apparatus --------------------------------------------------
        cy = h * 0.28
        cath_x, grid_x, coll_x = w * 0.14, w * 0.28, w * 0.42
        tube_y0, tube_y1 = cy - 32, cy + 32

        c.create_rectangle(cath_x - 8, tube_y0, coll_x + 12, tube_y1,
                           fill="#0f172a", outline="#475569", width=2)
        c.create_rectangle(cath_x - 14, tube_y0 + 6, cath_x - 4, tube_y1 - 6,
                           fill="#64748b", outline="#94a3b8")
        c.create_text(cath_x - 20, cy, text=self.t("topic.frank_hertz.cathode"),
                      fill=col["canvas_text"], font=self.font("tiny"), anchor="e")
        c.create_line(grid_x, tube_y0 - 4, grid_x, tube_y1 + 4, fill="#fbbf24", width=3)
        c.create_text(grid_x, tube_y1 + 16, text=self.t("topic.frank_hertz.grid"),
                      fill=col["canvas_text"], font=self.font("tiny"), anchor="n")
        c.create_rectangle(coll_x, tube_y0 + 4, coll_x + 8, tube_y1 - 4,
                           fill="#64748b", outline="#94a3b8")
        c.create_text(coll_x + 20, cy, text=self.t("topic.frank_hertz.collector"),
                      fill=col["canvas_text"], font=self.font("tiny"), anchor="w")

        # gas label
        c.create_text((grid_x + coll_x) / 2, cy,
                      text=self.t("gas." + self.gas),
                      fill=col["muted"], font=self.font("tiny"))

        # electrons
        for e in self.electrons:
            ex = cath_x + e["x"]
            ec = col["bad"] if e["inelastic"] > 0 else col["accent2"]
            c.create_oval(ex - 3, e["y"] - 3, ex + 3, e["y"] + 3, fill=ec, outline="")

        # voltage arrow
        c.create_text(cath_x - 20, tube_y0 - 18,
                      text=self.t("topic.frank_hertz.v_label", v=f"{self.voltage:.1f}"),
                      fill=col["accent"], font=self.font("small"), anchor="w")

        # --- I–V plot --------------------------------------------------------
        plot_top = h * 0.58
        box = (60, plot_top, w - 28, h - 50)
        ymax = atom.frank_hertz_current(V_MAX, E0) * 1.1 or 1.0
        p = Plot(c, box, (0, V_MAX), (0, ymax), col, self.font("small"))
        p.axes(self.t("topic.frank_hertz.v_axis"),
               self.t("topic.frank_hertz.i_axis"),
               (0, 5, 10, 15, 20, 25))

        # theoretical curve
        n_pts = 80
        vs = [V_MAX * i / (n_pts - 1) for i in range(n_pts)]
        Is = [atom.frank_hertz_current(v, E0) for v in vs]
        p.curve(vs, Is, col["accent"], width=2)

        # mark excitation thresholds
        for n in range(1, 6):
            Ve = n * E0
            if Ve <= V_MAX:
                p.vline(Ve, col["warn"], dash=(2, 4))

        # scanned history
        if self._history:
            hx = [pt[0] for pt in self._history]
            hy = [pt[1] for pt in self._history]
            p.curve(hx, hy, col["accent2"], width=1, dash=(4, 2))

        # current operating point
        p.label(self.voltage, I, "●", col["good"], anchor="center")

        c.create_text(w * 0.5, plot_top - 14,
                      text=self.t("topic.frank_hertz.iv_title"),
                      fill=col["accent2"], font=self.font("small"))
