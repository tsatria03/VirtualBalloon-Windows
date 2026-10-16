---
name: changes-file-style
description: How the user writes docks/changelog.txt: an "unrelease:" heading for changes not yet released, newest first, one sentence per line
metadata:
  type: feedback
---

Every change to the game gets a line in `docks/changelog.txt` (moved into `docks` and renamed from changes.txt by the user on 2026-10-16):
- Keep it small and plain, one sentence per line (user, 2026-10-16: "Nothing too fancy. One centince per line").
- Reverse chronological order: the newest entry at the top, also inside a heading.
- New lines go under the top heading `unrelease:` (the user's own spelling; their releaser script presumably turns it into a release heading - don't rename it). It replaced the earlier YY.MM.DD date heading (`26.10.16`).
- Lines are phrased as changes: "You can now ...", "Made ...", "... now plays ...".

**Why:** the user rewrote my first changes.txt (a "Version 1.0" heading and plain feature lines) into this style on 2026-10-16.
**Small follow-up tweaks** to something already listed (a changed number, a reworded message) edit the existing line instead of adding a new one (user, 2026-10-16: "For the change log, you can just modify one of the lines that exist").

**No secret timings:** the changelog ships with every release, so a line never says when the squeaks come or how long to hold on to win (user, 2026-10-16: "Fix the change log too"); write "moved the win to match" rather than a number.

**How to apply:** add new lines at the top under the `unrelease:` heading (one blank line after it). Check the grammar of each line (both verbs after "Made the music ..." take the same form).
