---
name: version-file
description: VERSION (e.g. 26.10.15-1) is set only by releaser.py, as YY.MM.DD-N; never edit it by hand
metadata:
  type: project
---

`VERSION` holds the release version, as `YY.MM.DD-N`: the release's date and that day's release number (`26.10.16-1` is the first release on 2026-10-16). `releaser.py` sets it as it releases, counting N from the `V` tags, and `compiler.py` copies it beside the exe; the releaser refuses to zip a build whose VERSION isn't the one being released. Between releases it shows the last release (or, before the first one, the user's placeholder `26.10.15-1`), so it can differ from the dates in the changelog.

**Why:** the user, 2026-10-16: "The version file is different for a reason because a releaser script will check for it." The releaser was built the same day ([[build-and-release]]).
**How to apply:** don't edit VERSION by hand or point out a date difference; only releaser.py changes it.
