"""Very small translation manager backed by JSON language files.

A language file is lang/<code>.json, e.g. lang/en.json. It contains a nested
dict of strings plus a "_meta" block with a human readable name:

    { "_meta": {"name": "English"}, "app": {"title": "..."} }

Look up strings with dotted keys:  i18n.t("app.title").
English (en) is always loaded as a fallback so missing keys never crash.
"""
import json
import os

from core.paths import lang_dir

FALLBACK_CODE = "en"


class I18n:
    def __init__(self, language):
        self.dir = lang_dir()
        self.available = {}       # code -> display name
        self.translations = {}    # active language dict
        self.fallback = {}        # english dict
        self.language = language
        self.scan()
        self._load_fallback()
        self.set_language(language)

    # discovery -------------------------------------------------------------
    def scan(self):
        self.available = {}
        if not os.path.isdir(self.dir):
            return
        for name in sorted(os.listdir(self.dir)):
            if not name.lower().endswith(".json"):
                continue
            code = os.path.splitext(name)[0]
            try:
                with open(os.path.join(self.dir, name), "r", encoding="utf-8") as f:
                    data = json.load(f)
                display = data.get("_meta", {}).get("name", code)
            except (json.JSONDecodeError, OSError):
                display = code
            self.available[code] = display

    def _read(self, code):
        path = os.path.join(self.dir, code + ".json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}

    def _load_fallback(self):
        self.fallback = self._read(FALLBACK_CODE)

    # activation ------------------------------------------------------------
    def set_language(self, code):
        if code not in self.available and self.available:
            code = FALLBACK_CODE if FALLBACK_CODE in self.available else next(iter(self.available))
        self.language = code
        self.translations = self._read(code)

    # lookup ----------------------------------------------------------------
    @staticmethod
    def _dig(tree, key):
        node = tree
        for part in key.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return None
        return node if isinstance(node, str) else None

    def t(self, key, **fmt):
        value = self._dig(self.translations, key)
        if value is None:
            value = self._dig(self.fallback, key)
        if value is None:
            return key  # show the raw key so missing strings are obvious
        if fmt:
            try:
                return value.format(**fmt)
            except (KeyError, IndexError, ValueError):
                return value
        return value
