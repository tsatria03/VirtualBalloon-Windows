"""Where the game's files are.

``game/`` holds the original app bundle's contents, as ``Payload/balloon.app`` shipped,
with the sounds in ``game/balloon.gameproj/sounds``. ``vendor/`` holds the NVDA controller
client.

From source, both are beside ``VirtualBalloon.py``. In a build, ``vendor/`` is inside the
program (PyInstaller's folder, ``sys._MEIPASS``), and ``game/`` is beside the executable in
a folder build, or inside it in a single-exe build (compiler.py --embed). The first place
that has the sounds wins.
"""
import os
import sys

FROZEN = getattr(sys, "frozen", False)
if FROZEN:
    ROOT = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    EXE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    EXE_DIR = ROOT

#: Where the sounds are inside the game folder.
SOUNDS_IN_GAME = os.path.join("balloon.gameproj", "sounds")


def _find_game():
    """The game folder beside the executable, or inside the build; the first with the sounds."""
    for place in (os.path.join(EXE_DIR, "game"), os.path.join(ROOT, "game")):
        if os.path.isdir(os.path.join(place, SOUNDS_IN_GAME)):
            return place
    return os.path.join(ROOT, "game")      # missing: the game says so when it loads the sounds


GAME = _find_game()
SOUNDS = os.path.join(GAME, SOUNDS_IN_GAME)
VENDOR = os.path.join(ROOT, "vendor")
NVDA_DLL = os.path.join(VENDOR, "nvda", "nvdaControllerClient64.dll")
