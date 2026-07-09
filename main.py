"""Atomic Physics Lecture - offline interactive simulation program.

Entry point. Run with:  python main.py
Build to .exe with:      build.bat  (uses PyInstaller)
"""
from core.app import LectureApp


def main():
    app = LectureApp()
    app.run()


if __name__ == "__main__":
    main()
