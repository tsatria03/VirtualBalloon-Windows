"""Virtual Balloon: hold Space to blow up the balloon. Let go too early and it
deflates; hold on until the end and it pops, and the crowd cheers.

A remake of On Beat Limited's 2009 iPhone game, with the same timings.
"""

import os
import time

import pygame
from accessible_output2.outputs.auto import Auto

SOUNDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")

# Timings from the original game, in seconds after the key goes down.
SQUEAKS = [(16, "squeak_center"), (26, "squeak_left"), (32, "squeak_right")]
WIN_AT = 39          # the win screen appears; the inflating sound plays on to the pop
CHEER_AFTER_WIN = 1  # the crowd cheers 1 second into the win screen
RESTART_AFTER_WIN = 4  # keys are ignored this long, so the pop and cheer can finish


def db_to_volume(db):
    """Turns NVGT-style decibels (0 = full, negative = quieter) into pygame's 0.0 to 1.0."""
    return 10 ** (db / 20)


MUSIC_DB = -10         # the music's normal volume
MUSIC_DUCKED_DB = -30  # while you blow up the balloon
DUCK_SPEED = 40        # dB per second, so a 10 dB change takes a quarter of a second


def fade_db(current, target, seconds):
    """Moves current toward target at DUCK_SPEED, without going past it."""
    step = DUCK_SPEED * seconds
    if current < target:
        return min(current + step, target)
    return max(current - step, target)


class Round:
    """One try at holding on, separate from pygame so it can be tested with made-up times."""

    def __init__(self, start):
        self.start = start
        self.squeaks = list(SQUEAKS)
        self.won_at = None
        self.cheered = False

    def update(self, now, holding):
        """Returns what happened since the last call, as a list of event names."""
        events = []
        held = now - self.start
        if self.won_at is None:
            if not holding:
                return ["lost"]
            while self.squeaks and held >= self.squeaks[0][0]:
                events.append(self.squeaks.pop(0)[1])
            if held >= WIN_AT:
                self.won_at = now
                events.append("won")
        elif not self.cheered and now - self.won_at >= CHEER_AFTER_WIN:
            self.cheered = True
            events.append("cheer")
        return events

    def seconds_held(self, now):
        return int(now - self.start)

    def can_restart(self, now):
        return self.won_at is not None and now - self.won_at >= RESTART_AFTER_WIN


class Game:
    def __init__(self):
        pygame.mixer.pre_init(frequency=48000)
        pygame.init()
        pygame.display.set_mode((400, 300))
        pygame.display.set_caption("Virtual Balloon")
        self.speech = Auto()
        self.sounds = {
            name[:-4]: pygame.mixer.Sound(os.path.join(SOUNDS, name))
            for name in os.listdir(SOUNDS) if name.endswith(".ogg")
        }
        self.music_db = MUSIC_DB
        self.music_target_db = MUSIC_DB
        self.sounds["music"].set_volume(db_to_volume(MUSIC_DB))
        # Two channels of their own: the music, and the balloon. Playing a sound on a
        # channel replaces what it was playing, so inflating and deflating never overlap.
        pygame.mixer.set_reserved(2)
        self.music = pygame.mixer.Channel(0)
        self.balloon = pygame.mixer.Channel(1)
        self.round = None
        self.state = "title"

    def say(self, text):
        self.speech.output(text, interrupt=True)

    def play(self, name):
        return self.sounds[name].play()

    def start_music(self):
        if not self.music.get_busy():
            self.music.play(self.sounds["music"], loops=-1)

    def fade_music(self, seconds):
        """Moves the music's volume a little toward its target; called every frame."""
        if self.music_db != self.music_target_db:
            self.music_db = fade_db(self.music_db, self.music_target_db, seconds)
            self.sounds["music"].set_volume(db_to_volume(self.music_db))

    def title(self):
        self.state = "title"
        self.round = None
        self.start_music()
        self.say("Virtual Balloon. Hold Space to blow up the balloon, and don't let go. Escape quits.")

    def ready(self):
        """Back to the start after a try, like the original's Try Again: the next press starts."""
        self.state = "ready"
        self.round = None
        self.start_music()  # it comes back here after a win
        self.say("Ready. Hold Space to blow up the balloon.")

    def press_space(self, now):
        """A new press of Space (holding the key doesn't repeat it)."""
        if self.state in ("title", "ready"):
            self.start_round()
        elif self.state == "lost" or (self.state == "won" and self.round.can_restart(now)):
            self.ready()

    def start_round(self):
        self.start_music()
        self.music_target_db = MUSIC_DUCKED_DB
        self.round = Round(time.monotonic())
        self.balloon.play(self.sounds["balloon_inflate"])
        self.state = "playing"

    def run(self):
        clock = pygame.time.Clock()
        self.play("logo")
        self.say("On Beat presents")
        logo_ends = time.monotonic() + self.sounds["logo"].get_length()
        self.state = "logo"
        while True:
            now = time.monotonic()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_SPACE:
                        self.press_space(now)
            if self.state == "logo" and now >= logo_ends:
                self.title()
            if self.state in ("playing", "won"):
                self.step(now, pygame.key.get_pressed()[pygame.K_SPACE])
            self.fade_music(clock.tick(60) / 1000)

    def step(self, now, holding):
        for event in self.round.update(now, holding or self.state == "won"):
            if event == "lost":
                self.balloon.play(self.sounds["balloon_deflate"])  # replaces the inflating sound
                self.music_target_db = MUSIC_DB
                held = self.round.seconds_held(now)
                self.say(f"You let go after {held} second{'s' if held != 1 else ''}. Press Space to try again.")
                self.state = "lost"
            elif event == "won":
                self.state = "won"  # the inflating sound keeps playing, so the balloon pops
                self.music.stop()
                self.music_target_db = self.music_db = MUSIC_DB  # back to normal for next time
                self.sounds["music"].set_volume(db_to_volume(MUSIC_DB))
            elif event == "cheer":
                self.play("crowd_cheer")
                self.say("Well done! You held on for 40 seconds. Press Space to play again.")
            else:
                self.play(event)


if __name__ == "__main__":
    try:
        Game().run()
    finally:
        pygame.quit()
