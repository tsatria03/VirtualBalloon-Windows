---
name: screen-reader-user
description: The user relies on the NVDA screen reader on Windows; everything must work without sight
metadata:
  type: user
---

The user uses NVDA on Windows. They play and test the game by ear.

**Why:** custom-drawn interfaces (for example tkinter, or a pygame window with drawn text) aren't read by NVDA; only speech and native controls are.
**How to apply:** give every game message through speech (accessible_output2, which speaks through NVDA), never only on screen. If menus or dialogs are ever needed, use native controls (wxPython is installed). Explain keyboard keys in replies.
