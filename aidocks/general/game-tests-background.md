---
name: game-tests-background
description: Test the game headless (no window, no sound, no speech) as a background command; never start the game itself
metadata:
  type: feedback
---

Test the game without showing anything or making any sound:
- Set `SDL_VIDEODRIVER=dummy` and `SDL_AUDIODRIVER=dummy` (and `PYGAME_HIDE_SUPPORT_PROMPT=1`) before importing pygame, so no window opens and nothing plays.
- Set `VIRTUALBALLOON_SILENT=1`, so `virtualballoon.speech.Speech` never loads NVDA's client or Prism and says nothing; to check what is said, give the game a stand-in object with a `speak(text, interrupt=True)` method as `game.speech`.
- Settings: point `virtualballoon.settings.SETTINGS_KEY` at a separate test key (the real key plus `-test`), delete it afterwards, and check the real key is unchanged. Never write the user's real setting.
- Import from the package: `from virtualballoon.game import Game`, `from virtualballoon import round, audio, speech, settings, paths` (the script's folder on `sys.path`).
- Drive the logic with made-up times: `Round.update(now, holding)`, `Game.step(now, holding)`, `Game.cut_deflate(now)` and `Game.fade_music(now, seconds)` take the time as numbers, so a 40-second round tests in a split second. Mixer behaviour (like channel volume after a fade) needs a real-time test, still with dummy audio.
- Run the test as a **background** command, and keep test scripts outside the project folder (the session scratchpad).
- Never start the game itself (`python VirtualBalloon.py` or the packed .exe): it opens a window and makes sound on the user's computer. The user runs it.

**Why:** the user, 2026-10-16: "Please run the tests in the backround for the game." They use NVDA ([[screen-reader-user]]); windows and sounds from a test interrupt what they're doing.
**How to apply:** after each change, run a headless test like this in the background, report what it showed, then let the user try the real game.
