"""Chapter 2, Section 3, Topic 1 - Features of atomic spectrum (prism spectroscope).

White light from a hot solid gives a *continuous* spectrum: every wavelength is
present. Light from a gas discharge or a low-pressure vapour lamp gives a
*line* spectrum: only discrete wavelengths characteristic of that element.
A prism (or grating) disperses the beam by wavelength so the two cases are easy
to tell apart on the viewing screen.
"""
import math

from simulations.base import Simulation
import simulations.atom as atom
import simulations.bb as bb

SOURCES = ("continuous", "hydrogen", "helium", "sodium")
PRISM_ANGLE = 0.42   # radians, deviation parameter


class PrismSpectroscopeSim(Simulation):
    title_key = "topic.prism_spectroscope.title"
    desc_key = "topic.prism_spectroscope.desc"

    def __init__(self, master, app):
        self.source = "hydrogen"
        self.temp = 5500.0
        self._beam_phase = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        from tkinter import ttk
        import tkinter as tk

        ttk.Label(parent, text=self.t("topic.prism_spectroscope.source"),
                  style="Panel.TLabel").pack(anchor="w", pady=(0, 2))
        self._src_keys = list(SOURCES)
        self.src_var = tk.StringVar()
        combo = ttk.Combobox(
            parent, state="readonly", textvariable=self.src_var,
            values=[self.t("source." + s) for s in self._src_keys],
        )
        combo.current(self._src_keys.index(self.source))
        combo.pack(fill="x")
        combo.bind("<<ComboboxSelected>>", self._on_source)

        self.t_var, _ = self.add_slider(
            parent, self.t("topic.prism_spectroscope.temperature"), 2000, 8000, self.temp,
            command=lambda v: setattr(self, "temp", v), fmt="{:.0f} K",
        )
        self.r_type = self.add_readout(parent, self.t("topic.prism_spectroscope.spectrum_type"))
        self.r_lines = self.add_readout(parent, self.t("topic.prism_spectroscope.line_count"))

    def _on_source(self, _e):
        labels = [self.t("source." + s) for s in self._src_keys]
        self.source = self._src_keys[labels.index(self.src_var.get())]

    def reset(self):
        self.source = "hydrogen"
        self.temp = 5500.0
        self.src_var.set(self.t("source.hydrogen"))
        self.t_var.set(self.temp)
        self._beam_phase = 0.0

    def tick(self, dt):
        if dt > 0:
            self._beam_phase = (self._beam_phase + dt * 2.5) % (2 * math.pi)

    def _lines_for_source(self):
        if self.source == "hydrogen":
            return atom.HYDROGEN_LINES
        if self.source == "helium":
            return atom.HELIUM_LINES
        if self.source == "sodium":
            return atom.SODIUM_LINES
        return []

    def _dispersion(self, nm):
        """Map wavelength (nm) to horizontal position on the spectrum strip (0..1)."""
        return max(0.0, min(1.0, (nm - 380) / (750 - 380)))

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        is_continuous = self.source == "continuous"

        self.r_type.set(
            self.t("topic.prism_spectroscope.continuous")
            if is_continuous else self.t("topic.prism_spectroscope.line")
        )
        lines = self._lines_for_source()
        self.r_lines.set(
            self.t("topic.prism_spectroscope.all_wavelengths")
            if is_continuous else str(len(lines))
        )

        # layout regions
        app_top, app_bot = h * 0.08, h * 0.52
        spec_top, spec_bot = h * 0.62, h * 0.92
        prism_cx, prism_cy = w * 0.52, (app_top + app_bot) / 2

        # --- apparatus -------------------------------------------------------
        src_x, src_y = w * 0.08, (app_top + app_bot) / 2
        slit_x = w * 0.22
        screen_x = w * 0.88

        # source glow
        src_col = bb.blackbody_rgb(self.temp) if is_continuous else "#4f8cff"
        c.create_oval(src_x - 18, src_y - 18, src_x + 18, src_y + 18,
                      fill=src_col, outline="#94a3b8")
        c.create_text(src_x, src_y + 30, text=self.t("topic.prism_spectroscope.lamp"),
                      fill=col["canvas_text"], font=self.font("small"))

        # collimator / slit
        c.create_rectangle(slit_x - 3, app_top + 8, slit_x + 3, app_bot - 8,
                           fill="#1e293b", outline="#64748b")
        c.create_line(src_x + 18, src_y, slit_x - 3, src_y, fill="#e2e8f0", width=2)
        c.create_text(slit_x, app_bot + 14, text=self.t("topic.prism_spectroscope.slit"),
                      fill=col["canvas_text"], font=self.font("small"))

        # prism (triangle)
        ps = 34
        pts = [prism_cx, prism_cy - ps, prism_cx - ps * 0.87, prism_cy + ps * 0.5,
               prism_cx + ps * 0.87, prism_cy + ps * 0.5]
        c.create_polygon(*pts, fill="#334155", outline="#94a3b8", width=2)
        c.create_text(prism_cx, app_bot + 14, text=self.t("topic.prism_spectroscope.prism"),
                      fill=col["accent2"], font=self.font("small"))

        # incoming white / coloured beam to prism
        c.create_line(slit_x + 3, src_y, prism_cx - ps * 0.5, prism_cy,
                      fill="#f8fafc" if is_continuous else "#7dd3fc", width=3)

        # dispersed rays (fan out by wavelength)
        if is_continuous:
            for nm in range(400, 721, 40):
                t = self._dispersion(nm)
                ang = -PRISM_ANGLE + t * 2 * PRISM_ANGLE
                ex = prism_cx + math.cos(ang) * (screen_x - prism_cx)
                ey = prism_cy + math.sin(ang) * (screen_x - prism_cx) * 0.35
                ray_col = atom.wavelength_to_rgb(nm)
                c.create_line(prism_cx, prism_cy, ex, ey, fill=ray_col, width=2)
        else:
            for nm, intensity, _ in lines:
                t = self._dispersion(nm)
                ang = -PRISM_ANGLE + t * 2 * PRISM_ANGLE
                ex = prism_cx + math.cos(ang) * (screen_x - prism_cx)
                ey = prism_cy + math.sin(ang) * (screen_x - prism_cx) * 0.35
                ray_col = atom.wavelength_to_rgb(nm)
                lw = 1 + int(intensity * 3)
                c.create_line(prism_cx, prism_cy, ex, ey, fill=ray_col, width=lw)

        c.create_text(screen_x, app_top - 6, text=self.t("topic.prism_spectroscope.screen"),
                      fill=col["canvas_text"], font=self.font("small"), anchor="center")

        # --- spectrum strip --------------------------------------------------
        sx0, sx1 = w * 0.1, w * 0.9
        c.create_rectangle(sx0, spec_top, sx1, spec_bot, fill="#0f172a", outline="#334155")
        c.create_text((sx0 + sx1) / 2, spec_top - 12,
                      text=self.t("topic.prism_spectroscope.spectrum_view"),
                      fill=col["accent2"], font=self.font("small"))

        if is_continuous:
            steps = 120
            for i in range(steps):
                nm = 380 + (750 - 380) * i / steps
                x0 = sx0 + (sx1 - sx0) * i / steps
                x1 = sx0 + (sx1 - sx0) * (i + 1) / steps
                c.create_rectangle(x0, spec_top + 4, x1, spec_bot - 4,
                                   fill=atom.wavelength_to_rgb(nm), outline="")
        else:
            for nm, intensity, label in lines:
                t = self._dispersion(nm)
                px = sx0 + (sx1 - sx0) * t
                half_w = 3 + int(intensity * 5)
                c.create_rectangle(px - half_w, spec_top + 6, px + half_w, spec_bot - 6,
                                   fill=atom.wavelength_to_rgb(nm), outline="")
                c.create_text(px, spec_bot + 14, text=label,
                              fill=col["canvas_text"], font=self.font("tiny"), anchor="n")

        # wavelength axis ticks
        for nm in (400, 500, 600, 700):
            tx = sx0 + (sx1 - sx0) * self._dispersion(nm)
            c.create_line(tx, spec_bot, tx, spec_bot + 5, fill="#475569")
            c.create_text(tx, spec_bot + 16, text=f"{nm}",
                          fill=col["canvas_text"], font=self.font("tiny"))

        c.create_text((sx0 + sx1) / 2, h - 8,
                      text=self.t("topic.prism_spectroscope.xlabel"),
                      fill=col["muted"], font=self.font("tiny"))
