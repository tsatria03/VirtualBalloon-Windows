---
name: game-workings
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
- **The remake's win is at 38.75 s, not 39** (2026-10-16): the user trimmed 0.25 s of silence from the start of `balloon_inflate.ogg` (39.82 -> 39.57 s), which moved the pop to about 38.8-39.3 s, so `WIN_AT` moved 0.25 s earlier to keep the pop just after the win. Cheer at 39.75 s, restart from 42.75 s. If the sound's start is edited again, move `WIN_AT` by the same amount (or tie the win to the sound's end - option 2, not chosen). Pop found by bytes per tenth of a second (scratchpad `ogg-burst.py`), confirmed earlier by the user's ear.

How VirtualBalloon.py copies it (pygame + accessible_output2):
- `Round` holds the rules and takes the time as a number (testable); `Game` plays sounds and speaks.
- Two reserved channels: one for the music, one for the balloon. `Channel.play` replaces what the channel was playing, so inflating and deflating never overlap.
- Music: loops from the title on, at **full volume, 0 dB** (`MUSIC_DB`; it was -10 dB until the user changed it on 2026-10-16), and keeps playing between tries. It stops at the win and comes back at the next round.
- While you hold Space, the music fades out steadily (in dB) from where it was to -100 dB over the inflating sound's length (pygame reads it as 39.55 s), so it's gone by the pop (about -98 dB at the 39 s win). When you let go, it fades steadily back in from where it was to 0 dB over the deflating sound's length (6.29 s in pygame), however deep it was (user: "based on the length of the balloon deflate sound"). Pressing again mid-way starts the fade-out from the current level, so there's no jump. Functions: `fade_db(start_db, end_db, elapsed, length)` and `Game.fade_music(now, seconds)`. This is the user's "brand new strategy" of 2026-10-16; before that the music ducked to a fixed level (-20, -30, then -25 dB).
- Volumes are written in decibels, converted with 10^(dB/20) (the same formula the user's usual game engine uses for its `volume` property).
- Keys: hold Space to inflate, Escape quits.
- Playing again (since 2026-10-16, user: pressing Space to play again "shouldn't imideatly make you blow up the balloon"): 4 s after a WIN, a Space press goes to the "ready" state ("Ready. Hold Space to blow up the balloon.", music back on), and only the next press starts a round. After a LOSS there is no Ready step: the next press starts a new try at once (user: Ready "should only occur after winning, not after you release too soon"). Key presses are handled in `Game.press_space(now)`; pygame's key repeat is off, so holding Space never counts as a second press.

**Why:** these numbers came from the original game files; keep them unless the user asks for a change.
**How to apply:** check new changes against this list, update it when the design changes, and add each change to [[changes-file-style]].
