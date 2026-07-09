"""Base class for every lecture simulation.

A simulation is a ttk.Frame with a standard layout:

    +--------------------------------------------------+
    | title                                            |
    | description                                      |
    +-----------------------------------+--------------+
    |                                   |  controls    |
    |            canvas                 |  (sliders,   |
    |                                   |   readouts)  |
    +-----------------------------------+--------------+

Subclasses set title_key / desc_key and implement:
    build_controls(parent)   -> create sliders / buttons / readouts
    reset()                  -> restore initial state
    tick(dt)                 -> advance physics by dt seconds (dt already 0 if paused)
    draw()                   -> redraw the canvas
"""
import time
import tkinter as tk
from tkinter import ttk


class Simulation(ttk.Frame):
    title_key = ""
    desc_key = ""

    def __init__(self, master, app):
        super().__init__(master, style="Content.TFrame")
        self.app = app
        self.colors = app.colors
        self._job = None
        self._running = False
        self._last = 0.0
        self.paused = False
        self.canvas = None
        self._build_layout()

    # translation / font helpers -------------------------------------------
    def t(self, key, **fmt):
        return self.app.i18n.t(key, **fmt)

    def font(self, name):
        return self.app.fonts[name]

    # layout ---------------------------------------------------------------
    def _build_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, style="Content.TFrame")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 6))
        ttk.Label(header, text=self.t(self.title_key), style="Heading.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text=self.t(self.desc_key),
            style="Muted.TLabel",
            wraplength=900,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        body = ttk.Frame(self, style="Content.TFrame")
        body.grid(row=1, column=0, sticky="nsew", padx=18, pady=(4, 14))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            body,
            background=self.colors["canvas"],
            highlightthickness=0,
            width=760,
            height=460,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        side = ttk.Frame(body, style="Panel.TFrame", width=300)
        side.grid(row=0, column=1, sticky="ns", padx=(14, 0))
        side.grid_propagate(False)
        self.controls = side

        self._build_control_container()
        self.canvas.bind("<Configure>", self._on_resize)

    def _build_control_container(self):
        inner = ttk.Frame(self.controls, style="Panel.TFrame")
        inner.pack(fill="both", expand=True, padx=14, pady=14)
        ttk.Label(inner, text=self.t("common.controls"), style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Separator(inner).pack(fill="x", pady=(6, 10))
        self.build_controls(inner)

        ttk.Separator(inner).pack(fill="x", pady=10)
        btns = ttk.Frame(inner, style="Panel.TFrame")
        btns.pack(fill="x")
        self._pause_btn = ttk.Button(btns, text=self.t("common.pause"), command=self.toggle_pause)
        self._pause_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(btns, text=self.t("common.reset"), command=self.reset).pack(
            side="left", expand=True, fill="x", padx=(4, 0)
        )

    def _on_resize(self, event):
        self.draw()

    # animation lifecycle --------------------------------------------------
    def on_show(self):
        self._running = True
        self._last = time.perf_counter()
        self._loop()

    def on_hide(self):
        self._running = False
        if self._job is not None:
            try:
                self.after_cancel(self._job)
            except tk.TclError:
                pass
            self._job = None

    def _loop(self):
        if not self._running:
            return
        now = time.perf_counter()
        dt = now - self._last
        self._last = now
        if dt > 0.05:
            dt = 0.05
        try:
            self.tick(0.0 if self.paused else dt)
            self.draw()
        except tk.TclError:
            return  # widget destroyed mid-frame
        self._job = self.after(33, self._loop)

    def toggle_pause(self):
        self.paused = not self.paused
        self._pause_btn.configure(
            text=self.t("common.play") if self.paused else self.t("common.pause")
        )

    # helpers for subclasses ----------------------------------------------
    def add_slider(self, parent, label_text, from_, to, value, command=None, fmt="{:.0f}"):
        """Add a labelled slider that shows its live value. Returns (var, value_label)."""
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.pack(fill="x", pady=(8, 0))
        top = ttk.Frame(row, style="Panel.TFrame")
        top.pack(fill="x")
        ttk.Label(top, text=label_text, style="Panel.TLabel").pack(side="left")
        val_lbl = ttk.Label(top, text=fmt.format(value), style="Value.TLabel")
        val_lbl.pack(side="right")
        var = tk.DoubleVar(value=value)

        def _on_change(_v):
            val_lbl.configure(text=fmt.format(var.get()))
            if command:
                command(var.get())

        scale = ttk.Scale(row, from_=from_, to=to, variable=var, command=_on_change)
        scale.pack(fill="x", pady=(2, 0))
        return var, val_lbl

    def add_readout(self, parent, label_text):
        """Add a label + dynamic value. Returns a tk.StringVar to update."""
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.pack(fill="x", pady=(6, 0))
        ttk.Label(row, text=label_text, style="Panel.TLabel").pack(side="left")
        var = tk.StringVar(value="-")
        ttk.Label(row, textvariable=var, style="Readout.TLabel").pack(side="right")
        return var

    # subclass hooks -------------------------------------------------------
    def build_controls(self, parent):
        raise NotImplementedError

    def reset(self):
        pass

    def tick(self, dt):
        pass

    def draw(self):
        pass
