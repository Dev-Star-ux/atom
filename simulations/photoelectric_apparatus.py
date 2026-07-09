"""Chapter 2, Section 2, Topic 1 - Experimental principle of the photoelectric effect.

Monochromatic light strikes a metal cathode inside an evacuated tube. If it
ejects electrons, they cross to the anode and register as a photocurrent. A
variable voltage between the plates can accelerate the electrons or retard
them; the reverse voltage that just stops the current (the stopping potential
V_s) measures the maximum kinetic energy of the electrons: e V_s = KE_max.
"""
import math
import random

from simulations.base import Simulation
import simulations.photo as photo

WORK = photo.MATERIALS["sodium"]   # cathode material for this apparatus
SP = 210.0                          # px-speed per sqrt(eV)


class PhotoApparatusSim(Simulation):
    title_key = "topic.pe_apparatus.title"
    desc_key = "topic.pe_apparatus.desc"

    def __init__(self, master, app):
        self.freq = 7.0        # x1e14 Hz
        self.intensity = 60.0  # 0..100
        self.voltage = 1.0     # collector voltage (V); negative = retarding
        self.electrons = []
        self._emit_acc = 0.0
        self.current = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        self.f_var, _ = self.add_slider(
            parent, self.t("topic.pe_apparatus.frequency"), 3, 15, self.freq,
            command=lambda v: setattr(self, "freq", v), fmt="{:.1f}",
        )
        self.i_var, _ = self.add_slider(
            parent, self.t("topic.pe_apparatus.intensity"), 0, 100, self.intensity,
            command=lambda v: setattr(self, "intensity", v), fmt="{:.0f}%",
        )
        self.v_var, _ = self.add_slider(
            parent, self.t("topic.pe_apparatus.voltage"), -3, 5, self.voltage,
            command=lambda v: setattr(self, "voltage", v), fmt="{:+.1f} V",
        )
        self.r_energy = self.add_readout(parent, self.t("topic.pe_apparatus.photon_energy"))
        self.r_ke = self.add_readout(parent, self.t("topic.pe_apparatus.ke_max"))
        self.r_stop = self.add_readout(parent, self.t("topic.pe_apparatus.stopping"))
        self.r_current = self.add_readout(parent, self.t("topic.pe_apparatus.current"))

    def reset(self):
        self.freq = 7.0
        self.intensity = 60.0
        self.voltage = 1.0
        self.f_var.set(self.freq)
        self.i_var.set(self.intensity)
        self.v_var.set(self.voltage)
        self.electrons.clear()
        self.current = 0.0

    # geometry -------------------------------------------------------------
    def _geom(self):
        w, h = self.cwh()
        cy = h * 0.42
        cathode_x = w * 0.30
        anode_x = w * 0.66
        return w, h, cy, cathode_x, anode_x

    def _ke_max(self):
        return photo.photon_energy_eV(self.freq) - WORK  # eV; may be negative

    # physics --------------------------------------------------------------
    def tick(self, dt):
        w, h, cy, cx, ax = self._geom()
        gap = ax - cx
        ke_max = self._ke_max()
        above = ke_max > 0

        if dt > 0:
            # emission rate proportional to intensity, when above threshold
            if above and self.intensity > 0:
                self._emit_acc += dt * self.intensity * 0.06
                while self._emit_acc >= 1.0:
                    self._emit_acc -= 1.0
                    ke = random.uniform(0.05, ke_max)
                    self.electrons.append({"x": 0.0, "ke": ke, "dir": 1,
                                           "y": cy + random.uniform(-24, 24)})
            for e in self.electrons:
                s = e["x"] / gap
                ke_local = e["ke"] + self.voltage * s   # eV at fraction s
                if ke_local <= 0:
                    e["dir"] = -1
                    ke_local = 0.02
                speed = SP * math.sqrt(ke_local)
                e["x"] += e["dir"] * speed * dt
            # collect / remove
            kept = []
            for e in self.electrons:
                if e["x"] >= gap:
                    continue  # collected
                if e["x"] <= 0 and e["dir"] < 0:
                    continue  # returned to cathode
                kept.append(e)
            self.electrons = kept

        # steady-state photocurrent (stable readout, independent of animation)
        if above and self.intensity > 0:
            if self.voltage >= 0:
                frac = 1.0
            elif -self.voltage < ke_max:
                frac = (ke_max + self.voltage) / ke_max
            else:
                frac = 0.0
            target = self.intensity * frac
        else:
            target = 0.0
        self.current += (target - self.current) * min(1.0, dt * 6)
        self._update_readouts(ke_max, above)

    def _update_readouts(self, ke_max, above):
        self.r_energy.set(f"{photo.photon_energy_eV(self.freq):.2f} eV")
        if above:
            self.r_ke.set(f"{ke_max:.2f} eV")
            self.r_stop.set(f"{ke_max:.2f} V")
        else:
            self.r_ke.set(self.t("topic.pe_apparatus.no_emit"))
            self.r_stop.set("-")
        self.r_current.set(f"{self.current * 0.1:.2f} µA")

    # drawing --------------------------------------------------------------
    def draw(self):
        c = self.canvas
        c.delete("all")
        w, h, cy, cx, ax = self._geom()
        gap = ax - cx
        col = self.colors
        color = photo.photon_color(self.freq)

        # evacuated tube
        c.create_rectangle(cx - 30, cy - 90, ax + 30, cy + 90, outline="#334155")

        # light beam onto the cathode
        if self.intensity > 0:
            for i in range(3):
                yy = cy - 16 + i * 16
                c.create_line(20, yy, cx - 30, yy, fill=color, width=2, arrow="last")
        c.create_text(70, cy - 40, text=self.t("topic.pe_apparatus.light"),
                      fill=col["canvas_text"], font=self.font("small"))

        # cathode (emitter) and anode (collector)
        c.create_rectangle(cx - 8, cy - 80, cx, cy + 80, fill="#64748b", outline="")
        c.create_rectangle(ax, cy - 80, ax + 8, cy + 80, fill="#64748b", outline="")
        c.create_text(cx - 4, cy + 96, text=self.t("topic.pe_apparatus.cathode"),
                      fill=col["canvas_text"], font=self.font("small"))
        c.create_text(ax + 4, cy + 96, text=self.t("topic.pe_apparatus.anode"),
                      fill=col["canvas_text"], font=self.font("small"))

        # electrons
        for e in self.electrons:
            x = cx + e["x"]
            c.create_oval(x - 3, e["y"] - 3, x + 3, e["y"] + 3, fill="#67e8f9", outline="")

        # external circuit with battery + ammeter
        by = cy + 150
        c.create_line(cx - 4, cy + 80, cx - 4, by, fill="#475569")
        c.create_line(cx - 4, by, ax + 4, by, fill="#475569")
        c.create_line(ax + 4, cy + 80, ax + 4, by, fill="#475569")
        mid = (cx + ax) / 2
        c.create_oval(mid - 16, by - 16, mid + 16, by + 16, outline="#94a3b8")
        c.create_text(mid, by, text="A", fill="#e2e8f0", font=self.font("base"))
        c.create_text(mid, by + 30, text=self.t("topic.pe_apparatus.ammeter"),
                      fill=col["canvas_text"], font=self.font("small"))
        # voltage polarity hint
        pol = self.t("topic.pe_apparatus.accel") if self.voltage >= 0 else self.t("topic.pe_apparatus.retard")
        c.create_text(mid, by - 34, text=f"V = {self.voltage:+.1f} V  ({pol})",
                      fill="#e2e8f0", font=self.font("small"))

        if self._ke_max() <= 0:
            c.create_text((cx + ax) / 2, cy - 108,
                          text=self.t("topic.pe_apparatus.below"),
                          fill="#f87171", font=self.font("small"))
