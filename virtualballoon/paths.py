"""Where the game's files are.

``game/`` holds the original app bundle's contents, as ``Payload/balloon.app`` shipped,
with the sounds in ``game/balloon.gameproj/sounds``. ``vendor/`` holds the NVDA controller
client. Both are found beside the script, or inside a PyInstaller build.
"""
import os
import sys

FROZEN = getattr(sys, "frozen", False)
if FROZEN:
    ROOT = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
else:
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GAME = os.path.join(ROOT, "game")
SOUNDS = os.path.join(GAME, "balloon.gameproj", "sounds")
VENDOR = os.path.join(ROOT, "vendor")
NVDA_DLL = os.path.join(VENDOR, "nvda", "nvdaControllerClient64.dll")
