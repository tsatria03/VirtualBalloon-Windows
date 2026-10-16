"""Build Virtual Balloon into a Windows program with PyInstaller.

It builds into dist\\VirtualBalloon-Windows, and nothing else: it never zips and never changes the
repository. Setting the version, filing the changelog, zipping, tagging and uploading a release are
releaser.py's work, and the releaser calls this to do the building. Windows only.

Double-click this file, or run py compiler.py with nothing after it, and it offers a numbered menu of
builds, then waits for Enter at the end so you can hear how it went. Each choice is one of these flags,
which still work typed out:

    py compiler.py                the folder build: balloon.gameproj beside the executable
    py compiler.py --test         the folder build, then start it silently for a few seconds to check it works
    py compiler.py --embed        one executable with balloon.gameproj inside it
    py compiler.py --clean        empty PyInstaller's cache first
    py compiler.py --console      keep a console window, to see why the game will not start
    py compiler.py --onefile      one executable with balloon.gameproj still beside it
    py compiler.py --no-game      leave balloon.gameproj out
    py compiler.py --dry-run      say what a build would do, build nothing

Every build lands in dist\\VirtualBalloon-Windows, around VirtualBalloon.exe, with the text a player
reads beside the executable: the changelog in a docks\\ folder, as in the repository, and VERSION and the
license at the top. The third-party licenses go inside the executable, as licenses\\. That folder is
what releaser.py zips into dist\\VirtualBalloon-Win-<VERSION>.zip.

The game and the NVDA controller client always go inside the build. Of the original app bundle in
game\\, a build carries the whole GameSalad project, balloon.gameproj - its scenes, actors, images and
sounds - so a player can look inside it; the game itself reads only the sounds. In the folder build it is
copied beside the executable, into game\\balloon.gameproj, which is where virtualballoon/paths.py looks for
the sounds; with --embed it goes inside the executable instead. The rest of the bundle - the iOS binary,
the engine, the icons, the code signature and the App Store license (SC_Info) - never goes into a build.

--test starts the finished build for a few seconds, silently, with no window and no speech, and checks
that it quits by itself with no error.
"""
from __future__ import annotations

import argparse
import fnmatch
import importlib.machinery
import importlib.metadata
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
#: The executable's name, before .exe.
NAME = 'VirtualBalloon'
ENTRY = 'VirtualBalloon.py'
EXE = NAME + '.exe'
#: The folder a build lands in, and the one a release's zip extracts to.
FOLDER = NAME + '-Windows'
#: What releaser.py calls this system in the zip's name: VirtualBalloon-Win-<version>.zip.
ZIP_SYSTEM = 'Win'

#: What the game cannot run without: the module, and what pip calls it. pygame, not pygame-ce - the two
#: cannot be installed side by side. prismatoid is Prism, which virtualballoon/speech.py speaks through for
#: every screen reader but NVDA, and for the Windows voices; the game starts without it, but then only an
#: NVDA player hears it, so no build leaves it out.
PLAY_PACKAGES = (('pygame', 'pygame'), ('prism', 'prismatoid'))
#: The vendored DLL that goes inside the build, and the folder it goes to there.
BINARIES = (('vendor/nvda/nvdaControllerClient64.dll', 'vendor/nvda'),)
#: Its license, which sits beside it in vendor/: the folder it goes to under licenses/ inside the
#: executable, and the file. Prism's and pygame's are not kept here - they come out of the installed
#: packages when the build runs (license_files()), so they always match what was bundled.
VENDOR_LICENSES = (('nvda-controller-client', ('vendor/nvda/license.txt',)),)
#: What a build carries of the original app bundle: the whole GameSalad project - its scenes, actors,
#: images and sounds - so a player can look inside it (tsatria03, 2026-10-16). The game reads only the
#: sounds. The rest of game\ - the iOS binary, the engine, the icons, the code signature and SC_Info,
#: the App Store license from the user's own download - never goes into a build.
GAMEPROJ = os.path.join('game', 'balloon.gameproj')
SOUNDS = os.path.join(GAMEPROJ, 'sounds')
SOUND_EXTENSIONS = ('.ogg',)
#: Never copied, wherever they are: an App Store license carries its buyer's Apple account's ID.
NEVER_SHIP = ('*.sinf', '*.supp', 'SC_Info')
#: Copied beside the executable rather than bundled inside it, so the player can open them: what it is
#: called here, and what it is called there. LICENSE has no extension, which is the convention on GitHub
#: but means Windows asks what to open it with, so it ships as a .txt.
DOCKS = 'docks'
CHANGELOG = os.path.join(DOCKS, 'changelog.txt')
SIDE_FILES = ((CHANGELOG, CHANGELOG),
              ('VERSION', 'VERSION'),
              ('LICENSE', 'license.txt'))


def say(text: str = '') -> None:
    print(text, flush=True)


def build_version() -> str:
    """What this build calls itself: the one line in VERSION, or '' when there is no such file."""
    try:
        with open(os.path.join(HERE, 'VERSION'), encoding='utf-8') as fh:
            return fh.read().strip().splitlines()[0].strip()
    except (OSError, IndexError):
        return ''


# --- the changelog -----------------------------------------------------------------------------------
# docks\changelog.txt collects what has changed under one heading, "unrelease:", at the top.
# releaser.py files those lines under the version being released before it calls this to build; the
# compiler only reads the changelog, and takes an empty unrelease: heading out of the copy it ships. The
# parsing lives here, where both use it.

#: The heading the changelog collects unreleased changes under: the whole line, colon and all.
UNRELEASE = 'unrelease:'
#: A heading is one word ending in a colon - "unrelease:", "26.10.16-1:". The entries are sentences, so a
#: line with a space in it, colons and all, is never taken for one.
_HEADING = re.compile(r'^[^\s:]+:$')


def changelog_heading(version: str) -> str:
    """'26.10.16-1' -> '26.10.16-1:'. The heading is VERSION exactly as written, build number and all."""
    return version + ':'


def _parse_changelog(text: str) -> list:
    """[[heading, [lines]], ...] in the order of the file. Blank lines only separate one version from
    the next, so they are not kept; anything above the first heading is a block with no heading."""
    blocks = []
    for line in text.replace('\r\n', '\n').split('\n'):
        if _HEADING.match(line.strip()):
            blocks.append([line.strip(), []])
        elif line.strip():
            if not blocks:
                blocks.append([None, []])
            blocks[-1][1].append(line)
    return blocks


def _render_changelog(blocks: list) -> str:
    """A heading, its lines, then one blank line before the next heading, all the way down - so where
    one version's changes end is something you hear, not something you have to work out."""
    return '\n\n'.join('\n'.join(([heading] if heading else []) + lines) for heading, lines in blocks) + '\n'


def unreleased_lines(text: str) -> list:
    """The lines under unrelease:, the changes no release has carried yet."""
    return next((lines for heading, lines in _parse_changelog(text) if heading == UNRELEASE), [])


def without_unrelease(text: str) -> str:
    """The changelog a player reads: the same, less the empty unrelease: heading, so it opens on the
    newest version. A heading that still has lines under it is left alone rather than lose them."""
    return _render_changelog([b for b in _parse_changelog(text) if not (b[0] == UNRELEASE and not b[1])])


def strip_shipped_changelog(dest_root: str) -> None:
    """Take the empty unrelease: heading out of the copy in the build's docks\\ - the copy only."""
    path = os.path.join(dest_root, CHANGELOG)
    if os.path.isfile(path):
        with open(path, encoding='utf-8') as fh:
            text = fh.read()
        with open(path, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(without_unrelease(text))


def release_warnings(changelog: str) -> list:
    """What would make this a bad thing to publish, judged on the changelog the build actually carries."""
    found = []
    if not build_version():
        found.append('there is no VERSION file, so the release has no version to be tagged with, and '
                     'the zip has none in its name')
    try:
        with open(changelog, encoding='utf-8') as fh:
            first = fh.readline().strip()
        if first == UNRELEASE:
            found.append('the changelog in this build still opens with "%s", because only releaser.py '
                         'files the changelog; release with it to put those lines under the version'
                         % UNRELEASE)
    except OSError:
        found.append('there is no changelog.txt, so the release notes would be empty')
    return found


def problems_now() -> list[str]:
    """Everything that would stop the build, in plain words."""
    found = []
    if sys.platform != 'win32':
        found.append('Virtual Balloon builds on Windows only, and this is %s' % sys.platform)
    if sys.maxsize <= 2 ** 32:
        found.append('use 64-bit Python: the NVDA controller client is 64-bit')
    if importlib.util.find_spec('PyInstaller') is None:
        found.append('PyInstaller is not installed in this Python: pip install pyinstaller')
    absent = [pip for mod, pip in PLAY_PACKAGES if importlib.util.find_spec(mod) is None]
    if absent:
        found.append("the game's own packages have to be installed here too, to be bundled: "
                     'pip install ' + ' '.join(absent))
    for src, _ in BINARIES:
        if not os.path.isfile(os.path.join(HERE, src.replace('/', os.sep))):
            found.append('%s is missing - it ships with the repository' % src)
    return found


def prism_native_modules() -> list[str]:
    """Prism's compiled Python module in its prism\\_native folder, which --collect-all leaves behind."""
    spec = importlib.util.find_spec('prism')
    if spec is None or not spec.submodule_search_locations:
        return []
    folder = os.path.join(list(spec.submodule_search_locations)[0], '_native')
    if not os.path.isdir(folder):
        return []
    suffixes = tuple(importlib.machinery.EXTENSION_SUFFIXES)
    return sorted(os.path.join(folder, name) for name in os.listdir(folder) if name.endswith(suffixes))


#: Where every build gathers the third-party licenses, which go inside the executable as licenses\;
#: only the game's own license.txt stays beside it.
LICENSES_STAGE = os.path.join(HERE, 'build', 'embed', 'licenses')


def sound_files() -> list[str]:
    """The sounds, as paths from the repository's top: every .ogg in the sounds folder."""
    folder = os.path.join(HERE, SOUNDS)
    if not os.path.isdir(folder):
        return []
    return [os.path.join(SOUNDS, name) for name in sorted(os.listdir(folder))
            if name.lower().endswith(SOUND_EXTENSIONS)]


def _never_ship(name: str) -> bool:
    return any(fnmatch.fnmatch(name.lower(), pattern.lower()) for pattern in NEVER_SHIP)


def gameproj_files() -> list[str]:
    """Everything a build carries of the app bundle, as paths from the repository's top: every file in
    balloon.gameproj, in its folders, less anything in NEVER_SHIP."""
    found = []
    for dirpath, dirs, files in os.walk(os.path.join(HERE, GAMEPROJ)):
        dirs[:] = sorted(d for d in dirs if not _never_ship(d))
        found += [os.path.relpath(os.path.join(dirpath, name), HERE)
                  for name in sorted(files) if not _never_ship(name)]
    return found


def data_summary(names: list[str]) -> str:
    """What a list of the game's files holds, in words: '42 files - 8 sounds, and 34 scenes, actors and images'."""
    sounds = sum(1 for name in names if name.lower().endswith(SOUND_EXTENSIONS))
    return '%d files - %d sounds, and %d scenes, actors, images and project files' % (
        len(names), sounds, len(names) - sounds)


#: Where --embed gathers balloon.gameproj, less NEVER_SHIP, for PyInstaller to take as one folder.
EMBED_STAGE = os.path.join(HERE, 'build', 'embed', 'balloon.gameproj')


def stage_gameproj() -> None:
    """Copy what --embed carries of balloon.gameproj into EMBED_STAGE, fresh."""
    if os.path.isdir(EMBED_STAGE):
        shutil.rmtree(EMBED_STAGE)
    for name in gameproj_files():
        target = os.path.join(EMBED_STAGE, os.path.relpath(name, GAMEPROJ))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(os.path.join(HERE, name), target)


def command(args) -> list[str]:
    """The PyInstaller command line."""
    cmd = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--noupx', '--name', NAME]
    for src, dest in BINARIES:
        cmd += ['--add-binary', src + os.pathsep + dest]
    # Prism is imported only once NVDA is found not to be running, so it is named outright rather than left
    # for the analysis to find. It loads its compiled half from a folder of its own, prism\_native:
    # --collect-all brings the DLL there but not the Python module beside it, because the folder is not a
    # package, so that is added by name - and it needs cffi's own compiled module, which nothing names either
    cmd += ['--collect-all', 'prism', '--hidden-import', '_cffi_backend']
    for src in prism_native_modules():
        cmd += ['--add-binary', src + os.pathsep + 'prism/_native']
    if not args.console:
        # no console window beside the game's own; a failure is said aloud in one line
        cmd += ['--windowed']
    if args.onefile or args.embed:
        # one file lands in dist\VirtualBalloon-Windows too, so every build is one folder to zip
        cmd += ['--onefile', '--distpath', output_dir()]
    if args.embed and not args.no_game:
        cmd += ['--add-data', EMBED_STAGE + os.pathsep + GAMEPROJ.replace(os.sep, '/')]
    # the third-party licenses go inside, whichever kind of build (stage_licenses fills the folder)
    cmd += ['--add-data', LICENSES_STAGE + os.pathsep + 'licenses']
    if args.clean:
        cmd += ['--clean']
    return cmd + [ENTRY]


def output_dir() -> str:
    """Where the executable lands, and so where everything beside it goes: dist\\VirtualBalloon-Windows."""
    return os.path.join(HERE, 'dist', FOLDER)


def pyinstaller_dir() -> str:
    """Where a folder build's PyInstaller puts it, named after the executable: dist\\VirtualBalloon. It is
    moved to output_dir() once built."""
    return os.path.join(HERE, 'dist', NAME)


def clear_output(dest_root: str) -> None:
    """Empty dist\\VirtualBalloon-Windows before a build, and dist\\VirtualBalloon, where a folder build first
    lands. A one-file build only writes its executable, and would leave an older build's files around it."""
    for folder in (dest_root, pyinstaller_dir()):
        if os.path.isdir(folder):
            shutil.rmtree(folder)


def move_folder_build(dest_root: str) -> None:
    """A folder build is made in dist\\VirtualBalloon; move it to dist\\VirtualBalloon-Windows."""
    built = pyinstaller_dir()
    if os.path.normcase(built) != os.path.normcase(dest_root) and os.path.isdir(built):
        os.replace(built, dest_root)


def copy_gameproj(dest_root: str) -> bool:
    """The folder build's balloon.gameproj, beside the executable in game\\balloon.gameproj."""
    names = gameproj_files()
    if not sound_files():
        say("  the sounds were not found in %s, so nothing was copied." % SOUNDS)
        return False
    say('copying %s into %s ...' % (data_summary(names), os.path.join(dest_root, GAMEPROJ)))
    for name in names:
        target = os.path.join(dest_root, name)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(os.path.join(HERE, name), target)
    return True


def copy_side_files(dest_root: str) -> None:
    """The text the player reads, next to the game rather than inside it: docks\\ as a folder, and
    VERSION and the license at the top."""
    for name, shipped_as in SIDE_FILES:
        src = os.path.join(HERE, name)
        if not os.path.isfile(src):
            say('  %s is not here, so it was not copied.' % name)
            continue
        target = os.path.join(dest_root, shipped_as)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(src, target)
        say('%s is in the build%s.' % (shipped_as, '' if shipped_as == name else ', from %s' % name))


def license_files() -> list[tuple[str, str]]:
    """Every third-party license a release carries: (where it goes under licenses\\, where it comes from).

    The NVDA client's license sits beside it in vendor\\. Prism's come out of its installed package's
    dist-info, and pygame's LGPL out of pygame's installed package, so a build always carries the licenses
    of exactly what it bundled. A file with no extension gets .txt, so Windows opens it."""
    found = []
    for folder, sources in VENDOR_LICENSES:
        for src in sources:
            found.append((os.path.join(folder, os.path.basename(src)),
                          os.path.join(HERE, src.replace('/', os.sep))))
    try:
        dist = importlib.metadata.distribution('prismatoid')
        for entry in dist.files or ():
            parts = entry.parts
            if len(parts) > 2 and parts[0].endswith('.dist-info') and parts[1] == 'licenses':
                rel = os.path.join('prism', *parts[2:])
                if not os.path.splitext(rel)[1]:
                    rel += '.txt'
                found.append((rel, str(dist.locate_file(entry))))
    except importlib.metadata.PackageNotFoundError:
        found.append((os.path.join('prism', 'LICENSE.txt'), ''))      # reported as missing
    spec = importlib.util.find_spec('pygame')
    folder = list(spec.submodule_search_locations)[0] if spec and spec.submodule_search_locations else ''
    found.append((os.path.join('pygame', 'LGPL.txt'),
                  os.path.join(folder, 'docs', 'generated', 'LGPL.txt') if folder else ''))
    return found


def stage_licenses(dest: str = None) -> int:
    """The third-party licenses, gathered fresh into LICENSES_STAGE for PyInstaller to put inside the
    executable as licenses\\. Returns how many."""
    dest = dest or LICENSES_STAGE
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    copied = 0
    for rel, src in license_files():
        if not src or not os.path.isfile(src):
            say('  the license %s was not found, so it was not copied.' % rel)
            continue
        target = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(src, target)
        copied += 1
    say('%d license files - the NVDA controller client, Prism and pygame - go inside the executable, '
        'as licenses%s.' % (copied, os.sep))
    return copied


# --- the test build ----------------------------------------------------------------------------------
# --test starts the build it has just made, for TEST_SECONDS: silent, with no sound device, no window and
# no speech, so it never speaks, plays or shows anything. It only reads the game's settings, never
# writes them.

#: How long the build plays before its --exit-after quits it.
TEST_SECONDS = 6
#: Long enough for a single exe to unpack itself and start, and then some.
TEST_TIMEOUT = 120
TEST_QUIET = {'VIRTUALBALLOON_SILENT': '1', 'SDL_AUDIODRIVER': 'dummy', 'SDL_VIDEODRIVER': 'dummy'}


def test_build(exe: str) -> bool:
    """Start the build for TEST_SECONDS, silently, and say whether it quit by itself with no error."""
    if not os.path.isfile(exe):
        say('the test cannot start: there is no %s' % exe)
        return False
    say('testing the build: starting it for %d seconds, silently...' % TEST_SECONDS)
    env = dict(os.environ, **TEST_QUIET)
    started = time.perf_counter()
    try:
        proc = subprocess.run([exe, '--exit-after', str(TEST_SECONDS)], env=env, cwd=os.path.dirname(exe),
                              timeout=TEST_TIMEOUT, capture_output=True, text=True)
        code, errors = proc.returncode, (proc.stderr or '').strip()
    except subprocess.TimeoutExpired:
        code, errors = None, ''
    except OSError as error:
        say('the test could not start the game: %s' % error)
        return False
    if code == 0:
        say('the test build worked: it started, ran for %d seconds and quit by itself, in %.0f seconds.'
            % (TEST_SECONDS, time.perf_counter() - started))
        return True
    say('the test build FAILED:')
    if code is None:
        say('  the game was still running after %d seconds and was stopped' % TEST_TIMEOUT)
    else:
        say('  the game ended with exit code %s' % code)
    if errors:
        say('  what it said: ' + errors.splitlines()[-1])
    return False


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog='compiler.py', description='build Virtual Balloon with PyInstaller')
    parser.add_argument('--embed', action='store_true',
                        help='one executable with balloon.gameproj inside it; the text a player reads stays beside it')
    parser.add_argument('--onefile', action='store_true', help='one executable, with balloon.gameproj still beside it')
    parser.add_argument('--no-game', action='store_true', help='leave balloon.gameproj out')
    parser.add_argument('--console', action='store_true',
                        help='keep a console window, where a failed start-up prints its traceback')
    parser.add_argument('--clean', action='store_true', help="throw away PyInstaller's cache first")
    parser.add_argument('--dry-run', action='store_true', help='print what would be done, build nothing')
    parser.add_argument('--test', action='store_true',
                        help='after building, start the build for a few seconds, silently, to check it works')
    args = parser.parse_args(argv)
    if args.test and args.no_game:
        say('--test needs balloon.gameproj in the build, so it cannot go with --no-game.')
        return 2
    os.chdir(HERE)                                      # the paths above are relative to the project

    found = problems_now()
    if found:
        say('this would stop the build:' if args.dry_run else 'the build cannot start:')
        for problem in found:
            say('  ' + problem)
        if not args.dry_run:
            return 2
        say()

    dest_root = output_dir()
    sounds = [] if args.no_game else sound_files()
    if args.embed and not sounds and not args.no_game:
        say('--embed puts balloon.gameproj inside the executable, and its sounds were not found in %s.' % SOUNDS)
        if not args.dry_run:
            return 2

    cmd = command(args)
    say('running: python ' + ' '.join(cmd[1:]))
    if args.dry_run:
        if args.no_game:
            say('balloon.gameproj would be left out.')
        elif args.embed:
            say('balloon.gameproj would go inside the executable: %s, and nothing else from the app bundle.'
                % data_summary(gameproj_files()))
        else:
            say('balloon.gameproj would then be copied into %s: %s, and nothing else from the app bundle.'
                % (os.path.join(dest_root, GAMEPROJ), data_summary(gameproj_files())))
        for name, shipped_as in SIDE_FILES:
            say('%s would be copied into the build%s%s'
                % (name, '' if shipped_as == name else ', as %s' % shipped_as,
                   '' if os.path.isfile(os.path.join(HERE, name)) else ' - but it is not here'))
        licenses = license_files()
        absent = [rel for rel, lic in licenses if not lic or not os.path.isfile(lic)]
        say('%d license files would go inside the executable, as licenses%s'
            % (len(licenses) - len(absent), os.sep))
        for rel in absent:
            say('  but the license %s is not here' % rel)
        for warning in release_warnings(os.path.join(HERE, CHANGELOG)):
            say('before releasing: ' + warning)
        if args.test:
            say('then %s would be started for %d seconds, silently, to check it works'
                % (os.path.join(dest_root, EXE), TEST_SECONDS))
        return 0

    stage_licenses()
    if args.embed and sounds:
        stage_gameproj()
    clear_output(dest_root)
    started = time.perf_counter()
    if subprocess.run(cmd).returncode != 0:
        say('PyInstaller failed - its own output above says why.')
        return 1
    say('built in %.0f seconds.' % (time.perf_counter() - started))
    if not (args.onefile or args.embed):
        move_folder_build(dest_root)

    if sounds and not args.embed:
        copy_gameproj(dest_root)
    elif sounds:
        say('balloon.gameproj is inside the executable: %s.' % data_summary(gameproj_files()))
    copy_side_files(dest_root)
    strip_shipped_changelog(dest_root)

    for warning in release_warnings(os.path.join(dest_root, CHANGELOG)):
        say('before releasing: ' + warning)

    exe = os.path.join(dest_root, EXE)
    say()
    say('the game is %s' % exe)
    say("the folder around it is what releaser.py zips, and balloon.gameproj in it is On Beat Limited's.")
    if args.test:
        say()
        if not test_build(exe):
            return 1
    return 0


# --- the menu ----------------------------------------------------------------------------------------
# Double-click compiler.py, or run it with nothing after it, and it asks rather than expects you to know
# the flags. Each choice is exactly one of the command lines above, so the two can never disagree.

MENU = (
    ('Folder build: the game in a folder, with balloon.gameproj beside the executable', []),
    ('Folder build and test: the folder build, then start it silently for a few seconds to check it works',
     ['--test']),
    ('Single exe: balloon.gameproj inside one executable', ['--embed']),
    ('Single exe and test: the single exe, then start it silently for a few seconds to check it works',
     ['--embed', '--test']),
    ("Clean build: empty PyInstaller's cache first, for when a build behaves oddly", ['--clean']),
    ('Build with a console window, to see why the game will not start', ['--console']),
    ('One-file build: a single executable, with balloon.gameproj still beside it', ['--onefile']),
    ('Build without balloon.gameproj', ['--no-game']),
    ('Show what a build would do, without building anything', ['--dry-run']),
)


def menu() -> list | None:
    """Ask which build. Returns the flags for it, or None to quit."""
    version = build_version()
    say('Virtual Balloon compiler. VERSION is %s.' % (version or 'missing - releaser.py sets it as it releases'))
    say()
    for number, (text, _flags) in enumerate(MENU, 1):
        say('  %d. %s' % (number, text))
    say('  0. Quit')
    say()
    while True:
        try:
            choice = input('Type a number and press Enter: ').strip()
        except EOFError:
            return None
        if choice == '0':
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(MENU):
            text, flags = MENU[int(choice) - 1]
            say('%s.' % text.split(':')[0])
            say()
            return list(flags)
        say('There is no choice "%s". Type a number from 0 to %d.' % (choice, len(MENU)))


def run(argv=None) -> int:
    """Flags on the command line build straight away. No flags with a keyboard at the other end - a
    double-click in Explorer, or py compiler.py typed on its own - opens the menu, and the window waits at
    the end so what happened can be heard before it closes. With no keyboard at all, no flags is the
    folder build."""
    argv = sys.argv[1:] if argv is None else argv
    if argv or not sys.stdin.isatty():
        return main(argv)
    chosen = menu()
    if chosen is None:
        return 0
    try:
        return main(chosen)
    finally:
        say()
        try:
            input('Finished. Press Enter to close this window.')
        except EOFError:
            pass


if __name__ == '__main__':
    sys.exit(run())
