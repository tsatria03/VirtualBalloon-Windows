---
name: how-the-game-works
description: Virtual Balloon's rules and timings, taken from the original 2009 game's files, and how VirtualBalloon.py copies them
metadata:
  type: project
---

The original (2009, made with GameSalad, an iPhone-only game) keeps its rules in XML files. Timings, in seconds after the key goes down:
- The inflating sound (`balloon_inflate.ogg`, 39.8 s) starts on the press; it was played as GameSalad "music", so it keeps playing across scene changes.
- Squeaks at 16 (center), 26 (left) and 32 (right) seconds - a bluff, nothing happens.
- Let go early: the inflating sound stops, the deflating sound plays, and the seconds held are shown (VirtualBalloon.py speaks them).
- Hold to 39 s: the win screen appears; nothing stops the inflating sound, so **the balloon pops at about 39.1-39.5 s** (the pop is inside the inflating sound's last moments, not a separate file or rule). The crowd cheers 1 s into the win screen (40 s); a new round is accepted only 4 s after the win (43 s).
- The user confirmed the pop by ear at about 38-39 s (2026-10-16). Earlier I wrongly said the balloon never pops: I had read only the rules, not listened to the sound - the audio files are part of the behaviour.
- `music.ogg` is the original's unused `piano.ogg`; in the remake it's the title music.

How VirtualBalloon.py copies it (pygame + accessible_output2):
- `Round` holds the rules and takes the time as a number (testable); `Game` plays sounds and speaks.
- Two reserved channels: one for the music, one for the balloon. `Channel.play` replaces what the channel was playing, so inflating and deflating never overlap.
- Music: loops from the title on, keeps playing between tries, fades to -25 dB while inflating (the user tried -20, then -30, and settled on -25 on 2026-10-16) and back to -10 dB on release (40 dB per second), stops at the win, comes back at the next round.
- Volumes are written in decibels, converted with 10^(dB/20) (the same formula the user's usual game engine uses for its `volume` property).
- Keys: hold Space to inflate, Escape quits.
- Playing again (since 2026-10-16, user: pressing Space to play again "shouldn't imideatly make you blow up the balloon"): after a loss, or 4 s after a win, a Space press goes to the "ready" state ("Ready. Hold Space to blow up the balloon.", music back on); only the next press starts a round, like the original's Try Again button going back to the Start screen. Key presses are handled in `Game.press_space(now)`; pygame's key repeat is off, so holding Space never counts as a second press.

**Why:** these numbers came from the original game files; keep them unless the user asks for a change.
**How to apply:** check new changes against this list, update it when the design changes, and add each change to [[changes-file-style]].
