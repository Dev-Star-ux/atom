"""Load / save user configuration (language, font)."""
import json

from core.paths import config_path

DEFAULTS = {
    "language": "en",
    "font_family": "Segoe UI",
    "font_size": 11,
}


class Config:
    def __init__(self):
        self.data = dict(DEFAULTS)
        self.load()

    def load(self):
        try:
            with open(config_path(), "r", encoding="utf-8") as f:
                loaded = json.load(f)
            for key in DEFAULTS:
                if key in loaded:
                    self.data[key] = loaded[key]
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            # No config yet, or it is corrupt -> keep defaults.
            pass

    def save(self):
        try:
            with open(config_path(), "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    # convenience accessors -------------------------------------------------
    def get(self, key):
        return self.data.get(key, DEFAULTS.get(key))

    def set(self, key, value):
        self.data[key] = value
