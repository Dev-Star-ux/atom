"""Chapter 2, Section 3, Topic 3 - Hydrogen atomic spectrum.

The Balmer, Lyman, and Paschen series follow the Rydberg formula

    1/λ = R_H (1/n₁² − 1/n₂²)   (n₂ > n₁)

Each bright line is a photon emitted when the electron drops from level n₂ to n₁.
The energy-level diagram and the spectrum strip are linked: pick a transition and
see its wavelength and photon energy.
"""
import tkinter as tk

from simulations.base import Simulation
from simulations.plot import Plot
import simulations.atom as atom

SERIES = (
    ("balmer", 2),
    ("lyman", 1),
    ("paschen", 3),
)


class HydrogenSpectrumSim(Simulation):
    title_key = "topic.hydrogen_spectrum.title"
    desc_key = "topic.hydrogen_spectrum.desc"

    def __init__(self, master, app):
        self.series = "balmer"
        self.n1 = 2
        self.n2 = 3
        self._pulse = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        from tkinter import ttk
        import tkinter as tk

        ttk.Label(parent, text=self.t("topic.hydrogen_spectrum.series"),
                  style="Panel.TLabel").pack(anchor="w", pady=(0, 2))
        self._ser_keys = [s[0] for s in SERIES]
        self.ser_var = tk.StringVar()
        combo = ttk.Combobox(
            parent, state="readonly", textvariable=self.ser_var,
            values=[self.t("series." + s) for s in self._ser_keys],
        )
        combo.current(0)
        combo.pack(fill="x")
        combo.bind("<<ComboboxSelected>>", self._on_series)

        self.n2_var, _ = self.add_slider(
            parent, self.t("topic.hydrogen_spectrum.upper_level"), 2, 7, self.n2,
            command=self._on_n2, fmt="n = {:.0f}",
        )
        self.r_lam = self.add_readout(parent, self.t("topic.hydrogen_spectrum.wavelength"))
        self.r_energy = self.add_readout(parent, self.t("topic.hydrogen_spectrum.photon"))
        self.r_transition = self.add_readout(parent, self.t("topic.hydrogen_spectrum.transition"))

    def _on_series(self, _e):
        labels = [self.t("series." + s) for s in self._ser_keys]
        self.series = self._ser_keys[labels.index(self.ser_var.get())]
        for key, n1 in SERIES:
            if key == self.series:
                self.n1 = n1
                break
        if self.n2 <= self.n1:
            self.n2 = self.n1 + 1
            self.n2_var.set(self.n2)

    def _on_n2(self, v):
        self.n2 = max(self.n1 + 1, int(round(v)))

    def reset(self):
        self.series = "balmer"
        self.n1 = 2
        self.n2 = 3
        self.ser_var.set(self.t("series.balmer"))
        self.n2_var.set(self.n2)
        self._pulse = 0.0

    def tick(self, dt):
        if dt > 0:
            self._pulse = min(1.0, self._pulse + dt * 1.5)
            if self._pulse >= 1.0:
                self._pulse = 0.0

    def _lam_nm(self):
        return atom.hydrogen_wavelength(self.n1, self.n2) * 1e9

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        lam = self._lam_nm()
        E_ph = atom.transition_energy_eV(self.n1, self.n2)

        self.r_lam.set(f"{lam:.1f} nm" if lam > 0 else "—")
        self.r_energy.set(f"{E_ph:.2f} eV" if E_ph > 0 else "—")
        self.r_transition.set(f"n₂={self.n2} → n₁={self.n1}")

        # --- energy level diagram --------------------------------------------
        levels_top, levels_bot = h * 0.06, h * 0.48
        lx0, lx1 = w * 0.08, w * 0.42
        n_show = 7
        level_y = {}
        for n in range(1, n_show + 1):
            frac = (n - 1) / (n_show - 1)
            y = levels_top + (levels_bot - levels_top) * frac
            level_y[n] = y
            lw = 3 if n in (self.n1, self.n2) else 1
            lc = col["accent"] if n in (self.n1, self.n2) else "#475569"
            c.create_line(lx0, y, lx1, y, fill=lc, width=lw)
            c.create_text(lx0 - 8, y, text=f"n={n}", anchor="e",
                          fill=col["canvas_text"], font=self.font("tiny"))
            c.create_text(lx1 + 10, y,
                          text=f"{atom.energy_level_eV(n):.2f} eV",
                          anchor="w", fill=col["muted"], font=self.font("tiny"))

        # transition arrow (animated photon)
        y2, y1 = level_y.get(self.n2, levels_top), level_y.get(self.n1, levels_bot)
        ax = (lx0 + lx1) / 2
        c.create_line(ax, y2, ax, y1, fill=col["accent2"], width=2, arrow=tk.LAST)
        if self._pulse < 0.85:
            py = y2 + (y1 - y2) * (self._pulse / 0.85)
            c.create_oval(ax - 5, py - 5, ax + 5, py + 5,
                          fill=atom.wavelength_to_rgb(lam), outline="")

        c.create_text((lx0 + lx1) / 2, levels_top - 14,
                      text=self.t("topic.hydrogen_spectrum.levels"),
                      fill=col["accent2"], font=self.font("small"))

        # Bohr nucleus
        c.create_oval(ax - 6, levels_bot + 20, ax + 6, levels_bot + 32,
                      fill=col["warn"], outline="")
        c.create_text(ax, levels_bot + 44, text="+",
                      fill=col["text"], font=self.font("tiny"))

        # --- spectrum strip --------------------------------------------------
        spec_top, spec_bot = h * 0.56, h * 0.78
        sx0, sx1 = w * 0.08, w * 0.94
        lam_min, lam_max = 90.0, 1100.0

        c.create_text((sx0 + sx1) / 2, spec_top - 14,
                      text=self.t("topic.hydrogen_spectrum.spectrum"),
                      fill=col["accent2"], font=self.font("small"))

        series_lines = atom.hydrogen_series(self.n1, 7)

        def x_of(nm):
            return sx0 + (sx1 - sx0) * (nm - lam_min) / (lam_max - lam_min)

        c.create_rectangle(sx0, spec_top, sx1, spec_bot, fill="#0f172a", outline="#334155")

        for nm, intensity, label in series_lines:
            px = x_of(nm)
            if px < sx0 or px > sx1:
                continue
            half = 2 + int(intensity * 4)
            highlight = abs(nm - lam) < 2
            c.create_rectangle(px - half, spec_top + 4, px + half, spec_bot - 4,
                               fill=atom.wavelength_to_rgb(nm), outline="")
            if highlight:
                c.create_rectangle(px - half - 2, spec_top + 2, px + half + 2, spec_bot - 2,
                                   outline=col["accent2"], width=2)
            c.create_text(px, spec_bot + 12, text=label,
                          fill=col["accent2"] if highlight else col["canvas_text"],
                          font=self.font("tiny"), anchor="n")

        # selected wavelength marker
        if lam_min <= lam <= lam_max:
            px = x_of(lam)
            c.create_line(px, spec_top - 4, px, spec_bot + 4, fill=col["good"], width=2)

        # --- Rydberg plot (series overview) --------------------------------
        plot_top = h * 0.82
        box = (60, plot_top, w - 28, h - 36)
        p = Plot(c, box, (lam_min, lam_max), (0, 1.15), col, self.font("small"))
        p.axes(self.t("topic.hydrogen_spectrum.xlabel"),
               self.t("topic.hydrogen_spectrum.ylabel"),
               (100, 400, 700, 1000))

        for nm, intensity, label in series_lines:
            if lam_min <= nm <= lam_max:
                p.vline(nm, atom.wavelength_to_rgb(nm))
                p.label(nm, intensity, label, col["canvas_text"], anchor="s")
