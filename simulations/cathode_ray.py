"""Topic 1 - Discovery of the electron (Thomson's cathode-ray tube).

An electron beam is fired from the cathode, passes between two charged
deflecting plates and (optionally) through a magnetic field, then strikes a
fluorescent screen. The beam bends toward the positive plate, which reveals
that cathode rays carry negative charge.
"""
import random

from simulations.base import Simulation


class CathodeRaySim(Simulation):
    title_key = "topic.cathode_ray.title"
    desc_key = "topic.cathode_ray.desc"

    def __init__(self, master, app):
        self.voltage = 40.0     # deflecting-plate voltage (arbitrary units)
        self.bfield = 0.0       # magnetic field (arbitrary units)
        self.beam_on = True
        self.particles = []     # each: dict(x, y, vx, vy)
        self.spot_y = None      # smoothed screen impact position
        self._emit_acc = 0.0
        super().__init__(master, app)

    # controls -------------------------------------------------------------
    def build_controls(self, parent):
        self.v_var, _ = self.add_slider(
            parent, self.t("topic.cathode_ray.voltage"), -100, 100, self.voltage,
            command=lambda v: setattr(self, "voltage", v), fmt="{:+.0f} V",
        )
        self.b_var, _ = self.add_slider(
            parent, self.t("topic.cathode_ray.bfield"), -100, 100, self.bfield,
            command=lambda v: setattr(self, "bfield", v), fmt="{:+.0f}",
        )
        import tkinter as tk
        from tkinter import ttk
        self.beam_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            parent, text=self.t("topic.cathode_ray.beam_on"),
            variable=self.beam_var, command=lambda: setattr(self, "beam_on", self.beam_var.get()),
            style="Panel.TCheckbutton",
        ).pack(anchor="w", pady=(10, 0))

        self.r_deflect = self.add_readout(parent, self.t("topic.cathode_ray.deflection"))
        self.r_charge = self.add_readout(parent, self.t("topic.cathode_ray.sign"))

    def reset(self):
        self.voltage = 40.0
        self.bfield = 0.0
        self.beam_on = True
        self.particles.clear()
        self.spot_y = None
        self.v_var.set(self.voltage)
        self.b_var.set(self.bfield)
        self.beam_var.set(True)

    # geometry -------------------------------------------------------------
    def _geom(self):
        w = self.canvas.winfo_width() or 760
        h = self.canvas.winfo_height() or 460
        cy = h / 2
        gun_x = w * 0.10
        plate_x1 = w * 0.34
        plate_x2 = w * 0.58
        screen_x = w * 0.90
        return w, h, cy, gun_x, plate_x1, plate_x2, screen_x

    # physics --------------------------------------------------------------
    def tick(self, dt):
        w, h, cy, gun_x, px1, px2, screen_x = self._geom()
        speed = 320.0  # px/s horizontal

        if dt > 0:
            # emit electrons at a steady rate while the beam is on
            if self.beam_on:
                self._emit_acc += dt
                while self._emit_acc >= 0.03:
                    self._emit_acc -= 0.03
                    self.particles.append({"x": gun_x, "y": cy, "vx": speed, "vy": 0.0})

            # electric field force (electron is negative -> pushed toward + plate).
            # Top plate is positive when voltage > 0, so the beam bends up
            # (negative y in canvas coordinates).
            e_acc = -self.voltage * 22.0
            alive = []
            for p in self.particles:
                in_field = px1 <= p["x"] <= px2
                if in_field:
                    p["vy"] += e_acc * dt
                    # magnetic force ~ q v x B, perpendicular to velocity
                    p["vy"] += self.bfield * p["vx"] * 0.05 * dt * 20
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                if p["x"] >= screen_x:
                    hit = max(6, min(h - 6, p["y"]))
                    self.spot_y = hit if self.spot_y is None else self.spot_y * 0.7 + hit * 0.3
                    continue
                if 0 < p["y"] < h:
                    alive.append(p)
            self.particles = alive

        self._update_readouts(cy)

    def _update_readouts(self, cy):
        if self.spot_y is None:
            self.r_deflect.set("-")
        else:
            d = cy - self.spot_y
            if abs(d) < 4:
                self.r_deflect.set(self.t("topic.cathode_ray.dir_none"))
            elif d > 0:
                self.r_deflect.set(self.t("topic.cathode_ray.dir_up"))
            else:
                self.r_deflect.set(self.t("topic.cathode_ray.dir_down"))
        self.r_charge.set(self.t("topic.cathode_ray.negative"))

    # drawing --------------------------------------------------------------
    def draw(self):
        c = self.canvas
        c.delete("all")
        w, h, cy, gun_x, px1, px2, screen_x = self._geom()
        col = self.colors

        # baseline (undeflected path)
        c.create_line(gun_x, cy, screen_x, cy, fill="#33415c", dash=(4, 4))

        # electron gun / cathode
        c.create_rectangle(gun_x - 46, cy - 26, gun_x, cy + 26, fill="#334155", outline="#64748b")
        c.create_text(gun_x - 23, cy + 42, text=self.t("topic.cathode_ray.cathode"),
                      fill=col["canvas_text"], font=self.font("small"))

        # deflecting plates (top sign follows voltage polarity)
        top_pos = self.voltage >= 0
        top_sign, bot_sign = ("+", "-") if top_pos else ("-", "+")
        top_col = "#ef4444" if top_pos else "#3b82f6"
        bot_col = "#3b82f6" if top_pos else "#ef4444"
        c.create_rectangle(px1, cy - 92, px2, cy - 80, fill=top_col, outline="")
        c.create_rectangle(px1, cy + 80, px2, cy + 92, fill=bot_col, outline="")
        c.create_text((px1 + px2) / 2, cy - 104, text=top_sign, fill=top_col, font=self.font("heading"))
        c.create_text((px1 + px2) / 2, cy + 104, text=bot_sign, fill=bot_col, font=self.font("heading"))

        # magnetic field region indicator
        if abs(self.bfield) > 1:
            c.create_text(px2 + 24, cy - 60,
                          text="B " + ("⊙" if self.bfield > 0 else "⊗"),
                          fill="#a78bfa", font=self.font("base"))

        # fluorescent screen
        c.create_rectangle(screen_x, cy - 120, screen_x + 14, cy + 120,
                           fill="#0b3d2e", outline="#10b981")
        c.create_text(screen_x + 7, cy + 138, text=self.t("topic.cathode_ray.screen"),
                      fill=col["canvas_text"], font=self.font("small"))

        # electrons
        for p in self.particles:
            c.create_oval(p["x"] - 3, p["y"] - 3, p["x"] + 3, p["y"] + 3,
                          fill="#67e8f9", outline="")

        # glowing screen spot
        if self.spot_y is not None:
            for r, color in ((14, "#064e3b"), (9, "#10b981"), (4, "#a7f3d0")):
                c.create_oval(screen_x + 7 - r, self.spot_y - r,
                              screen_x + 7 + r, self.spot_y + r, fill=color, outline="")
