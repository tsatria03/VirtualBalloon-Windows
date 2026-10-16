# VirtualBalloon-Windows

A Windows game in Python, a remake of **Virtual Balloon** (`com.onbeat.balloon` 1.0, On Beat
Limited, 2009), an iPhone game: press and hold, and the balloon starts to inflate, but as soon
as you take your finger off the screen it deflates. Hold on long enough and it pops.

The remake runs on the original app's own files: its sounds, recovered from the iOS app and
converted to Ogg Vorbis, and its rules, read out of the XML scenes and actors the original
was built from with GameSalad. Every timing the game uses comes from those files: the
squeaks, the win, the cheer. It is played with the keyboard and speaks everything through
your screen reader, so it can be played without looking at the screen.

## Download

Releases are published on the
[releases page](https://github.com/tsatria03/VirtualBalloon-Windows/releases). Each release has a
zip, `VirtualBalloon-Win-<version>.zip`: extract it and run `VirtualBalloon.exe` in the
`VirtualBalloon-Windows` folder it contains. A version is
the date of the release and that day's number: `26.10.15-1` is the first release of the
15th of October 2026. The changelog in `docks/changelog.txt` lists what each release
changed.

---

## Requirements

To run it from source: 64-bit Python 3.12 or newer on Windows 10 or later, and two packages:

    pip install -r requirements.txt

| package | what needs it |
|---|---|
| `pygame` | the window, the keyboard, the frame loop and the sound (`virtualballoon/game.py`) |
| `prismatoid` | Prism, which speaks the game's announcements through any screen reader other than NVDA, or through a Windows voice when none is running (`virtualballoon/speech.py`). Without it the game still runs, but only NVDA speaks |

Everything else is the standard library: the settings are kept in the registry with
`winreg`, and NVDA is reached through `ctypes`.

`vendor/nvda/nvdaControllerClient64.dll` ships with the repository, so there is nothing to
install for NVDA. NVDA speaks through its own client; any other screen reader (JAWS, ZDSR,
ZoomText, System Access, PC-Talker, Narrator and more) through Prism; and with none running,
a SAPI 5 or OneCore voice does. A player with NVDA running never loads Prism at all.

## Running it

```bash
python VirtualBalloon.py
```

That plays the On Beat logo and its jingle, as the original does, then the title with its
music. Hold **Space** to blow up the balloon.

The announcements setting is remembered between runs, in the registry under
`HKEY_CURRENT_USER\Software\tsatria03\VirtualBalloon` (the value `Announcements`). The game
never writes anywhere else.

## Controls

| | |
|---|---|
| **Space** | hold to blow up the balloon; press to try again, or to play again after a win |
| **A** | turn the announcements off or on; the game always says which. Does nothing while the logo plays |
| **Esc** | quit |

Keyboard only, no mouse.

## How to play

Hold **Space**, and the balloon fills with air while the music fades out. The game says
"Inflating...". At 16, 26 and 32 seconds it squeaks, from the center, the left and the
right, as if it were about to burst. It is a bluff: keep holding.

- **Let go too soon,** and the air goes out of it for as long as you held on, while the
  music fades back in. The game tells you how many seconds you lasted. Hold Space again to
  try again.
- **Hold on to the end,** about 39 seconds, and you have won: the balloon pops, and a second
  later the crowd cheers. Press Space as soon as the cheer starts to play again.

The balloon inflates for at least 200 ms however quickly you tap, and rests 200 ms after you
let go, so it cannot be spammed.

## Building and releasing

Both scripts are for Windows. Double-click either one, or run it with `py`, and it offers a numbered
menu, then waits for Enter at the end so you can hear how it went.

**`compiler.py`** builds the game with PyInstaller (`pip install pyinstaller`) into
`dist\VirtualBalloon-Windows`, around `VirtualBalloon.exe`:

    py compiler.py                the folder build: the sounds beside the executable
    py compiler.py --test         the folder build, then start it silently for a few seconds to check it works
    py compiler.py --embed        one executable with the sounds inside it
    py compiler.py --clean        empty PyInstaller's cache first
    py compiler.py --console      keep a console window, to see why the game will not start
    py compiler.py --onefile      one executable with the sounds still beside it
    py compiler.py --no-game      leave the sounds out
    py compiler.py --dry-run      say what a build would do, build nothing

The game, the NVDA controller client, Prism and the third-party licenses (in `licenses\`) go inside
the executable. Of `game\`, a build carries only the sounds, the one thing the game reads. Beside the
executable go `docks\changelog.txt`, `VERSION` and `license.txt`. `--test` starts the finished build
for 6 seconds with no window, no sound and no speech, and checks that it quits by itself.

**`releaser.py`** makes a release, asking Y or N before each step: it checks that everything is
committed and pushed and that 5 to 100 changes are waiting under `unrelease:` in the changelog; sets
`VERSION` to today's date and release number and files the changelog under it; builds and tests with
`compiler.py`; zips the build into `dist\VirtualBalloon-Win-<version>.zip`; commits and pushes
`VERSION` and the changelog as "Release <version>"; tags it `V<version>`; and uploads the zip to GitHub
as the release "Virtual Balloon V<version>", with that version's changelog lines as its notes. The
upload needs the [GitHub CLI](https://cli.github.com), signed in with `gh auth login`. Nothing it does
ever moves a tag or replaces a file already on a release.

---

## Layout

```
VirtualBalloon.py        entry point
virtualballoon/
  game.py                the Game class: the sounds, the keys and the announcements
  round.py               one try at holding on: the rules and the original's timings
  audio.py               volumes in decibels, and how the music fades
  speech.py              the game's voice: NVDA, Prism or a Windows voice
  settings.py            the announcements setting, in the registry
  paths.py               where game/ and vendor/ are, also inside a PyInstaller build
game/                    the original app bundle (see below)
vendor/                  NVDA's controller client, with its license
aidocks/general/         the notes for AI-assisted work (see CLAUDE.md)
aidocks/plans/           plans for features and fixes
docks/                   changelog.txt, which ships in a docks folder
compiler.py              builds the game with PyInstaller
releaser.py              sets the version, files the changelog, builds, zips, tags and uploads a release
requirements.txt         the two packages it needs
VERSION                  the release version
```

### `game/` — the original's data

`game/` holds the contents of `Payload/balloon.app` as the IPA shipped them: the `balloon`
binary, the GameSalad engine (`engine32.luo`), `Info.plist`, the icons and
`_CodeSignature/`. The game itself is in `balloon.gameproj/`: five scenes and eight actors as
XML, the images, and the sounds. The remake reads only the sounds; the XML is where its rules
came from.

The sounds are in `game/balloon.gameproj/sounds/`, under new names that say what they are.
The original's two `.m4a` files were converted to Ogg Vorbis like the rest, and two had the
silence at their start trimmed: the inflating sound, which is why the win comes at 38.75
seconds rather than the original's 39, and the left squeak. `music.ogg` is the original's
`piano.ogg`, which the original shipped but never played; here it is the title music.

The App Store license that came with the download (`SC_Info/`) is not part of the
repository.

## Where this came from

The original is made with GameSalad, so the game is not program code but data: each scene
and actor is an XML file of rules, such as "when the touch is pressed, start a 39-second
timer". Reading those files gave every timing the remake uses. The one thing they do not say
is the pop: it is the last moment of the inflating sound itself, which the original plays as
music, so it carries on into the win screen. The remake plays it the same way.

## Status

The whole game is remade: the logo, the title, holding on and letting go, the squeaks, the
pop and the cheer, with the music fading under the balloon and announcements for every
screen.

## Credits

- **[tsatria03](https://github.com/tsatria03)** owns and publishes the repository: recovered
  the original's files, converted and trimmed its sounds, and designed the remake: the
  music fading with the balloon, the deflate that lasts as long as you held on, the
  cooldown, the announcements and their key.
- The speech module comes from **Sixth Sense Reborn**, adapted for this game.

Virtual Balloon itself is On Beat Limited's game, from 2009.

## Licence

The remake's code is in `LICENSE`. Everything under `game/` is On Beat Limited's and is not
covered by it.

The third-party pieces keep their own licenses. NVDA's controller client's sits beside its
DLL in `vendor/nvda/`. Each can also be read online:

- the NVDA controller client, LGPL 2.1: <https://github.com/nvaccess/nvda/blob/master/extras/controllerClient/license.txt>
- Prism, MPL 2.0: <https://github.com/ethindp/prism>
- pygame, LGPL 2.1: <https://github.com/pygame/pygame/blob/main/docs/LGPL.txt>
