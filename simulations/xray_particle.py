"""Chapter 2, Section 5, Topic 3 - Particle property of X-rays.

Although X-rays are electromagnetic waves, they also arrive in discrete energy
packets (photons) of energy E = hν = hc/λ. At keV energies a single photon can
ionise an atom or knock out a photoelectron — behaviour that is naturally
described particle-by-particle, as in the photoelectric effect extended to
hard X-rays.
"""
import math
import random

from simulations.base import Simulation
import simulations.xray as xr

# Binding energies for inner-shell ionisation (keV) — simplified
SHELLS = {
    "k_shell": 1.0,
    "l_shell": 0.15,
    "outer": 0.01,
}


class XrayParticleSim(Simulation):
    title_key = "topic.xray_particle.title"
    desc_key = "topic.xray_particle.desc"

    def __init__(self, master, app):
        self.energy = 30.0   # keV
        self.intensity = 60.0
        self.shell = "k_shell"
        self.photons = []
        self.electrons = []
        self._emit = 0.0
        self._ionised = 0
        super().__init__(master, app)

    def build_controls(self, parent):
        from tkinter import ttk
        import tkinter as tk

        self.e_var, _ = self.add_slider(
            parent, self.t("topic.xray_particle.energy"), 5, 100, self.energy,
            command=lambda v: setattr(self, "energy", v), fmt="{:.0f} keV",
        )
        self.i_var, _ = self.add_slider(
            parent, self.t("topic.xray_particle.intensity"), 0, 100, self.intensity,
            command=lambda v: setattr(self, "intensity", v), fmt="{:.0f}%",
        )
        ttk.Label(parent, text=self.t("topic.xray_particle.shell"),
                  style="Panel.TLabel").pack(anchor="w", pady=(8, 0))
        self._shell_keys = list(SHELLS.keys())
        self.shell_var = tk.StringVar()
        combo = ttk.Combobox(
            parent, state="readonly", textvariable=self.shell_var,
            values=[self.t("shell." + s) for s in self._shell_keys],
        )
        combo.current(0)
        combo.pack(fill="x")
        combo.bind("<<ComboboxSelected>>", self._on_shell)

        self.r_lam = self.add_readout(parent, self.t("topic.xray_particle.wavelength"))
        self.r_binding = self.add_readout(parent, self.t("topic.xray_particle.binding"))
        self.r_ke = self.add_readout(parent, self.t("topic.xray_particle.photoelectron"))
        self.r_count = self.add_readout(parent, self.t("topic.xray_particle.ionised"))

    def _on_shell(self, _e):
        labels = [self.t("shell." + s) for s in self._shell_keys]
        self.shell = self._shell_keys[labels.index(self.shell_var.get())]

    def _binding(self):
        return SHELLS[self.shell]

    def reset(self):
        self.energy = 30.0
        self.intensity = 60.0
        self.shell = "k_shell"
        self.e_var.set(self.energy)
        self.i_var.set(self.intensity)
        self.shell_var.set(self.t("shell.k_shell"))
        self.photons.clear()
        self.electrons.clear()
        self._ionised = 0

    def tick(self, dt):
        if dt <= 0:
            return
        w, h = self.cwh()
        atom_x = w * 0.55

        bind = self._binding()
        ke = self.energy - bind

        if self.intensity > 0:
            self._emit += dt * self.intensity * 0.04
            while self._emit >= 1.0:
                self._emit -= 1.0
                y = random.uniform(h * 0.28, h * 0.58)
                self.photons.append({"x": 30.0, "y": y, "hit": False})

        for p in self.photons:
            if not p["hit"]:
                p["x"] += 320.0 * dt
                if p["x"] >= atom_x:
                    p["hit"] = True
                    if ke > 0:
                        self._ionised += 1
                        ang = random.uniform(-1.2, 1.2)
                        speed = 80.0 + 40.0 * math.sqrt(ke)
                        self.electrons.append({
                            "x": atom_x, "y": p["y"],
                            "vx": speed * math.cos(ang),
                            "vy": speed * math.sin(ang),
                        })
        self.photons = [p for p in self.photons if not p["hit"]]
        for e in self.electrons:
            e["x"] += e["vx"] * dt
            e["y"] += e["vy"] * dt
        self.electrons = [e for e in self.electrons
                          if -20 < e["x"] < w + 20 and -20 < e["y"] < h + 20]

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        lam = xr.lambda_pm_from_energy_keV(self.energy)
        bind = self._binding()
        ke = max(0.0, self.energy - bind)

        self.r_lam.set(f"{lam:.1f} pm")
        self.r_binding.set(f"{bind:.2f} keV")
        self.r_ke.set(f"{ke:.2f} keV" if ke > 0 else self.t("topic.xray_particle.no_eject"))
        self.r_count.set(str(self._ionised))

        atom_x = w * 0.55
        cy = h * 0.43

        # atom (nucleus + shells)
        c.create_oval(atom_x - 40, cy - 40, atom_x + 40, cy + 40, outline="#334155")
        c.create_oval(atom_x - 24, cy - 24, atom_x + 24, cy + 24, outline="#475569", dash=(3, 3))
        c.create_oval(atom_x - 8, cy - 8, atom_x + 8, cy + 8, fill="#ef4444", outline="")
        c.create_text(atom_x, cy, text="+", fill="#fff", font=self.font("tiny"))
        c.create_text(atom_x, cy + 54, text=self.t("topic.xray_particle.atom"),
                      fill=col["canvas_text"], font=self.font("small"))

        # X-ray photons (particles — drawn as bold packets)
        for p in self.photons:
            if not p["hit"]:
                c.create_oval(p["x"] - 6, p["y"] - 6, p["x"] + 6, p["y"] + 6,
                                fill="#22d3ee", outline="#67e8f9", width=2)
                c.create_line(p["x"] - 14, p["y"], p["x"] + 14, p["y"],
                              fill="#38bdf8", width=2)

        # photoelectrons
        for e in self.electrons:
            c.create_oval(e["x"] - 4, e["y"] - 4, e["x"] + 4, e["y"] + 4,
                          fill="#f472b6", outline="")

        # energy balance
        bx, by = w * 0.08, h * 0.72
        c.create_text(bx, by, text=self.t("topic.xray_particle.balance"),
                      fill=col["accent2"], font=self.font("small"), anchor="w")
        c.create_text(bx, by + 22,
                      text=self.t("topic.xray_particle.equation",
                                  E=f"{self.energy:.0f}", W=f"{bind:.2f}", ke=f"{ke:.2f}"),
                      fill=col["canvas_text"], font=self.font("small"), anchor="w")

        if ke <= 0:
            c.create_text(atom_x + 60, cy, text=self.t("topic.xray_particle.below"),
                          fill=col["bad"], font=self.font("small"))

        c.create_text(w * 0.5, h - 18,
                      text=self.t("topic.xray_particle.note"),
                      fill=col["muted"], font=self.font("tiny"))
