# CLAUDE.md

This file points Claude to the project's memories. The memories themselves live in the `aidocks` folder; read them before working on this game.

## About the project

Virtual Balloon is the user's own remake of a 2009 iPhone game, written in Python with pygame and Prism (`requirements.txt`). Layout, modelled on the user's Sixth Sense Reborn port (since 2026-10-16):
- `VirtualBalloon.py`: the entry point only.
- `virtualballoon/`: the package. `game.py` (the `Game` class: sounds, keys, announcements), `round.py` (the rules and timings), `audio.py` (decibels and fades), `speech.py` (NVDA's own client, then Prism), `settings.py` (the registry), `paths.py` (where `game/` and `vendor/` are, also inside a PyInstaller build).
- `game/`: the original app bundle's contents; the sounds are in `game/balloon.gameproj/sounds/`. `game/SC_Info/` (the App Store license from the user's download) is in `.gitignore`.
- `vendor/nvda/`: the NVDA controller client DLL and its license.
- `docks/changelog.txt`: the change list; `README.md`, an MIT `LICENSE`.
- `user/` (ignored): the user's other projects for reference, such as the Sixth Sense port. Since 2026-10-16 it's a **private** GitHub repository, `tsatria03/VirtualBalloon-Windows` (branch `main`), and the version number is in the `VERSION` file. **Status: complete** since 2026-10-16 (the user: "it's good as complete"); change it only when the user asks.

## Where memories live

- `aidocks/general/` holds general information: who the user is, how they want Claude to work, how the game works.
- `aidocks/plans/` holds plans, finished and unfinished: one file per feature or fix, with its status and steps.
- `aidocks/private/` holds personal information. It's listed in `.gitignore`, so it never goes to GitHub; read it like the others.
- `aidocks/general/MEMORY.md` is the index: one line per memory file, linking to it. **Read it first at the start of every session**, then open the files that apply to the task.

## Rules for memories

- **Use `aidocks` for every new memory**, not Claude's built-in memory folder.
- Put general facts and rules in `aidocks/general/`, plans in `aidocks/plans/` (file names start with `plan-`), and anything personal in `aidocks/private/`.
- **Keep `general` and `plans` free of private details**, because they're stored in the repository (private for now, but it could be made public later): no names, user names in paths (write `%USERPROFILE%` or `<project>`), email addresses, device names or IDs, or purchase history. Those go in `aidocks/private/`.
- Each memory is one Markdown file about one thing, with this front matter:

  ```markdown
  ---
  name: short-kebab-case-slug
  description: one-line summary, used to decide whether the file is relevant
  metadata:
    type: user | feedback | project | reference
  ---
  ```

  For rules and decisions, add **Why:** and **How to apply:** lines. Link related memories with `[[their-name]]`.
- After adding a memory, add one line for it to `aidocks/general/MEMORY.md`: `- [Title](file.md) — short hook`. Plans are linked as `../plans/file.md`, private files as `../private/file.md`.
- Before adding a memory, check whether an existing file already covers it, and update that file instead. Fix or remove memories that turn out to be wrong.
- Don't store what the project already records (the code, `docks/changelog.txt`), and never store passwords.

## Most important rules (details in the files)

- The user uses the NVDA screen reader (`screen-reader-user.md`).
- Ask one question per reply, as plain text, never with a picker (`no-pickers.md`).
- Test the game headless and in the background; never start the game itself (`game-tests-background.md`).
- Every change goes at the top of `docks/changelog.txt`, in the user's style (`changes-file-style.md`).
- Commit and push changes myself, straight to `main`, in small commits, and **never add a co-author line** (`commit-rules.md`).
