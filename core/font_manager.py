"""Load custom fonts from the editable fonts/ folder next to the program.

Drop .ttf / .otf / .ttc files into fonts/ (or dist/fonts/ beside the .exe).
On Windows they are registered for the current session; the family name then
appears in Settings → Font alongside system fonts.
"""
import os
import sys

from core.paths import fonts_dir

_FONT_EXTS = (".ttf", ".otf", ".ttc")
_registered = []          # absolute paths successfully loaded this session
_custom_families = []     # font family names introduced by fonts/


def _register_file(path: str) -> bool:
    """Register one font file with the OS (Windows). Returns True on success."""
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        flags = 0x10   # FR_PRIVATE — available to this process only
        n = ctypes.windll.gdi32.AddFontResourceExW(os.path.abspath(path), flags, 0)
        return n > 0
    except (OSError, AttributeError):
        return False


def load_custom_fonts(tk_root=None) -> list[str]:
    """Scan fonts/, register files, return new font family names.

    Safe to call more than once; already-loaded files are skipped.
    """
    global _custom_families
    folder = fonts_dir()
    if not os.path.isdir(folder):
        _custom_families = []
        return _custom_families

    before = set()
    if tk_root is not None:
        try:
            from tkinter import font as tkfont
            before = set(tkfont.families(root=tk_root))
        except tk.TclError:
            before = set()

    for name in sorted(os.listdir(folder)):
        if not name.lower().endswith(_FONT_EXTS):
            continue
        path = os.path.join(folder, name)
        if path in _registered:
            continue
        if _register_file(path):
            _registered.append(path)

    if tk_root is not None:
        try:
            from tkinter import font as tkfont
            after = set(tkfont.families(root=tk_root))
            _custom_families = sorted(after - before)
        except tk.TclError:
            pass

    return list(_custom_families)


def custom_families() -> list[str]:
    """Family names loaded from fonts/ this session."""
    return list(_custom_families)


def available_families(tk_root=None) -> list[str]:
    """All font families: custom (from fonts/) first, then system."""
    from tkinter import font as tkfont
    try:
        kw = {"root": tk_root} if tk_root is not None else {}
        system = set(tkfont.families(**kw))
    except tk.TclError:
        system = set()
    custom = set(_custom_families)
    # custom first (sorted), then remaining system fonts
    rest = sorted(system - custom)
    return list(_custom_families) + rest


def fonts_folder() -> str:
    """Absolute path to the editable fonts directory."""
    return fonts_dir()
