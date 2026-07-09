"""Chapter 2, Section 4, Topic 3 - Hydrogen atom: electron orbit & spectrum series.

The hydrogen atom in Bohr's model: the electron moves on quantised circular
orbits (r_n = n² a₀). Each allowed orbit has a definite energy. When the
electron drops from a higher orbit n₂ to a lower orbit n₁ it emits a photon,
producing one line of the hydrogen spectrum. Balmer, Lyman, and Paschen series
are the sets of lines with a common lower level n₁.

This view shows orbital motion on the left and the matching spectrum series on
the right, linked by the selected transition n₂ → n₁.
"""
import math
import tkinter as tk

from simulations.base import Simulation
from simulations.plot import Plot
import simulations.atom as atom

SERIES = (
    ("balmer", 2),
    ("lyman", 1),
    ("paschen", 3),
)

N_MAX = 7
LAM_MIN, LAM_MAX = 90.0, 1100.0


class BohrHydrogenSim(Simulation):
    title_key = "topic.bohr_hydrogen.title"
    desc_key = "topic.bohr_hydrogen.desc"

    def __init__(self, master, app):
        self.series = "balmer"
        self.n1 = 2
        self.n2 = 3
        self.angle = 0.0
        self._pulse = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        from tkinter import ttk

        ttk.Label(parent, text=self.t("topic.bohr_hydrogen.series"),
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
            parent, self.t("topic.bohr_hydrogen.orbit_n"), 2, N_MAX, self.n2,
            command=self._on_n2, fmt="n = {:.0f}",
        )
        self.r_radius = self.add_readout(parent, self.t("topic.bohr_hydrogen.radius"))
        self.r_speed = self.add_readout(parent, self.t("topic.bohr_hydrogen.speed"))
        self.r_lam = self.add_readout(parent, self.t("topic.bohr_hydrogen.wavelength"))
        self.r_photon = self.add_readout(parent, self.t("topic.bohr_hydrogen.photon"))
        self.r_transition = self.add_readout(parent, self.t("topic.bohr_hydrogen.transition"))

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
        self.n2 = max(self.n1 + 1, min(N_MAX, int(round(v))))

    def reset(self):
        self.series = "balmer"
        self.n1 = 2
        self.n2 = 3
        self.angle = 0.0
        self._pulse = 0.0
        self.ser_var.set(self.t("series.balmer"))
        self.n2_var.set(self.n2)

    def tick(self, dt):
        if dt <= 0:
            return
        self.angle += atom.orbit_angular_speed(self.n2) * dt
        self._pulse = (self._pulse + dt * 1.2) % 2.5

    def _geom(self):
        w, h = self.cwh()
        cx, cy = w * 0.26, h * 0.40
        scale = min(w, h) / 500.0 * 14.0
        return w, h, cx, cy, scale

    def _level_y(self, n, top, bot):
        """Map quantum number to vertical position (n=1 at bottom)."""
        return bot - (bot - top) * (n - 1) / (N_MAX - 1)

    def render(self):
        c = self.canvas
        w, h, cx, cy, scale = self._geom()
        col = self.colors
        lam = atom.hydrogen_wavelength(self.n1, self.n2) * 1e9
        E_ph = atom.transition_energy_eV(self.n1, self.n2)
        rn = atom.bohr_radius(self.n2)
        v = atom.bohr_orbital_speed(self.n2)

        self.r_radius.set(f"r_{self.n2} = {rn * 1e11:.2f} ×10⁻¹¹ m")
        self.r_speed.set(f"v = {v / 1e6:.2f} ×10⁶ m/s")
        self.r_lam.set(f"{lam:.1f} nm" if lam > 0 else "—")
        self.r_photon.set(f"ΔE = {E_ph:.2f} eV" if E_ph > 0 else "—")
        self.r_transition.set(f"n₂={self.n2} → n₁={self.n1}")

        self._draw_orbits(c, cx, cy, scale, col)
        self._draw_levels(c, w, h, col)
        self._draw_spectrum(c, w, h, col, lam)
        self._draw_formula(c, w, h, col)

    def _draw_orbits(self, c, cx, cy, scale, col):
        """Bohr orbits with electron moving on the selected level n₂."""
        # all allowed orbits
        for n in range(1, N_MAX + 1):
            r = atom.orbit_radius_px(n, scale)
            active = n == self.n2
            c.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                outline=col["accent"] if active else "#1e293b",
                width=2 if active else 1,
                dash=() if active else (4, 6),
            )
            if n <= 4:
                c.create_text(cx + r + 6, cy, text=f"n={n}",
                              fill=col["accent2"] if active else col["muted"],
                              font=self.font("tiny"), anchor="w")

        r = atom.orbit_radius_px(self.n2, scale)
        ex = cx + r * math.cos(self.angle)
        ey = cy + r * math.sin(self.angle)

        # motion trail
        trail = []
        for i in range(12):
            a = self.angle - i * 0.22
            trail.append(cx + r * math.cos(a))
            trail.append(cy + r * math.sin(a))
        if len(trail) >= 4:
            c.create_line(*trail, fill="#2a6f8f", width=2)

        # velocity direction (tangent)
        tx = -math.sin(self.angle)
        ty = math.cos(self.angle)
        c.create_line(ex, ey, ex + tx * 22, ey + ty * 22,
                      fill=col["accent2"], arrow=tk.LAST, width=2)

        c.create_oval(ex - 8, ey - 8, ex + 8, ey + 8, fill="#38bdf8", outline="#7dd3fc")
        c.create_text(ex, ey, text="e⁻", fill="#0b1220", font=self.font("tiny"))

        # nucleus
        c.create_oval(cx - 10, cy - 10, cx + 10, cy + 10, fill="#ef4444", outline="#fecaca")
        c.create_text(cx, cy, text="p⁺", fill="#fff", font=self.font("tiny"))

        c.create_text(cx, cy + scale * N_MAX * N_MAX + 24,
                      text=self.t("topic.bohr_hydrogen.orbit_label"),
                      fill=col["accent2"], font=self.font("small"))

        # transition arrow toward inner orbit n₁
        r1 = atom.orbit_radius_px(self.n1, scale)
        ax = cx - r * 0.35
        c.create_line(ax, cy - r1, ax, cy - r,
                      fill=col["good"], width=2, arrow=tk.FIRST)
        if self._pulse < 0.4:
            py = cy - r1 + (r - r1) * (self._pulse / 0.4)
            pc = atom.wavelength_to_rgb(atom.hydrogen_wavelength(self.n1, self.n2) * 1e9)
            c.create_oval(ax - 6, py - 6, ax + 6, py + 6, fill=pc, outline=col["good"])

    def _draw_levels(self, c, w, h, col):
        """Energy-level diagram linked to the selected transition."""
        lx0, lx1 = w * 0.50, w * 0.66
        top, bot = h * 0.10, h * 0.48
        level_y = {}

        c.create_text((lx0 + lx1) / 2, top - 14,
                      text=self.t("topic.bohr_hydrogen.levels"),
                      fill=col["accent2"], font=self.font("small"))

        for n in range(1, N_MAX + 1):
            y = self._level_y(n, top, bot)
            level_y[n] = y
            hl = n in (self.n1, self.n2)
            c.create_line(lx0, y, lx1, y,
                          fill=col["accent"] if hl else "#475569",
                          width=2 if hl else 1)
            c.create_text(lx0 - 8, y, text=f"n={n}", anchor="e",
                          fill=col["canvas_text"], font=self.font("tiny"))
            c.create_text(lx1 + 8, y,
                          text=f"{atom.energy_level_eV(n):.2f} eV",
                          anchor="w", fill=col["muted"], font=self.font("tiny"))

        ax = (lx0 + lx1) / 2
        y2, y1 = level_y[self.n2], level_y[self.n1]
        c.create_line(ax, y2, ax, y1, fill=col["accent2"], width=2, arrow=tk.LAST)
        c.create_text(ax + 14, (y1 + y2) / 2,
                      text=self.t("topic.bohr_hydrogen.photon_emit"),
                      fill=col["good"], font=self.font("tiny"), anchor="w")

    def _draw_spectrum(self, c, w, h, col, lam):
        """Full hydrogen spectral series with the active line highlighted."""
        spec_top, spec_bot = h * 0.56, h * 0.76
        sx0, sx1 = w * 0.08, w * 0.94
        series_lines = atom.hydrogen_series(self.n1, N_MAX)

        def x_of(nm):
            return sx0 + (sx1 - sx0) * (nm - LAM_MIN) / (LAM_MAX - LAM_MIN)

        c.create_text((sx0 + sx1) / 2, spec_top - 14,
                      text=self.t("topic.bohr_hydrogen.spectrum", series=self.t("series." + self.series)),
                      fill=col["accent2"], font=self.font("small"))
        c.create_rectangle(sx0, spec_top, sx1, spec_bot, fill="#0f172a", outline="#334155")

        for nm, intensity, label in series_lines:
            if not (LAM_MIN <= nm <= LAM_MAX):
                continue
            px = x_of(nm)
            half = 2 + int(intensity * 5)
            highlight = abs(nm - lam) < 1.5
            c.create_rectangle(px - half, spec_top + 4, px + half, spec_bot - 4,
                               fill=atom.wavelength_to_rgb(nm), outline="")
            if highlight:
                c.create_rectangle(px - half - 2, spec_top + 2, px + half + 2, spec_bot - 2,
                                   outline=col["accent2"], width=2)
            c.create_text(px, spec_bot + 12, text=label,
                          fill=col["accent2"] if highlight else col["canvas_text"],
                          font=self.font("tiny"), anchor="n")

        if LAM_MIN <= lam <= LAM_MAX:
            px = x_of(lam)
            c.create_line(px, spec_top - 4, px, spec_bot + 4, fill=col["good"], width=2)

        # wavelength axis
        plot_top = h * 0.82
        box = (60, plot_top, w - 28, h - 36)
        p = Plot(c, box, (LAM_MIN, LAM_MAX), (0, 1.1), col, self.font("small"))
        p.axes(self.t("topic.bohr_hydrogen.xlabel"),
               self.t("topic.bohr_hydrogen.ylabel"),
               (100, 400, 700, 1000))
        for nm, intensity, label in series_lines:
            if LAM_MIN <= nm <= LAM_MAX:
                p.vline(nm, atom.wavelength_to_rgb(nm))
                if abs(nm - lam) < 1.5:
                    p.label(nm, intensity, label, col["accent2"], anchor="s")

    def _draw_formula(self, c, w, h, col):
        c.create_text(w * 0.5, h * 0.52,
                      text=self.t("topic.bohr_hydrogen.formula"),
                      fill=col["muted"], font=self.font("small"))
