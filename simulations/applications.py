"""Chapter 2, Section 2, Topic 4 - Applications of the photoelectric effect.

Two devices, selectable from the drop-down:

* Photomultiplier tube (PMT): a photon frees one electron at the photocathode;
  it is accelerated onto a dynode that emits several secondary electrons, and
  the cascade repeats down a chain of dynodes, so a single photon becomes a
  large, measurable pulse (gain ~ delta^N).

* Solar cell: photons striking a p-n junction create electron-hole pairs; the
  built-in field sweeps them to opposite contacts, driving a current through an
  external load - light turned directly into electrical power.
"""
import math
import random

from simulations.base import Simulation
import simulations.photo as photo


class ApplicationsSim(Simulation):
    title_key = "topic.applications.title"
    desc_key = "topic.applications.desc"

    def __init__(self, master, app):
        self.device = "pmt"
        # PMT
        self.n_dynodes = 6
        self.delta = 3.0
        self.pmt_particles = []     # dict(x, y, stage)
        self._pmt_emit = 0.0
        self.last_gain = 0
        # Solar
        self.intensity = 60.0
        self.carriers = []          # dict(x, y, kind 'e'/'h', vx, vy)
        self._solar_emit = 0.0
        self.current = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        from tkinter import ttk
        import tkinter as tk
        ttk.Label(parent, text=self.t("topic.applications.device"),
                  style="Panel.TLabel").pack(anchor="w")
        self._devs = ["pmt", "solar"]
        self.dev_var = tk.StringVar()
        combo = ttk.Combobox(parent, state="readonly", textvariable=self.dev_var,
                             values=[self.t("topic.applications." + d) for d in self._devs])
        combo.current(0)
        combo.pack(fill="x", pady=(2, 8))
        combo.bind("<<ComboboxSelected>>", self._on_dev)
        self._combo = combo

        # PMT controls
        self.pmt_frame = ttk.Frame(parent, style="Panel.TFrame")
        self.pmt_frame.pack(fill="x")
        self.nd_var, _ = self.add_slider(
            self.pmt_frame, self.t("topic.applications.dynodes"), 3, 10, self.n_dynodes,
            command=lambda v: setattr(self, "n_dynodes", int(round(v))), fmt="{:.0f}",
        )
        self.dl_var, _ = self.add_slider(
            self.pmt_frame, self.t("topic.applications.secondary"), 2, 5, self.delta,
            command=lambda v: setattr(self, "delta", v), fmt="{:.1f}×",
        )
        self.r_gain = self.add_readout(self.pmt_frame, self.t("topic.applications.gain"))

        # Solar controls
        self.solar_frame = ttk.Frame(parent, style="Panel.TFrame")
        self.il_var, _ = self.add_slider(
            self.solar_frame, self.t("topic.applications.intensity"), 0, 100, self.intensity,
            command=lambda v: setattr(self, "intensity", v), fmt="{:.0f}%",
        )
        self.r_current = self.add_readout(self.solar_frame, self.t("topic.applications.current"))
        self.r_power = self.add_readout(self.solar_frame, self.t("topic.applications.power"))
        self._sync_panels()

    def _on_dev(self, _e):
        labels = [self.t("topic.applications." + d) for d in self._devs]
        self.device = self._devs[labels.index(self.dev_var.get())]
        self.pmt_particles.clear()
        self.carriers.clear()
        self._sync_panels()

    def _sync_panels(self):
        if self.device == "pmt":
            self.solar_frame.pack_forget()
            self.pmt_frame.pack(fill="x")
        else:
            self.pmt_frame.pack_forget()
            self.solar_frame.pack(fill="x")

    def reset(self):
        self.device = "pmt"
        self.n_dynodes = 6
        self.delta = 3.0
        self.intensity = 60.0
        self.dev_var.set(self.t("topic.applications.pmt"))
        self.nd_var.set(self.n_dynodes)
        self.dl_var.set(self.delta)
        self.il_var.set(self.intensity)
        self.pmt_particles.clear()
        self.carriers.clear()
        self.current = 0.0
        self._sync_panels()

    # physics --------------------------------------------------------------
    def tick(self, dt):
        if self.device == "pmt":
            self._tick_pmt(dt)
        else:
            self._tick_solar(dt)

    def _dynode_xy(self, w, h, i):
        """Position of dynode i (0..n-1), zig-zagging down the tube."""
        x0, x1 = w * 0.16, w * 0.82
        x = x0 + (x1 - x0) * i / max(1, self.n_dynodes)
        y = h * 0.34 + (h * 0.18) * (1 if i % 2 else -1)
        return x, y

    def _tick_pmt(self, dt):
        w, h = self.cwh()
        if dt <= 0:
            return
        # launch a photoelectron from the photocathode now and then
        self._pmt_emit += dt
        if self._pmt_emit >= 1.4 and len(self.pmt_particles) < 400:
            self._pmt_emit = 0.0
            self.pmt_particles = [{"x": w * 0.08, "y": h * 0.30, "stage": 0}]
            self.last_gain = 1
        tx = {}
        for p in self.pmt_particles:
            if p["stage"] >= self.n_dynodes:
                target = (w * 0.9, h * 0.34)
            else:
                target = self._dynode_xy(w, h, p["stage"])
            dx, dy = target[0] - p["x"], target[1] - p["y"]
            dist = math.hypot(dx, dy) or 1.0
            sp = 300.0 * dt
            if dist <= sp:
                p["x"], p["y"] = target
                p["arrived"] = True
            else:
                p["x"] += dx / dist * sp
                p["y"] += dy / dist * sp
        # handle arrivals: multiply at dynodes, collect at anode
        new_particles = []
        for p in self.pmt_particles:
            if p.get("arrived"):
                if p["stage"] >= self.n_dynodes:
                    continue  # collected at anode
                n_sec = max(2, int(self.delta))
                for _ in range(n_sec):
                    if len(new_particles) + len(self.pmt_particles) < 600:
                        new_particles.append({
                            "x": p["x"], "y": p["y"] + random.uniform(-6, 6),
                            "stage": p["stage"] + 1})
                self.last_gain = self.last_gain * n_sec if p["stage"] == 0 else self.last_gain
            else:
                new_particles.append(p)
        self.pmt_particles = new_particles
        gain = int(round(max(2, int(self.delta)) ** self.n_dynodes))
        self.r_gain.set(self.t("topic.applications.gain_val", g=f"{gain:,}"))

    def _tick_solar(self, dt):
        w, h = self.cwh()
        if dt <= 0:
            return
        jx = w * 0.5
        self._solar_emit += dt * self.intensity / 100.0 * 8.0
        while self._solar_emit >= 1.0 and len(self.carriers) < 200:
            self._solar_emit -= 1.0
            y = random.uniform(h * 0.24, h * 0.6)
            # a photon creates an electron-hole pair near the junction
            self.carriers.append({"x": jx, "y": y, "kind": "e", "vx": 130.0, "vy": 0.0})
            self.carriers.append({"x": jx, "y": y, "kind": "h", "vx": -130.0, "vy": 0.0})
        for cpt in self.carriers:
            cpt["x"] += cpt["vx"] * dt
        self.carriers = [cp for cp in self.carriers if w * 0.14 < cp["x"] < w * 0.86]
        target = self.intensity
        self.current += (target - self.current) * min(1.0, dt * 5)
        i_ua = self.current * 0.4
        self.r_current.set(f"{i_ua:.1f} µA")
        self.r_power.set(f"{i_ua * 0.5:.1f} µW")

    # drawing --------------------------------------------------------------
    def draw(self):
        if self.device == "pmt":
            self._draw_pmt()
        else:
            self._draw_solar()

    def _draw_pmt(self):
        c = self.canvas
        c.delete("all")
        w, h = self.cwh()
        col = self.colors
        c.create_rectangle(w * 0.05, h * 0.10, w * 0.95, h * 0.66, outline="#334155")
        # photocathode
        c.create_line(w * 0.08, h * 0.18, w * 0.08, h * 0.42, fill="#22d3ee", width=4)
        c.create_text(w * 0.08, h * 0.46, text=self.t("topic.applications.photocathode"),
                      fill=col["canvas_text"], font=self.font("small"))
        # incoming photon
        c.create_line(w * 0.02, h * 0.24, w * 0.075, h * 0.30, fill="#fde047",
                      width=3, arrow="last")
        # dynodes
        for i in range(self.n_dynodes):
            x, y = self._dynode_xy(w, h, i)
            c.create_line(x - 14, y - 10, x + 14, y + 10, fill="#94a3b8", width=4)
        # anode
        c.create_line(w * 0.9, h * 0.24, w * 0.9, h * 0.44, fill="#f59e0b", width=4)
        c.create_text(w * 0.9, h * 0.48, text=self.t("topic.applications.anode"),
                      fill=col["canvas_text"], font=self.font("small"))
        # particles
        for p in self.pmt_particles:
            c.create_oval(p["x"] - 2.5, p["y"] - 2.5, p["x"] + 2.5, p["y"] + 2.5,
                          fill="#67e8f9", outline="")
        c.create_text(w / 2, h * 0.76, text=self.t("topic.applications.pmt_note"),
                      fill=col["canvas_text"], font=self.font("small"))

    def _draw_solar(self):
        c = self.canvas
        c.delete("all")
        w, h = self.cwh()
        col = self.colors
        jx = w * 0.5
        # p and n regions
        c.create_rectangle(w * 0.2, h * 0.2, jx, h * 0.64, fill="#3b2f4a", outline="#64748b")
        c.create_rectangle(jx, h * 0.2, w * 0.8, h * 0.64, fill="#26384a", outline="#64748b")
        c.create_text(w * 0.35, h * 0.2 - 12, text=self.t("topic.applications.p_side"),
                      fill=col["canvas_text"], font=self.font("small"))
        c.create_text(w * 0.65, h * 0.2 - 12, text=self.t("topic.applications.n_side"),
                      fill=col["canvas_text"], font=self.font("small"))
        c.create_line(jx, h * 0.18, jx, h * 0.66, fill="#94a3b8", dash=(3, 3))

        # sunlight
        if self.intensity > 0:
            for i in range(5):
                x = w * 0.28 + i * w * 0.1
                c.create_line(x, h * 0.06, x - 14, h * 0.2, fill="#fde047", width=2, arrow="last")

        # carriers
        for cp in self.carriers:
            color = "#67e8f9" if cp["kind"] == "e" else "#fca5a5"
            c.create_oval(cp["x"] - 3, cp["y"] - 3, cp["x"] + 3, cp["y"] + 3,
                          fill=color, outline="")

        # external circuit with a lamp whose glow tracks the current
        by = h * 0.82
        c.create_line(w * 0.2, h * 0.64, w * 0.2, by, fill="#475569")
        c.create_line(w * 0.2, by, w * 0.8, by, fill="#475569")
        c.create_line(w * 0.8, h * 0.64, w * 0.8, by, fill="#475569")
        glow = int(40 + 180 * min(1.0, self.current / 100.0))
        lamp = f"#{glow:02x}{glow:02x}20"
        c.create_oval(w * 0.5 - 14, by - 14, w * 0.5 + 14, by + 14, fill=lamp, outline="#94a3b8")
        c.create_text(w * 0.5, by + 28, text=self.t("topic.applications.load"),
                      fill=col["canvas_text"], font=self.font("small"))
        c.create_text(w / 2, h * 0.12, text=self.t("topic.applications.solar_note"),
                      fill=col["canvas_text"], font=self.font("small"))
