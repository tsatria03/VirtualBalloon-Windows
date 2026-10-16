---
name: changes-file-style
description: How the user writes docks/changes.txt: YY.MM.DD date headings, newest first, one sentence per line
metadata:
  type: feedback
---

Every change to the game gets a line in `docks/changes.txt` (the user moved it into the `docks` folder on 2026-10-16):
- Keep it small and plain, one sentence per line (user, 2026-10-16: "Nothing too fancy. One centince per line").
- Reverse chronological order: the newest entry at the top, also inside a heading.
- Headings are dates as YY.MM.DD (for example `26.10.16`), not version numbers.
- Lines are phrased as changes: "You can now ...", "Made ...", "... now plays ...".

**Why:** the user rewrote my first changes.txt (a "Version 1.0" heading and plain feature lines) into this style on 2026-10-16.
**Small follow-up tweaks** to something already listed (a changed number, a reworded message) edit the existing line instead of adding a new one (user, 2026-10-16: "For the change log, you can just modify one of the lines that exist").

**How to apply:** add new lines at the top under today's date heading; start a new date heading above the older ones on a new day. Check the grammar of each line (both verbs after "Made the music ..." take the same form).
