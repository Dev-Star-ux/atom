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
        header.grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 8))
        titlerow = ttk.Frame(header, style="Content.TFrame")
        titlerow.pack(fill="x")
        # accent bar to the left of the title
        tk.Frame(titlerow, width=4, background=self.colors["accent"]).pack(
            side="left", fill="y", padx=(0, 12))
        tcol = ttk.Frame(titlerow, style="Content.TFrame")
        tcol.pack(side="left", fill="x", expand=True)
        ttk.Label(tcol, text=self.t(self.title_key), style="Heading.TLabel").pack(anchor="w")
        ttk.Label(tcol, text=self.t(self.desc_key), style="Muted.TLabel",
                  wraplength=880, justify="left").pack(anchor="w", pady=(4, 0))

        body = ttk.Frame(self, style="Content.TFrame")
        body.grid(row=1, column=0, sticky="nsew", padx=22, pady=(6, 18))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        # canvas wrapped in a bordered frame for a framed-panel look
        canvas_wrap = tk.Frame(body, background=self.colors["border"])
        canvas_wrap.grid(row=0, column=0, sticky="nsew")
        self.canvas = tk.Canvas(
            canvas_wrap,
            background=self.colors["canvas"],
            highlightthickness=0,
            width=760,
            height=460,
        )
        self.canvas.pack(fill="both", expand=True, padx=1, pady=1)

        side = ttk.Frame(body, style="Panel.TFrame", width=304)
        side.grid(row=0, column=1, sticky="ns", padx=(16, 0))
        side.grid_propagate(False)
        self.controls = side

        self._build_control_container()
        self.canvas.bind("<Configure>", self._on_resize)

    def _build_control_container(self):
        inner = ttk.Frame(self.controls, style="Panel.TFrame")
        inner.pack(fill="both", expand=True, padx=16, pady=16)
        titlerow = ttk.Frame(inner, style="Panel.TFrame")
        titlerow.pack(fill="x")
        tk.Frame(titlerow, width=3, height=14, background=self.colors["accent2"]).pack(
            side="left", fill="y", padx=(0, 8))
        ttk.Label(titlerow, text=self.t("common.controls").upper(),
                  style="PanelTitle.TLabel").pack(side="left")
        ttk.Separator(inner).pack(fill="x", pady=(8, 10))
        self.build_controls(inner)

        ttk.Separator(inner).pack(fill="x", pady=12)
        btns = ttk.Frame(inner, style="Panel.TFrame")
        btns.pack(fill="x")
        self._pause_btn = ttk.Button(btns, text="⏸  " + self.t("common.pause"), command=self.toggle_pause)
        self._pause_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(btns, text="↺  " + self.t("common.reset"), command=self.reset).pack(
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
            text=("▶  " + self.t("common.play")) if self.paused
            else ("⏸  " + self.t("common.pause"))
        )

    # helpers for subclasses ----------------------------------------------
    def cwh(self):
        """Canvas width/height, guarded against the 1x1 size reported before
        the widget has been laid out."""
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        return (760 if w < 50 else w), (460 if h < 50 else h)

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

    # background -----------------------------------------------------------
    def paint_bg(self):
        """Paint a subtle vertical gradient across the canvas (drawn as a few
        wide bands so it stays cheap to redraw every frame)."""
        c = self.canvas
        w, h = self.cwh()
        top = self.colors["canvas_top"]
        bot = self.colors["canvas"]
        bands = 40
        for i in range(bands):
            t = i / (bands - 1)
            color = _blend(top, bot, t)
            y0 = h * i / bands
            y1 = h * (i + 1) / bands + 1
            c.create_rectangle(0, y0, w, y1, fill=color, outline="")

    def draw(self):
        """Template: clear, paint the gradient, then let the subclass render.
        Subclasses implement render(), not draw()."""
        try:
            self.canvas.delete("all")
        except tk.TclError:
            return
        self.paint_bg()
        self.render()

    # subclass hooks -------------------------------------------------------
    def build_controls(self, parent):
        raise NotImplementedError

    def reset(self):
        pass

    def tick(self, dt):
        pass

    def render(self):
        pass


def _blend(a, b, t):
    """Blend two hex colours; t=0 -> a, t=1 -> b."""
    ar, ag, ab = int(a[1:3], 16), int(a[3:5], 16), int(a[5:7], 16)
    br, bg, bb = int(b[1:3], 16), int(b[3:5], 16), int(b[5:7], 16)
    r = int(ar + (br - ar) * t)
    g = int(ag + (bg - ag) * t)
    bl = int(ab + (bb - ab) * t)
    return f"#{r:02x}{g:02x}{bl:02x}"
