---
name: version-file
description: The VERSION file (e.g. 26.10.15-1) is read by the user's releaser script; its date can differ from changes.txt on purpose - never change it
metadata:
  type: project
---

`VERSION` holds the release version, for example `26.10.15-1`. A releaser script of the user's checks it. It's allowed to differ from the date headings in `docks/changes.txt` (on 2026-10-16 VERSION said 26.10.15-1 while changes.txt said 26.10.16).

**Why:** the user, 2026-10-16: "The version file is different for a reason because a releaser script will check for it. We can discuss that later."
**How to apply:** don't edit VERSION or point out the date difference again; wait until the user brings up the releaser script.
