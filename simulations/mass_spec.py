"""Topic 3 - Mass analysis of matter (mass spectrometer).

Singly-charged ions are accelerated through a voltage U, then bent by a
magnetic field B. The radius of the circular path is

    r = (1 / B) * sqrt( 2 m U / q )

so heavier ions swing wider. Ions of an element's different isotopes land at
different positions on the detector, and their peak heights reproduce the
natural isotopic abundances - this is how relative atomic mass is measured.
"""
import math
import random

from simulations.base import Simulation

AMU = 1.66054e-27   # kg
E_CHARGE = 1.602e-19

# element -> list of (mass number, exact-ish mass in u, natural abundance %)
SAMPLES = {
    "neon": [(20, 19.99, 90.48), (21, 20.99, 0.27), (22, 21.99, 9.25)],
    "chlorine": [(35, 34.97, 75.77), (37, 36.97, 24.23)],
    "magnesium": [(24, 23.99, 78.99), (25, 24.99, 10.00), (26, 25.98, 11.01)],
    "carbon": [(12, 12.00, 98.93), (13, 13.00, 1.07)],
}


class MassSpecSim(Simulation):
    title_key = "topic.mass_spec.title"
    desc_key = "topic.mass_spec.desc"

    def __init__(self, master, app):
        self.sample = "neon"
        self.voltage = 1500.0     # accelerating voltage (V)
        self.bfield = 0.30        # magnetic flux density (T)
        self.ions = []            # travelling ions
        self.spectrum = {}        # mass number -> accumulated count
        self._emit_acc = 0.0
        super().__init__(master, app)

    # controls -------------------------------------------------------------
    def build_controls(self, parent):
        from tkinter import ttk
        import tkinter as tk

        ttk.Label(parent, text=self.t("topic.mass_spec.sample"), style="Panel.TLabel").pack(anchor="w")
        self.sample_var = tk.StringVar(value=self.sample)
        names = list(SAMPLES.keys())
        combo = ttk.Combobox(parent, state="readonly", textvariable=self.sample_var,
                             values=[self.t("element." + n) for n in names])
        combo.pack(fill="x", pady=(2, 4))
        self._sample_names = names
        combo.current(names.index(self.sample))
        combo.bind("<<ComboboxSelected>>", self._on_sample)

        self.u_var, _ = self.add_slider(
            parent, self.t("topic.mass_spec.voltage"), 500, 4000, self.voltage,
            command=lambda v: setattr(self, "voltage", v), fmt="{:.0f} V",
        )
        self.b_var, _ = self.add_slider(
            parent, self.t("topic.mass_spec.bfield"), 0.10, 0.80, self.bfield,
            command=lambda v: setattr(self, "bfield", v), fmt="{:.2f} T",
        )
        self.r_info = self.add_readout(parent, self.t("topic.mass_spec.detected"))

    def _on_sample(self, _evt):
        idx = self._sample_var_index()
        self.sample = self._sample_names[idx]
        self.reset()

    def _sample_var_index(self):
        try:
            return self._sample_names.index(self.sample_var.get())
        except ValueError:
            # combobox holds the translated label; map back by position
            labels = [self.t("element." + n) for n in self._sample_names]
            if self.sample_var.get() in labels:
                return labels.index(self.sample_var.get())
        return 0

    def reset(self):
        self.ions.clear()
        self.spectrum.clear()

    # geometry -------------------------------------------------------------
    def _geom(self):
        w = self.canvas.winfo_width() or 760
        h = self.canvas.winfo_height() or 460
        source = (w * 0.12, h * 0.80)   # ion source (bottom-left)
        return w, h, source

    def _radius_px(self, mass_u):
        """Path radius in pixels for a given isotope mass (u)."""
        m = mass_u * AMU
        r_m = math.sqrt(2.0 * m * self.voltage / E_CHARGE) / self.bfield
        return r_m * 4.0e4  # scale metres -> pixels

    # physics --------------------------------------------------------------
    def tick(self, dt):
        w, h, source = self._geom()
        if dt > 0:
            self._emit_acc += dt
            while self._emit_acc >= 0.05:
                self._emit_acc -= 0.05
                self._emit_ion()
            for ion in self.ions:
                ion["theta"] += ion["omega"] * dt
            self._collect(h)
        peaks = ", ".join(f"{mn}:{int(v)}" for mn, v in sorted(self.spectrum.items()))
        self.r_info.set(peaks or "-")

    def _emit_ion(self):
        isotopes = SAMPLES[self.sample]
        weights = [ab for _, _, ab in isotopes]
        mn, mass, _ab = random.choices(isotopes, weights=weights, k=1)[0]
        r = self._radius_px(mass)
        self.ions.append({"mn": mn, "mass": mass, "r": r, "theta": math.pi, "omega": 2.6})

    def _collect(self, h):
        alive = []
        for ion in self.ions:
            if ion["theta"] >= 2 * math.pi:  # completed the semicircle back to the baseline
                self.spectrum[ion["mn"]] = self.spectrum.get(ion["mn"], 0) + 1
            else:
                alive.append(ion)
        self.ions = alive

    # drawing --------------------------------------------------------------
    def render(self):
        c = self.canvas
        w, h, (sx, sy) = self._geom()
        col = self.colors

        # magnetic field region
        c.create_rectangle(sx - 10, h * 0.14, w - 30, sy + 10,
                           outline="#334155", dash=(3, 5))
        c.create_text(w - 70, h * 0.20, text="B ⊗", fill="#a78bfa", font=self.font("base"))

        # ion source and accelerator
        c.create_rectangle(sx - 40, sy - 14, sx, sy + 14, fill="#334155", outline="#64748b")
        c.create_text(sx - 20, sy + 30, text=self.t("topic.mass_spec.source"),
                      fill=col["canvas_text"], font=self.font("small"))

        # detector baseline (ions leave the source going up, curve right, land here)
        c.create_line(sx, sy, w - 30, sy, fill="#475569")
        c.create_text((sx + w) / 2, sy + 30, text=self.t("topic.mass_spec.detector"),
                      fill=col["canvas_text"], font=self.font("small"))

        # predicted landing marks + spectrum peaks per isotope
        isotopes = SAMPLES[self.sample]
        max_count = max(self.spectrum.values()) if self.spectrum else 1
        for mn, mass, ab in isotopes:
            r = self._radius_px(mass)
            land_x = sx + 2 * r
            if land_x < w - 30:
                c.create_line(land_x, sy - 6, land_x, sy + 6, fill="#64748b")
                c.create_text(land_x, sy + 16, text=str(mn), fill=col["canvas_text"],
                              font=self.font("small"))
                count = self.spectrum.get(mn, 0)
                if count:
                    bar_h = 90 * count / max_count
                    c.create_rectangle(land_x - 8, sy - bar_h, land_x + 8, sy,
                                       fill="#38bdf8", outline="")
                    c.create_text(land_x, sy - bar_h - 10, text=f"{ab:.1f}%",
                                  fill="#7dd3fc", font=self.font("small"))

        # travelling ions along their circular arcs
        for ion in self.ions:
            cx = sx + ion["r"]           # centre of the circular path
            cy = sy
            x = cx + ion["r"] * math.cos(ion["theta"])
            y = cy + ion["r"] * math.sin(ion["theta"])
            if y <= sy:
                c.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#fca5a5", outline="")
