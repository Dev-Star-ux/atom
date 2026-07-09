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
        ],
    },
]

COLORS = {
    "bg": "#0f172a",
    "sidebar": "#111c33",
    "content": "#0f172a",
    "panel": "#1e293b",
    "canvas": "#0b1220",
    "canvas_text": "#94a3b8",
    "accent": "#3b82f6",
    "text": "#e2e8f0",
    "muted": "#94a3b8",
    "border": "#233047",
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
            "heading": font.Font(family=fam, size=size + 6, weight="bold"),
            "title": font.Font(family=fam, size=size + 12, weight="bold"),
            "panel_title": font.Font(family=fam, size=size + 1, weight="bold"),
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
        self.fonts["heading"].configure(family=fam, size=size + 6)
        self.fonts["title"].configure(family=fam, size=size + 12)
        self.fonts["panel_title"].configure(family=fam, size=size + 1)
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
        s.configure("Content.TFrame", background=c["content"])
        s.configure("Sidebar.TFrame", background=c["sidebar"])
        s.configure("Panel.TFrame", background=c["panel"])

        s.configure("TLabel", background=c["content"], foreground=c["text"], font=self.fonts["base"])
        s.configure("Muted.TLabel", background=c["content"], foreground=c["muted"], font=self.fonts["base"])
        s.configure("Heading.TLabel", background=c["content"], foreground=c["text"], font=self.fonts["heading"])
        s.configure("Title.TLabel", background=c["content"], foreground=c["text"], font=self.fonts["title"])
        s.configure("Sidebar.TLabel", background=c["sidebar"], foreground=c["muted"], font=self.fonts["small"])
        s.configure("SidebarTitle.TLabel", background=c["sidebar"], foreground=c["text"], font=self.fonts["panel_title"])

        s.configure("Panel.TLabel", background=c["panel"], foreground=c["text"], font=self.fonts["base"])
        s.configure("PanelTitle.TLabel", background=c["panel"], foreground=c["text"], font=self.fonts["panel_title"])
        s.configure("Value.TLabel", background=c["panel"], foreground=c["accent"], font=self.fonts["base"])
        s.configure("Readout.TLabel", background=c["panel"], foreground="#38bdf8", font=self.fonts["base"])
        s.configure("Panel.TCheckbutton", background=c["panel"], foreground=c["text"], font=self.fonts["base"])
        s.map("Panel.TCheckbutton", background=[("active", c["panel"])])

        s.configure("TButton", font=self.fonts["base"], padding=6)
        s.configure("Accent.TButton", font=self.fonts["base"], padding=8)

        s.configure("Nav.Treeview", background=c["sidebar"], fieldbackground=c["sidebar"],
                    foreground=c["text"], borderwidth=0, rowheight=30, font=self.fonts["base"])
        s.map("Nav.Treeview", background=[("selected", c["accent"])],
              foreground=[("selected", "#ffffff")])
        s.configure("Nav.Treeview.Heading", background=c["sidebar"], foreground=c["muted"])
        s.layout("Nav.Treeview", [("Nav.Treeview.treearea", {"sticky": "nswe"})])  # hide header

        s.configure("TScale", background=c["panel"])
        s.configure("TCombobox", fieldbackground="#0b1220", background=c["panel"], foreground=c["text"])
        s.configure("TSeparator", background=c["border"])

    # UI -------------------------------------------------------------------
    def _build_ui(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # sidebar
        sidebar = ttk.Frame(self.root, style="Sidebar.TFrame", width=290)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)
        self.sidebar = sidebar

        head = ttk.Frame(sidebar, style="Sidebar.TFrame")
        head.pack(fill="x", padx=18, pady=(18, 8))
        self.lbl_app_title = ttk.Label(head, text=self.i18n.t("app.title"), style="SidebarTitle.TLabel")
        self.lbl_app_title.pack(anchor="w")
        self.lbl_app_sub = ttk.Label(head, text=self.i18n.t("app.subtitle"), style="Sidebar.TLabel")
        self.lbl_app_sub.pack(anchor="w")

        self.lbl_contents = ttk.Label(sidebar, text=self.i18n.t("nav.contents"), style="Sidebar.TLabel")
        self.lbl_contents.pack(anchor="w", padx=18, pady=(10, 2))

        self.tree = ttk.Treeview(sidebar, style="Nav.Treeview", show="tree", selectmode="browse")
        self.tree.pack(fill="both", expand=True, padx=10)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self._populate_tree()

        footer = ttk.Frame(sidebar, style="Sidebar.TFrame")
        footer.pack(fill="x", padx=14, pady=14)
        self.btn_settings = ttk.Button(footer, text=self.i18n.t("nav.settings"), command=self._open_settings)
        self.btn_settings.pack(fill="x")
        self.btn_about = ttk.Button(footer, text=self.i18n.t("nav.about"), command=self._show_about)
        self.btn_about.pack(fill="x", pady=(6, 0))

        # content area
        self.content = ttk.Frame(self.root, style="Content.TFrame")
        self.content.grid(row=0, column=1, sticky="nsew")
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
        frame = ttk.Frame(self.content, style="Content.TFrame")
        frame.grid(row=0, column=0, sticky="nsew")
        inner = ttk.Frame(frame, style="Content.TFrame")
        inner.place(relx=0.5, rely=0.42, anchor="center")
        ttk.Label(inner, text=self.i18n.t("welcome.title"), style="Title.TLabel").pack(anchor="center")
        ttk.Label(inner, text=self.i18n.t("welcome.body"), style="Muted.TLabel",
                  wraplength=620, justify="center").pack(anchor="center", pady=(14, 0))
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
        wrap.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(wrap, text=self.i18n.t("settings.title"), style="PanelTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

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

        ttk.Button(btns, text=self.i18n.t("settings.cancel"), command=dlg.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(btns, text=self.i18n.t("settings.apply"), command=apply_and_close).pack(side="right")
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
        self.btn_settings.configure(text=self.i18n.t("nav.settings"))
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
