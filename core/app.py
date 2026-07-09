"""Main application window: navigation tree, content area, settings dialog.

The curriculum is data-driven so new chapters / sections / simulations can be
added just by extending CURRICULUM below.
"""
import tkinter as tk
from tkinter import font, ttk

from core.config import Config
from core.i18n import I18n
from simulations.cathode_ray import CathodeRaySim
from simulations.millikan import MillikanSim
from simulations.mass_spec import MassSpecSim
from simulations.cross_section import CrossSectionSim
from simulations.planetary import PlanetarySim
from simulations.cloud_chamber import CloudChamberSim
from simulations.rutherford import RutherfordSim
from simulations.spectral_density import SpectralDensitySim
from simulations.bb_features import BBFeaturesSim
from simulations.rayleigh_jeans import RayleighJeansSim
from simulations.planck import PlanckSim
from simulations.photoelectric_apparatus import PhotoApparatusSim
from simulations.wave_theory import WaveTheorySim
from simulations.quantum_theory import QuantumTheorySim
from simulations.applications import ApplicationsSim
from simulations.prism_spectroscope import PrismSpectroscopeSim
from simulations.frank_hertz import FrankHertzSim
from simulations.hydrogen_spectrum import HydrogenSpectrumSim

# --- curriculum registry -------------------------------------------------
# To add content later, append sections/topics here and add matching strings
# to the language files. `sim` is the Simulation subclass (or None for text).
CURRICULUM = [
    {
        "id": "ch1",
        "title_key": "curriculum.ch1.title",
        "sections": [
            {
                "id": "ch1_sec1",
                "title_key": "curriculum.ch1.sec1.title",
                "topics": [
                    {"id": "cathode_ray", "title_key": "topic.cathode_ray.title", "sim": CathodeRaySim},
                    {"id": "millikan", "title_key": "topic.millikan.title", "sim": MillikanSim},
                    {"id": "mass_spec", "title_key": "topic.mass_spec.title", "sim": MassSpecSim},
                ],
            },
            {
                "id": "ch1_sec2",
                "title_key": "curriculum.ch1.sec2.title",
                "topics": [
                    {"id": "cross_section", "title_key": "topic.cross_section.title", "sim": CrossSectionSim},
                    {"id": "planetary", "title_key": "topic.planetary.title", "sim": PlanetarySim},
                    {"id": "cloud_chamber", "title_key": "topic.cloud_chamber.title", "sim": CloudChamberSim},
                    {"id": "rutherford", "title_key": "topic.rutherford.title", "sim": RutherfordSim},
                ],
            },
        ],
    },
    {
        "id": "ch2",
        "title_key": "curriculum.ch2.title",
        "sections": [
            {
                "id": "ch2_sec1",
                "title_key": "curriculum.ch2.sec1.title",
                "topics": [
                    {"id": "spectral_density", "title_key": "topic.spectral_density.title", "sim": SpectralDensitySim},
                    {"id": "bb_features", "title_key": "topic.bb_features.title", "sim": BBFeaturesSim},
                    {"id": "rayleigh_jeans", "title_key": "topic.rayleigh_jeans.title", "sim": RayleighJeansSim},
                    {"id": "planck", "title_key": "topic.planck.title", "sim": PlanckSim},
                ],
            },
            {
                "id": "ch2_sec2",
                "title_key": "curriculum.ch2.sec2.title",
                "topics": [
                    {"id": "pe_apparatus", "title_key": "topic.pe_apparatus.title", "sim": PhotoApparatusSim},
                    {"id": "wave_theory", "title_key": "topic.wave_theory.title", "sim": WaveTheorySim},
                    {"id": "quantum_theory", "title_key": "topic.quantum_theory.title", "sim": QuantumTheorySim},
                    {"id": "applications", "title_key": "topic.applications.title", "sim": ApplicationsSim},
                ],
            },
            {
                "id": "ch2_sec3",
                "title_key": "curriculum.ch2.sec3.title",
                "topics": [
                    {"id": "prism_spectroscope", "title_key": "topic.prism_spectroscope.title", "sim": PrismSpectroscopeSim},
                    {"id": "frank_hertz", "title_key": "topic.frank_hertz.title", "sim": FrankHertzSim},
                    {"id": "hydrogen_spectrum", "title_key": "topic.hydrogen_spectrum.title", "sim": HydrogenSpectrumSim},
                ],
            },
        ],
    },
]

COLORS = {
    "bg": "#080d1a",             # window backdrop
    "sidebar": "#0e1730",        # sidebar base
    "sidebar_top": "#111d38",    # sidebar gradient top
    "sidebar_bot": "#0a1122",    # sidebar gradient bottom
    "content": "#0a1020",
    "panel": "#131e38",          # control card
    "panel2": "#1a2748",         # nested control / button
    "canvas": "#0a1122",         # gradient bottom (canvas)
    "canvas_top": "#12203c",     # gradient top (canvas)
    "canvas_text": "#8ba0c4",
    "accent": "#4f8cff",         # primary electric blue
    "accent_hover": "#6ea0ff",
    "accent2": "#22d3ee",        # cyan
    "text": "#eef3fc",
    "muted": "#8092b4",
    "border": "#22304f",
    "good": "#34d399",
    "warn": "#fbbf24",
    "bad": "#f87171",
    "value": "#7dd3fc",
}


class LectureApp:
    def __init__(self):
        self.config = Config()
        self.i18n = I18n(self.config.get("language"))
        self.colors = COLORS

        self.root = tk.Tk()
        self.root.title(self.i18n.t("app.title"))
        self.root.geometry("1180x740")
        self.root.minsize(980, 640)
        self.root.configure(background=COLORS["bg"])

        self._init_fonts()
        self._init_style()

        self.current_view = None
        self.topic_lookup = {}   # tree item id -> topic dict

        self._build_ui()
        self._show_welcome()

    # fonts ----------------------------------------------------------------
    def _init_fonts(self):
        fam = self.config.get("font_family")
        size = int(self.config.get("font_size"))
        self.fonts = {
            "base": font.Font(family=fam, size=size),
            "small": font.Font(family=fam, size=max(8, size - 2)),
            "tiny": font.Font(family=fam, size=max(7, size - 3)),
            "bold": font.Font(family=fam, size=size, weight="bold"),
            "heading": font.Font(family=fam, size=size + 7, weight="bold"),
            "title": font.Font(family=fam, size=size + 15, weight="bold"),
            "panel_title": font.Font(family=fam, size=max(8, size - 1), weight="bold"),
            "chip": font.Font(family=fam, size=max(7, size - 3), weight="bold"),
        }
        # make ttk's built-in named fonts follow the config too
        for named in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
            try:
                font.nametofont(named).configure(family=fam, size=size)
            except tk.TclError:
                pass

    def _apply_fonts(self):
        fam = self.config.get("font_family")
        size = int(self.config.get("font_size"))
        self.fonts["base"].configure(family=fam, size=size)
        self.fonts["small"].configure(family=fam, size=max(8, size - 2))
        self.fonts["tiny"].configure(family=fam, size=max(7, size - 3))
        self.fonts["bold"].configure(family=fam, size=size)
        self.fonts["heading"].configure(family=fam, size=size + 7)
        self.fonts["title"].configure(family=fam, size=size + 15)
        self.fonts["panel_title"].configure(family=fam, size=max(8, size - 1))
        self.fonts["chip"].configure(family=fam, size=max(7, size - 3))
        for named in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
            try:
                font.nametofont(named).configure(family=fam, size=size)
            except tk.TclError:
                pass

    # style ----------------------------------------------------------------
    def _init_style(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self._configure_style()

    def _configure_style(self):
        c = self.colors
        s = self.style

        # frames / surfaces
        s.configure("Content.TFrame", background=c["content"])
        s.configure("Sidebar.TFrame", background=c["sidebar"])
        s.configure("Panel.TFrame", background=c["panel"])
        s.configure("Panel2.TFrame", background=c["panel2"])

        # labels
        s.configure("TLabel", background=c["content"], foreground=c["text"], font=self.fonts["base"])
        s.configure("Muted.TLabel", background=c["content"], foreground=c["muted"], font=self.fonts["base"])
        s.configure("Heading.TLabel", background=c["content"], foreground=c["text"], font=self.fonts["heading"])
        s.configure("Title.TLabel", background=c["content"], foreground=c["text"], font=self.fonts["title"])
        s.configure("Sidebar.TLabel", background=c["sidebar"], foreground=c["muted"], font=self.fonts["small"])
        s.configure("SidebarTitle.TLabel", background=c["sidebar"], foreground=c["text"], font=self.fonts["heading"])
        s.configure("Kicker.TLabel", background=c["sidebar"], foreground=c["accent2"], font=self.fonts["chip"])
        s.configure("SectionHead.TLabel", background=c["sidebar"], foreground=c["muted"], font=self.fonts["chip"])

        s.configure("Panel.TLabel", background=c["panel"], foreground=c["text"], font=self.fonts["base"])
        s.configure("PanelTitle.TLabel", background=c["panel"], foreground=c["accent2"], font=self.fonts["panel_title"])
        s.configure("Value.TLabel", background=c["panel"], foreground=c["accent"], font=self.fonts["bold"])
        s.configure("Readout.TLabel", background=c["panel"], foreground=c["value"], font=self.fonts["bold"])
        s.configure("Panel.TCheckbutton", background=c["panel"], foreground=c["text"], font=self.fonts["base"])
        s.map("Panel.TCheckbutton",
              background=[("active", c["panel"])],
              indicatorcolor=[("selected", c["accent"]), ("!selected", c["panel2"])])

        # buttons: ghost default + accent primary
        s.configure("TButton", font=self.fonts["bold"], padding=(12, 9),
                    background=c["panel2"], foreground=c["text"],
                    borderwidth=0, relief="flat", focuscolor=c["panel2"])
        s.map("TButton",
              background=[("pressed", c["accent"]), ("active", c["border"])],
              foreground=[("active", c["text"])])
        s.configure("Accent.TButton", font=self.fonts["bold"], padding=(12, 9),
                    background=c["accent"], foreground="#08122b",
                    borderwidth=0, relief="flat", focuscolor=c["accent"])
        s.map("Accent.TButton",
              background=[("pressed", c["accent"]), ("active", c["accent_hover"])],
              foreground=[("active", "#08122b")])

        # navigation tree
        s.configure("Nav.Treeview", background=c["sidebar"], fieldbackground=c["sidebar"],
                    foreground=c["text"], borderwidth=0, rowheight=32, font=self.fonts["base"])
        s.map("Nav.Treeview",
              background=[("selected", c["accent"])],
              foreground=[("selected", "#08122b")])
        s.configure("Nav.Treeview.Item", padding=2)
        s.layout("Nav.Treeview", [("Nav.Treeview.treearea", {"sticky": "nswe"})])  # hide header

        # sliders
        s.configure("Horizontal.TScale", background=c["panel"], troughcolor=c["panel2"],
                    borderwidth=0, lightcolor=c["accent"], darkcolor=c["accent"])
        s.map("Horizontal.TScale", background=[("active", c["panel"])])

        # combobox
        s.configure("TCombobox", fieldbackground=c["panel2"], background=c["panel2"],
                    foreground=c["text"], arrowcolor=c["accent2"], borderwidth=0,
                    padding=6, selectbackground=c["panel2"], selectforeground=c["text"])
        s.map("TCombobox", fieldbackground=[("readonly", c["panel2"])],
              foreground=[("readonly", c["text"])])

        # scrollbar (navigation)
        s.configure("Nav.Vertical.TScrollbar", background=c["panel2"], troughcolor=c["sidebar"],
                    bordercolor=c["sidebar"], arrowcolor=c["muted"], borderwidth=0, relief="flat")
        s.map("Nav.Vertical.TScrollbar", background=[("active", c["accent"])])

        # spinbox / separators
        s.configure("TSpinbox", fieldbackground=c["panel2"], background=c["panel2"],
                    foreground=c["text"], arrowcolor=c["accent2"], borderwidth=0, padding=4)
        s.configure("TSeparator", background=c["border"])
        try:
            self.root.option_add("*TCombobox*Listbox.background", c["panel2"])
            self.root.option_add("*TCombobox*Listbox.foreground", c["text"])
            self.root.option_add("*TCombobox*Listbox.selectBackground", c["accent"])
            self.root.option_add("*TCombobox*Listbox.selectForeground", "#08122b")
        except tk.TclError:
            pass

    # UI -------------------------------------------------------------------
    def _build_ui(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # sidebar
        sidebar = ttk.Frame(self.root, style="Sidebar.TFrame", width=292)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)
        self.sidebar = sidebar

        # brand header: atom glyph + title + subtitle
        head = ttk.Frame(sidebar, style="Sidebar.TFrame")
        head.pack(fill="x", padx=20, pady=(22, 10))
        logo = ttk.Label(head, text="⚛", style="SidebarTitle.TLabel", foreground=self.colors["accent2"])
        logo.pack(side="left", padx=(0, 10))
        titlecol = ttk.Frame(head, style="Sidebar.TFrame")
        titlecol.pack(side="left", fill="x")
        self.lbl_app_title = ttk.Label(titlecol, text=self.i18n.t("app.title"), style="SidebarTitle.TLabel")
        self.lbl_app_title.pack(anchor="w")
        self.lbl_app_sub = ttk.Label(titlecol, text=self.i18n.t("app.subtitle"), style="Sidebar.TLabel")
        self.lbl_app_sub.pack(anchor="w")

        ttk.Separator(sidebar).pack(fill="x", padx=20, pady=(4, 8))
        self.lbl_contents = ttk.Label(sidebar, text=self.i18n.t("nav.contents"), style="SectionHead.TLabel")
        self.lbl_contents.pack(anchor="w", padx=22, pady=(2, 4))

        treewrap = ttk.Frame(sidebar, style="Sidebar.TFrame")
        treewrap.pack(fill="both", expand=True, padx=(12, 6))
        self.tree = ttk.Treeview(treewrap, style="Nav.Treeview", show="tree", selectmode="browse")
        vsb = ttk.Scrollbar(treewrap, orient="vertical", command=self.tree.yview,
                            style="Nav.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        # mouse-wheel scrolling over the navigation
        self.tree.bind("<MouseWheel>", self._on_tree_wheel)
        self.tree.bind("<Button-4>", lambda e: self.tree.yview_scroll(-1, "units"))
        self.tree.bind("<Button-5>", lambda e: self.tree.yview_scroll(1, "units"))
        self._populate_tree()

        ttk.Separator(sidebar).pack(fill="x", padx=20, pady=(6, 0))
        footer = ttk.Frame(sidebar, style="Sidebar.TFrame")
        footer.pack(fill="x", padx=16, pady=16)
        self.btn_settings = ttk.Button(footer, text="⚙  " + self.i18n.t("nav.settings"),
                                       style="Accent.TButton", command=self._open_settings)
        self.btn_settings.pack(fill="x")
        self.btn_about = ttk.Button(footer, text=self.i18n.t("nav.about"), command=self._show_about)
        self.btn_about.pack(fill="x", pady=(8, 0))

        # thin divider between sidebar and content
        divider = tk.Frame(self.root, width=1, background=self.colors["border"])
        divider.grid(row=0, column=1, sticky="nsw")

        # content area
        self.content = ttk.Frame(self.root, style="Content.TFrame")
        self.content.grid(row=0, column=1, sticky="nsew", padx=(1, 0))
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

    def _populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        self.topic_lookup = {}
        for ch in CURRICULUM:
            ch_id = self.tree.insert("", "end", text="  " + self.i18n.t(ch["title_key"]), open=True)
            for sec in ch["sections"]:
                sec_id = self.tree.insert(ch_id, "end", text="  " + self.i18n.t(sec["title_key"]), open=True)
                for i, topic in enumerate(sec["topics"], 1):
                    node = self.tree.insert(sec_id, "end", text=f"  {i}. " + self.i18n.t(topic["title_key"]))
                    self.topic_lookup[node] = topic

    # navigation -----------------------------------------------------------
    def _on_tree_wheel(self, event):
        self.tree.yview_scroll(-1 if event.delta > 0 else 1, "units")

    def _on_tree_select(self, _evt):
        sel = self.tree.selection()
        if not sel:
            return
        topic = self.topic_lookup.get(sel[0])
        if topic and topic.get("sim"):
            self._show_topic(topic)

    def _clear_content(self):
        if self.current_view is not None:
            if hasattr(self.current_view, "on_hide"):
                self.current_view.on_hide()
            self.current_view.destroy()
            self.current_view = None

    def _show_topic(self, topic):
        self._clear_content()
        view = topic["sim"](self.content, self)
        view.grid(row=0, column=0, sticky="nsew")
        view.on_show()
        self.current_view = view

    def _show_welcome(self):
        self._clear_content()
        c = self.colors
        frame = ttk.Frame(self.content, style="Content.TFrame")
        frame.grid(row=0, column=0, sticky="nsew")
        inner = ttk.Frame(frame, style="Content.TFrame")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(inner, text="⚛  " + self.i18n.t("app.subtitle").upper(),
                  style="TLabel", foreground=c["accent2"], font=self.fonts["chip"]).pack(anchor="center")
        ttk.Label(inner, text=self.i18n.t("welcome.title"), style="Title.TLabel").pack(anchor="center", pady=(8, 0))
        ttk.Label(inner, text=self.i18n.t("welcome.body"), style="Muted.TLabel",
                  wraplength=680, justify="center").pack(anchor="center", pady=(14, 22))

        # chapter cards
        cards = ttk.Frame(inner, style="Content.TFrame")
        cards.pack(anchor="center")
        for idx, ch in enumerate(CURRICULUM):
            card = tk.Frame(cards, background=c["panel"], highlightthickness=1,
                            highlightbackground=c["border"])
            card.grid(row=0, column=idx, padx=8, sticky="n")
            pad = ttk.Frame(card, style="Panel.TFrame")
            pad.pack(fill="both", padx=16, pady=14)
            n_topics = sum(len(sec["topics"]) for sec in ch["sections"])
            ttk.Label(pad, text=self.i18n.t(ch["title_key"]), style="PanelTitle.TLabel",
                      foreground=c["text"], font=self.fonts["bold"]).pack(anchor="w")
            ttk.Label(pad, text=self.i18n.t("welcome.topics", n=n_topics),
                      style="Panel.TLabel", foreground=c["accent2"],
                      font=self.fonts["small"]).pack(anchor="w", pady=(1, 8))
            for sec in ch["sections"]:
                row = ttk.Frame(pad, style="Panel.TFrame")
                row.pack(fill="x", pady=1)
                ttk.Label(row, text="›", style="Panel.TLabel", foreground=c["accent"]).pack(side="left", padx=(0, 6))
                ttk.Label(row, text=self.i18n.t(sec["title_key"]), style="Panel.TLabel",
                          foreground=c["muted"], font=self.fonts["small"]).pack(side="left")

        ttk.Label(inner, text=self.i18n.t("welcome.hint"), style="Muted.TLabel",
                  font=self.fonts["small"]).pack(anchor="center", pady=(22, 0))
        self.current_view = frame

    # settings -------------------------------------------------------------
    def _open_settings(self):
        dlg = tk.Toplevel(self.root)
        dlg.title(self.i18n.t("settings.title"))
        dlg.configure(background=self.colors["panel"])
        dlg.transient(self.root)
        dlg.resizable(False, False)
        dlg.grab_set()

        wrap = ttk.Frame(dlg, style="Panel.TFrame")
        wrap.pack(fill="both", expand=True, padx=26, pady=24)

        titlerow = ttk.Frame(wrap, style="Panel.TFrame")
        titlerow.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))
        tk.Frame(titlerow, width=3, height=16, background=self.colors["accent2"]).pack(
            side="left", fill="y", padx=(0, 8))
        ttk.Label(titlerow, text="⚙  " + self.i18n.t("settings.title"),
                  style="PanelTitle.TLabel", foreground=self.colors["text"],
                  font=self.fonts["heading"]).pack(side="left")

        # language
        ttk.Label(wrap, text=self.i18n.t("settings.language"), style="Panel.TLabel").grid(
            row=1, column=0, sticky="w", pady=6, padx=(0, 12))
        codes = list(self.i18n.available.keys()) or ["en"]
        names = [self.i18n.available.get(c, c) for c in codes]
        lang_var = tk.StringVar(value=self.i18n.available.get(self.i18n.language, "English"))
        lang_combo = ttk.Combobox(wrap, state="readonly", values=names, textvariable=lang_var, width=22)
        lang_combo.grid(row=1, column=1, sticky="ew", pady=6)

        # font family
        ttk.Label(wrap, text=self.i18n.t("settings.font_family"), style="Panel.TLabel").grid(
            row=2, column=0, sticky="w", pady=6, padx=(0, 12))
        families = sorted(set(font.families()))
        fam_var = tk.StringVar(value=self.config.get("font_family"))
        fam_combo = ttk.Combobox(wrap, values=families, textvariable=fam_var, width=22)
        fam_combo.grid(row=2, column=1, sticky="ew", pady=6)

        # font size
        ttk.Label(wrap, text=self.i18n.t("settings.font_size"), style="Panel.TLabel").grid(
            row=3, column=0, sticky="w", pady=6, padx=(0, 12))
        size_var = tk.IntVar(value=int(self.config.get("font_size")))
        ttk.Spinbox(wrap, from_=8, to=22, textvariable=size_var, width=8).grid(
            row=3, column=1, sticky="w", pady=6)

        btns = ttk.Frame(wrap, style="Panel.TFrame")
        btns.grid(row=4, column=0, columnspan=2, sticky="e", pady=(16, 0))

        def apply_and_close():
            # language: map chosen display name back to code
            chosen = lang_var.get()
            for code, disp in self.i18n.available.items():
                if disp == chosen:
                    self.config.set("language", code)
                    break
            self.config.set("font_family", fam_var.get() or self.config.get("font_family"))
            try:
                self.config.set("font_size", int(size_var.get()))
            except (tk.TclError, ValueError):
                pass
            self.config.save()
            self._apply_settings()
            dlg.destroy()

        ttk.Button(btns, text=self.i18n.t("settings.cancel"), command=dlg.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(btns, text=self.i18n.t("settings.apply"), style="Accent.TButton",
                   command=apply_and_close).pack(side="right")
        wrap.columnconfigure(1, weight=1)

    def _apply_settings(self):
        # reload language, refresh fonts and every visible string
        self.i18n.set_language(self.config.get("language"))
        self._apply_fonts()
        self._configure_style()
        self.root.title(self.i18n.t("app.title"))
        self.lbl_app_title.configure(text=self.i18n.t("app.title"))
        self.lbl_app_sub.configure(text=self.i18n.t("app.subtitle"))
        self.lbl_contents.configure(text=self.i18n.t("nav.contents"))
        self.btn_settings.configure(text="⚙  " + self.i18n.t("nav.settings"))
        self.btn_about.configure(text=self.i18n.t("nav.about"))
        self._populate_tree()
        # rebuild current view so its labels pick up the new language
        self._show_welcome()

    def _show_about(self):
        dlg = tk.Toplevel(self.root)
        dlg.title(self.i18n.t("nav.about"))
        dlg.configure(background=self.colors["panel"])
        dlg.transient(self.root)
        dlg.resizable(False, False)
        dlg.grab_set()
        wrap = ttk.Frame(dlg, style="Panel.TFrame")
        wrap.pack(fill="both", expand=True, padx=24, pady=24)
        ttk.Label(wrap, text=self.i18n.t("app.title"), style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(wrap, text=self.i18n.t("about.text"), style="Panel.TLabel",
                  wraplength=420, justify="left").pack(anchor="w", pady=(10, 16))
        ttk.Button(wrap, text=self.i18n.t("settings.cancel"), command=dlg.destroy).pack(anchor="e")

    # run ------------------------------------------------------------------
    def run(self):
        self.root.mainloop()
