---
name: build-and-release
description: compiler.py and releaser.py - Windows-only, no GitHub workflows; how builds are made and tested, and what a release does
metadata:
  type: project
---

Since 2026-10-16 the game has `compiler.py` and `releaser.py`, adapted from Sixth Sense Reborn's (in the ignored `user/` folder). The user: "This game is only for windows only. We don't need github workflows."

- **compiler.py**: PyInstaller into `dist/VirtualBalloon-Windows` (`VirtualBalloon.exe`). Menu or flags: folder build, `--test`, `--embed` (sounds inside), `--clean`, `--console`, `--onefile`, `--no-game`, `--dry-run`. Bundles the NVDA DLL, Prism (`--collect-all prism`, `_cffi_backend`, and `prism/_native/*.pyd` added by name) and the licenses (NVDA client, Prism's dist-info licenses, pygame's LGPL) as `licenses/` inside. Of `game/` the whole `balloon.gameproj` ships (since 2026-10-16, user: "copy all of the gameproj folders back, except for the private apple id stuff"): actors, scenes, images, sounds and its 3 XML files, 35 files (`gameproj_files()`); never the iOS binary, the engine, the icons or `SC_Info`, and `NEVER_SHIP` (`*.sinf`, `*.supp`, `SC_Info`) is skipped wherever it appears. The game itself reads only the sounds. `--embed` stages the folder in `build/embed/balloon.gameproj` first. Beside the exe: `docks/changelog.txt` (empty `unrelease:` heading stripped from the copy), `VERSION`, `license.txt`.
- **--test** starts the build with `--exit-after 6` and `VIRTUALBALLOON_SILENT=1`, SDL dummy video and audio: no window, sound or speech; passes on exit code 0. First run 2026-10-16: built in 25 s, test passed, 173 files, 37.8 MB.
- **releaser.py**: check (committed, pushed, `gh` signed in, 5 to 100 lines under `unrelease:`, or Y to release anyway with fewer) -> prepare (VERSION = `YY.MM.DD-N` counted from `V` tags; changelog lines filed under `YY.MM.DD-N:`) -> build with `--test` (a failed build restores VERSION and the changelog) -> zip `dist/VirtualBalloon-Win-<version>.zip` (one `VirtualBalloon-Windows` folder inside) -> commit "Release <version>" and push -> tag `V<version>` -> `gh release create` titled "Virtual Balloon V<version>". Every step asks Y/N; nothing ever moves a tag or replaces a release file.
- `paths.py` finds `game/` beside the exe (folder build) or inside it (`--embed`); `VirtualBalloon.py` takes `--exit-after SECONDS` and, if the game crashes, says why aloud (a windowed build has no console).

**Why:** the user asked for these to release the game ([[version-file]]: the releaser is what sets VERSION).
**How to apply:** never run a release (releaser.py) unless the user asks; it commits, tags and publishes. When testing a build myself, run compiler.py on the hidden desktop with the watchdog watching `VirtualBalloon` ([[game-tests-background]]). `build/`, `dist/` and `*.spec` are ignored.
