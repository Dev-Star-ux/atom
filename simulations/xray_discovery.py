"""Chapter 2, Section 5, Topic 1 - Discovery of X-rays.

Wilhelm Röntgen (1895) noticed that a Crookes / cathode-ray tube caused a
nearby fluorescent screen to glow even when the tube was wrapped in black
paper. The unknown radiation passed through soft tissue but was stopped by
bone — the first medical X-ray image. Electrons accelerated by a high voltage
strike a metal target; the sudden deceleration (bremsstrahlung) and inner-shell
transitions produce X-rays.
"""
import math
import random

from simulations.base import Simulation
import simulations.xray as xr


class XrayDiscoverySim(Simulation):
    title_key = "topic.xray_discovery.title"
    desc_key = "topic.xray_discovery.desc"

    def __init__(self, master, app):
        self.voltage = 50.0    # kV
        self.intensity = 70.0
        self.electrons = []
        self.xrays = []
        self._emit = 0.0
        self._glow = 0.0
        super().__init__(master, app)

    def build_controls(self, parent):
        self.v_var, _ = self.add_slider(
            parent, self.t("topic.xray_discovery.voltage"), 20, 100, self.voltage,
            command=lambda v: setattr(self, "voltage", v), fmt="{:.0f} kV",
        )
        self.i_var, _ = self.add_slider(
            parent, self.t("topic.xray_discovery.intensity"), 0, 100, self.intensity,
            command=lambda v: setattr(self, "intensity", v), fmt="{:.0f}%",
        )
        self.r_lmin = self.add_readout(parent, self.t("topic.xray_discovery.lambda_min"))
        self.r_energy = self.add_readout(parent, self.t("topic.xray_discovery.max_energy"))
        self.r_pen = self.add_readout(parent, self.t("topic.xray_discovery.penetration"))

    def reset(self):
        self.voltage = 50.0
        self.intensity = 70.0
        self.v_var.set(self.voltage)
        self.i_var.set(self.intensity)
        self.electrons.clear()
        self.xrays.clear()
        self._emit = 0.0

    def tick(self, dt):
        if dt <= 0:
            return
        w, h = self.cwh()
        cath_x, anode_x = w * 0.18, w * 0.38
        self._glow = 0.85 + 0.15 * math.sin(self._emit * 5)

        if self.intensity > 0:
            self._emit += dt * self.intensity * 0.05
            while self._emit >= 1.0:
                self._emit -= 1.0
                y = random.uniform(h * 0.32, h * 0.52)
                self.electrons.append({"x": cath_x, "y": y, "hit": False})

        speed = 280.0 + self.voltage * 2.0
        for e in self.electrons:
            if not e["hit"]:
                e["x"] += speed * dt
                if e["x"] >= anode_x:
                    e["hit"] = True
                    for _ in range(2):
                        ang = random.uniform(-0.6, 0.6)
                        self.xrays.append({
                            "x": anode_x, "y": e["y"],
                            "vx": 200.0 * math.cos(ang),
                            "vy": 80.0 * math.sin(ang),
                            "life": 1.0,
                        })
        self.electrons = [e for e in self.electrons if not e["hit"]]
        for x in self.xrays:
            x["x"] += x["vx"] * dt
            x["y"] += x["vy"] * dt
            x["life"] -= dt * 0.35
        self.xrays = [x for x in self.xrays if x["life"] > 0]

    def render(self):
        c = self.canvas
        w, h = self.cwh()
        col = self.colors
        lam_min = xr.lambda_min_nm(self.voltage)
        E_max = self.voltage  # keV ≈ eV_max in kV for cutoff

        self.r_lmin.set(f"{lam_min:.3f} nm")
        self.r_energy.set(f"{E_max:.0f} keV")
        self.r_pen.set(self.t("topic.xray_discovery.pen_high" if self.voltage > 60
                               else "topic.xray_discovery.pen_med"))

        cath_x, anode_x = w * 0.18, w * 0.38
        screen_x = w * 0.82
        cy = h * 0.42

        # X-ray tube
        c.create_rectangle(cath_x - 20, cy - 50, anode_x + 30, cy + 50,
                           fill="#0f172a", outline="#475569", width=2)
        c.create_rectangle(cath_x - 16, cy - 8, cath_x - 4, cy + 8,
                           fill="#64748b", outline="#94a3b8")
        c.create_text(cath_x - 24, cy, text=self.t("topic.xray_discovery.cathode"),
                      fill=col["canvas_text"], font=self.font("tiny"), anchor="e")
        # angled anode (target)
        c.create_polygon(anode_x, cy - 30, anode_x + 18, cy - 10,
                         anode_x + 18, cy + 30, anode_x, cy + 20,
                         fill="#94a3b8", outline="#cbd5e1")
        c.create_text(anode_x + 28, cy, text=self.t("topic.xray_discovery.anode"),
                      fill=col["canvas_text"], font=self.font("tiny"), anchor="w")
        c.create_text((cath_x + anode_x) / 2, cy - 58,
                      text=self.t("topic.xray_discovery.tube", v=f"{self.voltage:.0f}"),
                      fill=col["accent2"], font=self.font("small"))

        # electrons
        for e in self.electrons:
            if not e["hit"]:
                c.create_oval(e["x"] - 3, e["y"] - 3, e["x"] + 3, e["y"] + 3,
                              fill=col["accent2"], outline="")

        # X-rays (greenish fan)
        for x in self.xrays:
            alpha = x["life"]
            c.create_line(x["x"], x["y"], x["x"] + 30, x["y"],
                            fill=f"#{int(80*alpha):02x}{int(220*alpha):02x}{int(180*alpha):02x}",
                            width=2)

        # hand + fluorescent screen
        sx0, sy0 = screen_x - 8, cy - 70
        glow = int(180 * self._glow * (self.intensity / 100))
        c.create_rectangle(sx0, sy0, screen_x + 8, cy + 70,
                           fill=f"#{glow:02x}{glow:02x}{int(glow*0.6):02x}", outline="#475569")
        c.create_text(screen_x, sy0 - 14, text=self.t("topic.xray_discovery.screen"),
                      fill=col["canvas_text"], font=self.font("small"))

        # simplified hand silhouette (bones opaque, flesh semi-transparent to X-rays)
        hx, hy = screen_x - 4, cy
        c.create_oval(hx - 28, hy - 55, hx + 28, hy + 55, outline="#334155", width=2)
        for bx, by, bw, bh in ((hx - 8, hy - 40, 6, 50), (hx + 4, hy - 38, 6, 48),
                                (hx - 22, hy - 20, 5, 30), (hx + 16, hy - 18, 5, 28)):
            c.create_rectangle(bx, by, bx + bw, by + bh, fill="#e2e8f0", outline="")
        c.create_text(hx, hy + 68, text=self.t("topic.xray_discovery.hand"),
                      fill=col["muted"], font=self.font("tiny"))

        c.create_text(w * 0.5, h - 22,
                      text=self.t("topic.xray_discovery.note"),
                      fill=col["muted"], font=self.font("small"))
