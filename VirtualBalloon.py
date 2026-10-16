"""Virtual Balloon: hold Space to blow up the balloon. Let go too early and it
deflates; hold on until the end and it pops, and the crowd cheers.

A remake of On Beat Limited's 2009 iPhone game, with the same timings. Entry point; the
game itself is in the virtualballoon package.

    python VirtualBalloon.py
    python VirtualBalloon.py --exit-after 6     quit by itself after 6 seconds (the build test)
"""
import argparse
import sys
import time
import traceback


def _say_why(text):
    """A build has no console, so a failure is said aloud too, through the screen reader or a
    Windows voice - the game's own sound may be what failed."""
    print(text, file=sys.stderr)
    try:
        from virtualballoon.speech import Speech
        if Speech().speak(text):
            time.sleep(min(15.0, 2.0 + 0.07 * len(text)))   # a voice stops when we exit
    except Exception:
        pass


def main(argv=None):
    parser = argparse.ArgumentParser(prog="VirtualBalloon", description="Virtual Balloon")
    parser.add_argument("--exit-after", type=float, metavar="SECONDS",
                        help="quit by itself after this many seconds (for testing a build)")
    args = parser.parse_args(argv)
    import pygame
    from virtualballoon.game import Game
    try:
        Game().run(exit_after=args.exit_after)
    finally:
        pygame.quit()
    return 0


def run():
    try:
        return main()
    except SystemExit:
        raise
    except Exception as error:
        traceback.print_exc()
        _say_why("Virtual Balloon stopped because of an error. %s: %s" % (type(error).__name__, error))
        return 1


if __name__ == "__main__":
    sys.exit(run())
