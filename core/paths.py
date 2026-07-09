"""Filesystem paths that work both when run as a script and when frozen by
PyInstaller into a single .exe.

- Writable / user-editable files (config.json, lang/) live next to the
  executable so the user can change them any time without recompiling.
- If an external copy is missing (fresh install), we fall back to the copy
  bundled inside the .exe (PyInstaller's _MEIPASS temp dir).
"""
import os
import sys


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def base_dir() -> str:
    """Directory that holds the running program (folder of the .exe, or the
    project root when running from source)."""
    if is_frozen():
        return os.path.dirname(sys.executable)
    # this file is core/paths.py -> project root is one level up
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_dir() -> str:
    """Directory of read-only resources bundled with the program."""
    if is_frozen():
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return base_dir()


def lang_dir() -> str:
    """Language files folder. Prefer an external, editable copy."""
    external = os.path.join(base_dir(), "lang")
    if os.path.isdir(external):
        return external
    return os.path.join(resource_dir(), "lang")


def config_path() -> str:
    return os.path.join(base_dir(), "config.json")
