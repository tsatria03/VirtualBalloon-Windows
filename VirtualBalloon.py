"""Virtual Balloon: hold Space to blow up the balloon. Let go too early and it
deflates; hold on until the end and it pops, and the crowd cheers.

A remake of On Beat Limited's 2009 iPhone game, with the same timings. Entry point; the
game itself is in the virtualballoon package.

    python VirtualBalloon.py
"""
import pygame

from virtualballoon.game import Game


def main():
    try:
        Game().run()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
