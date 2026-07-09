"""Chapter 2, Section 1, Topic 2 - Features of blackbody radiation.

Brings together the classical laws:
  * Kirchhoff's law  - a cavity with a small hole is the ideal blackbody
                       (good absorber = good emitter).
  * Wien's displacement - the peak wavelength shifts as lambda_max = b / T.
  * Stefan-Boltzmann - the total radiated power per area grows as sigma T^4.

The main curve (normalised to its own peak) is shown with two ghost curves at
lower and higher temperature so the peak shift is obvious; the temperature's
true colour and its sigma T^4 power are reported alongside.
"""
from simulations.spectrum_base import SpectrumSim, XTICKS
import simulations.bb as bb


class BBFeaturesSim(SpectrumSim):
    title_key = "topic.bb_features.title"
    desc_key = "topic.bb_features.desc"

    def __init__(self, master, app):
        self.temp = 5000.0
        super().__init__(master, app)

    def build_controls(self, parent):
        self.t_var, _ = self.add_slider(
            parent, self.t("topic.bb_features.temperature"), 1000, 8000, self.temp,
            command=lambda v: setattr(self, "temp", v), fmt="{:.0f} K",
        )
        self.r_peak = self.add_readout(parent, self.t("topic.bb_features.wien"))
        self.r_power = self.add_readout(parent, self.t("topic.bb_features.power"))
        self.r_ratio = self.add_readout(parent, self.t("topic.bb_features.ratio"))

    def reset(self):
        self.temp = 5000.0
        self.t_var.set(self.temp)

    def draw(self):
        c = self.canvas
        c.delete("all")
        lams = self.lam_grid()
        xs = self.nm(lams)
        scale = self.planck_peak_value(self.temp) or 1.0
        p = self.make_plot(1.35)
        p.axes(self.t("topic.bb_features.xlabel"),
               self.t("topic.bb_features.ylabel"), XTICKS)

        # ghost curves (cooler / hotter), same normalisation
        for factor, color in ((0.65, "#475569"), (1.4, "#64748b")):
            tg = self.temp * factor
            p.curve(xs, [bb.planck_u(l, tg) / scale for l in lams], color, width=1)
            p.label(bb.wien_peak(tg) * 1e9, 1.28,
                    f"{tg:.0f} K", color, anchor="center")

        # main curve
        p.curve(xs, [bb.planck_u(l, self.temp) / scale for l in lams], "#38bdf8", width=2)
        peak_nm = bb.wien_peak(self.temp) * 1e9
        p.vline(peak_nm, "#fbbf24",
                label=self.t("topic.bb_features.peak_mark", nm=f"{peak_nm:.0f}"))

        self._draw_side(c)

        # readouts
        self.r_peak.set(f"{peak_nm:.0f} nm")
        power = bb.stefan_boltzmann(self.temp)
        self.r_power.set(f"{power:.3g} W/m²")
        self.r_ratio.set(self.t("topic.bb_features.ratio_val",
                                r=f"{(self.temp / 1000.0) ** 4:.1f}"))

    def _draw_side(self, c):
        w, h = self.cwh()
        # colour swatch for the current temperature
        col = bb.blackbody_rgb(self.temp)
        cx, cy = w - 150, 60
        c.create_oval(cx - 22, cy - 22, cx + 22, cy + 22, fill=col, outline="#94a3b8")
        c.create_text(cx, cy + 36, text=self.t("topic.bb_features.colour"),
                      fill=self.colors["canvas_text"], font=self.font("small"))

        # Kirchhoff cavity icon (a box with a small hole = ideal blackbody)
        bx, by = w - 90, 40
        c.create_rectangle(bx, by, bx + 46, by + 40, outline="#94a3b8")
        c.create_oval(bx + 18, by + 30, bx + 28, by + 40, fill="#000000", outline="#94a3b8")
        c.create_text(bx + 23, by + 52, text=self.t("topic.bb_features.cavity"),
                      fill=self.colors["canvas_text"], font=self.font("small"))
