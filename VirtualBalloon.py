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
WIN_AT = 38.75       # the win screen appears; the inflating sound plays on to the pop
                     # (39 in the original; 0.25 s earlier since the sound's silent start was trimmed)
CHEER_AFTER_WIN = 1  # the crowd cheers 1 second into the win screen
RESTART_AFTER_WIN = 4  # keys are ignored this long, so the pop and cheer can finish
COOLDOWN = 0.2       # the balloon inflates at least this long, and rests this long after you let go
DEFLATE_CUT_FADE_MS = 30  # the deflating sound fades out this quickly when it's cut short


def db_to_volume(db):
    """Turns NVGT-style decibels (0 = full, negative = quieter) into pygame's 0.0 to 1.0."""
    return 10 ** (db / 20)


MUSIC_DB = -10          # the music's normal volume
MUSIC_SILENT_DB = -100  # where it fades to while you blow up the balloon


def fade_db(start_db, end_db, elapsed, length):
    """A steady fade (in dB) from start_db to end_db that takes length seconds.
    The music fades out over the inflating sound, and back in over the deflating one."""
    part = min(elapsed / length, 1)
    return start_db + (end_db - start_db) * part


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
            if not holding and held >= COOLDOWN:  # a quick tap still inflates for COOLDOWN
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
        self.announcements = True  # the A key turns them off and on
        self.sounds = {
            name[:-4]: pygame.mixer.Sound(os.path.join(SOUNDS, name))
            for name in os.listdir(SOUNDS) if name.endswith(".ogg")
        }
        self.music_db = MUSIC_DB
        self.fade_start_db = MUSIC_DB  # where the music was when its current fade began
        self.fade_start = 0.0          # when the fade back in began (after letting go)
        self.lost_at = 0.0             # when you last let go too soon, for the cooldown
        self.deflate_length = 0.0      # how long the deflating sound plays: as long as you held on
        self.deflate_cut = True        # whether that cut has been made
        self.sounds["music"].set_volume(db_to_volume(MUSIC_DB))
        # Two channels of their own: the music, and the balloon. Playing a sound on a
        # channel replaces what it was playing, so inflating and deflating never overlap.
        pygame.mixer.set_reserved(2)
        self.music = pygame.mixer.Channel(0)
        self.balloon = pygame.mixer.Channel(1)
        self.round = None
        self.state = "title"

    def say(self, text):
        if self.announcements:
            self.speech.output(text, interrupt=True)

    def toggle_announcements(self):
        """The A key: turns the game's announcements off or on. The answer is always spoken."""
        self.announcements = not self.announcements
        self.speech.output("Announcements on" if self.announcements else "Announcements off", interrupt=True)

    def play(self, name):
        return self.sounds[name].play()

    def play_balloon(self, name):
        """Plays an inflating or deflating sound on the balloon channel, at full volume.
        A new sound that starts while the channel is fading out stops the fade but keeps
        the volume it had reached (SDL_mixer), so the volume is set back every time."""
        self.balloon.play(self.sounds[name])
        self.balloon.set_volume(1.0)

    def start_music(self):
        if not self.music.get_busy():
            self.music.play(self.sounds["music"], loops=-1)

    def fade_music(self, now, seconds):
        """Sets the music's volume for this frame. While you hold Space it fades out
        over the inflating sound; after you let go it fades back in over the deflating one."""
        if self.state == "playing":
            length = self.sounds["balloon_inflate"].get_length()
            db = fade_db(self.fade_start_db, MUSIC_SILENT_DB, now - self.round.start, length)
        elif self.state == "lost" and self.music_db != MUSIC_DB:
            db = fade_db(self.fade_start_db, MUSIC_DB, now - self.fade_start, self.deflate_length)
        else:
            return
        if db != self.music_db:
            self.music_db = db
            self.sounds["music"].set_volume(db_to_volume(db))

    def title(self):
        self.state = "title"
        self.round = None
        self.start_music()
        self.say("Virtual Balloon. Hold Space to blow up the balloon, and don't let go. "
                 "A turns announcements off or on. Escape quits.")

    def ready(self):
        """Back to the start after a win: the next press starts a new round."""
        self.state = "ready"
        self.round = None
        self.sounds["crowd_cheer"].stop()  # the cheer runs to about 48.7 s, past the 43 s restart
        self.start_music()  # it comes back here after a win
        self.say("Ready. Hold Space to blow up the balloon.")

    def press_space(self, now):
        """A new press of Space (holding the key doesn't repeat it)."""
        if self.state in ("title", "ready"):
            self.start_round()
        elif self.state == "lost":
            self.try_again(now, True)
        elif self.state == "won" and self.round.can_restart(now):
            self.ready()

    def cut_deflate(self, now):
        """Ends the deflating sound once it has played as long as you held on; called every frame."""
        if self.state == "lost" and not self.deflate_cut and now - self.lost_at >= self.deflate_length:
            self.balloon.fadeout(DEFLATE_CUT_FADE_MS)  # a very short fade, so the cut doesn't click
            self.deflate_cut = True

    def try_again(self, now, holding):
        """After letting go too soon, holding Space tries again once the cooldown is over,
        whether you pressed during the cooldown or after it."""
        if holding and now - self.lost_at >= COOLDOWN:
            self.start_round()

    def start_round(self):
        self.start_music()
        self.fade_start_db = self.music_db  # fade from here, even if it's still coming back up
        self.round = Round(time.monotonic())
        self.play_balloon("balloon_inflate")
        self.state = "playing"
        self.say("Inflating...")

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
                    elif event.key == pygame.K_a:
                        self.toggle_announcements()
            if self.state == "logo" and now >= logo_ends:
                self.title()
            holding = pygame.key.get_pressed()[pygame.K_SPACE]
            if self.state in ("playing", "won"):
                self.step(now, holding)
            elif self.state == "lost":
                self.cut_deflate(now)
                self.try_again(now, holding)
            self.fade_music(time.monotonic(), clock.tick(60) / 1000)

    def step(self, now, holding):
        for event in self.round.update(now, holding or self.state == "won"):
            if event == "lost":
                self.play_balloon("balloon_deflate")  # replaces the inflating sound
                full = self.sounds["balloon_deflate"].get_length()
                self.deflate_length = min(now - self.round.start, full)  # as long as you held on
                self.deflate_cut = False
                self.fade_start_db, self.fade_start = self.music_db, now  # fade back in from here
                self.lost_at = now
                held = self.round.seconds_held(now)
                if held == 0:
                    after = "less than a second"
                else:
                    after = f"{held} second{'s' if held != 1 else ''}"
                self.say(f"You let go after {after}. Hold Space to try again.")
                self.state = "lost"
            elif event == "won":
                self.state = "won"  # the inflating sound keeps playing, so the balloon pops
                self.music.stop()
                self.music_db = MUSIC_DB  # back to normal for next time
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
