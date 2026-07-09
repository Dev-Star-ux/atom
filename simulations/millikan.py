"""Topic 2 - Millikan oil-drop experiment (mass & charge of the electron).

A charged oil drop floats between two horizontal plates. Gravity pulls it
down; the electric field between the plates can push it up. By tuning the
voltage until the drop hovers, the charge is found from  q = m g d / V.
Every drop carries a whole-number multiple of the elementary charge e, which
is how the charge of a single electron is revealed.

Real physical constants are used so the readouts are realistic; the on-screen
motion is time-accelerated so the very slow drift is visible.
"""
import math
import random

from simulations.base import Simulation

E_CHARGE = 1.602e-19     # elementary charge (C)
G = 9.81                 # gravity (m/s^2)
RHO_OIL = 900.0          # oil density (kg/m^3)
ETA = 1.81e-5            # air viscosity (Pa s)
PLATE_GAP = 5.0e-3       # distance between plates (m)
TIME_SCALE = 400.0       # animation speed-up factor


class MillikanSim(Simulation):
    title_key = "topic.millikan.title"
    desc_key = "topic.millikan.desc"

    def __init__(self, master, app):
        self.voltage = 200.0
        self.drop = None
        super().__init__(master, app)
        self._new_drop()

    # controls -------------------------------------------------------------
    def build_controls(self, parent):
        from tkinter import ttk
        self.v_var, _ = self.add_slider(
            parent, self.t("topic.millikan.voltage"), 0, 600, self.voltage,
            command=lambda v: setattr(self, "voltage", v), fmt="{:.0f} V",
        )
        ttk.Button(parent, text=self.t("topic.millikan.new_drop"),
                   command=self._new_drop).pack(fill="x", pady=(12, 0))
        ttk.Button(parent, text=self.t("topic.millikan.balance"),
                   command=self._auto_balance).pack(fill="x", pady=(6, 0))

        self.r_radius = self.add_readout(parent, self.t("topic.millikan.radius"))
        self.r_mass = self.add_readout(parent, self.t("topic.millikan.mass"))
        self.r_charge = self.add_readout(parent, self.t("topic.millikan.measured_q"))
        self.r_n = self.add_readout(parent, self.t("topic.millikan.n_electrons"))
        self.r_status = self.add_readout(parent, self.t("topic.millikan.status"))

    def reset(self):
        self.voltage = 200.0
        self.v_var.set(self.voltage)
        self._new_drop()

    # drop setup -----------------------------------------------------------
    def _new_drop(self):
        r = random.uniform(0.4e-6, 1.1e-6)          # radius (m)
        mass = (4.0 / 3.0) * math.pi * r ** 3 * RHO_OIL
        n = random.randint(1, 6)                     # number of extra electrons
        q = n * E_CHARGE
        self.drop = {
            "r": r, "mass": mass, "n": n, "q": q,
            "y": 0.5, "v": 0.0,                       # y in fraction of gap (0 top .. 1 bottom)
            "drag": 6.0 * math.pi * ETA * r,
        }

    def _auto_balance(self):
        """Set the voltage so the current drop hovers (q E = m g)."""
        if self.drop:
            v = self.drop["mass"] * G * PLATE_GAP / self.drop["q"]
            self.voltage = max(0.0, min(600.0, v))
            self.v_var.set(self.voltage)

    # physics --------------------------------------------------------------
    def tick(self, dt):
        d = self.drop
        if d is None:
            return
        if dt > 0:
            sdt = dt * TIME_SCALE
            e_field = self.voltage / PLATE_GAP
            f_grav = d["mass"] * G                         # down (+y)
            f_elec = d["q"] * e_field                       # up (-y)
            f_drag = -d["drag"] * d["v"]                     # opposes motion
            accel = (f_grav - f_elec + f_drag) / d["mass"]
            d["v"] += accel * sdt
            d["y"] += (d["v"] / PLATE_GAP) * sdt            # convert m/s -> gap-fraction/s
            if d["y"] < 0.02:
                d["y"], d["v"] = 0.02, 0.0
            elif d["y"] > 0.98:
                d["y"], d["v"] = 0.98, 0.0
        self._update_readouts()

    def _update_readouts(self):
        d = self.drop
        self.r_radius.set(f"{d['r'] * 1e6:.2f} µm")
        self.r_mass.set(f"{d['mass'] * 1e15:.2f} fg")
        # measured charge from the balance condition at the current voltage
        if self.voltage > 1:
            q_meas = d["mass"] * G * PLATE_GAP / self.voltage
            self.r_charge.set(f"{q_meas:.2e} C")
            self.r_n.set(self.t("topic.millikan.n_value",
                                n=round(q_meas / E_CHARGE), e=f"{E_CHARGE:.3e}"))
        else:
            self.r_charge.set("-")
            self.r_n.set("-")
        if abs(d["v"]) < 2e-6:
            self.r_status.set(self.t("topic.millikan.balanced"))
        elif d["v"] > 0:
            self.r_status.set(self.t("topic.millikan.falling"))
        else:
            self.r_status.set(self.t("topic.millikan.rising"))

    # drawing --------------------------------------------------------------
    def draw(self):
        c = self.canvas
        c.delete("all")
        w = self.canvas.winfo_width() or 760
        h = self.canvas.winfo_height() or 460
        col = self.colors
        margin = 60
        top_y = margin
        bot_y = h - margin
        left = w * 0.18
        right = w * 0.82

        top_pos = True  # top plate positive -> field points down -> force on (-)charge is up
        c.create_rectangle(left, top_y - 14, right, top_y, fill="#ef4444", outline="")
        c.create_rectangle(left, bot_y, right, bot_y + 14, fill="#3b82f6", outline="")
        c.create_text(left - 16, top_y - 7, text="+", fill="#ef4444", font=self.font("heading"))
        c.create_text(left - 16, bot_y + 7, text="−", fill="#3b82f6", font=self.font("heading"))

        # field lines
        if self.voltage > 1:
            n_lines = 6
            for i in range(n_lines):
                x = left + (right - left) * (i + 0.5) / n_lines
                c.create_line(x, top_y, x, bot_y, fill="#1e293b", dash=(2, 6))

        # oil drop
        d = self.drop
        if d:
            py = top_y + (bot_y - top_y) * d["y"]
            px = (left + right) / 2
            rr = 8 + d["r"] * 1e6 * 4
            c.create_oval(px - rr, py - rr, px + rr, py + rr,
                          fill="#fbbf24", outline="#f59e0b")
            c.create_text(px, py, text=f"{d['n']}e⁻", fill="#78350f", font=self.font("small"))

            # force arrows
            cx = right + 34
            f_grav = d["mass"] * G
            f_elec = d["q"] * self.voltage / PLATE_GAP
            self._arrow(c, cx, py, 0, 34 * min(2, f_grav / (f_grav + 1e-30) + 0.6), "#f87171", "mg")
            if self.voltage > 1:
                scale = min(1.8, f_elec / (f_grav + 1e-30))
                self._arrow(c, cx, py, 0, -34 * scale, "#60a5fa", "qE")

        c.create_text((left + right) / 2, bot_y + 34,
                      text=self.t("topic.millikan.gap_label", d="5.0 mm"),
                      fill=col["canvas_text"], font=self.font("small"))

    def _arrow(self, c, x, y, dx, dy, color, label):
        c.create_line(x, y, x + dx, y + dy, fill=color, width=3, arrow="last")
        c.create_text(x + dx + 12, y + dy, text=label, fill=color, font=self.font("small"))
