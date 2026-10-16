"""One try at holding on: the rules and timings, separate from pygame so they can be
tested with made-up times."""

# Timings from the original game, in seconds after the key goes down.
SQUEAKS = [(16, "squeak_center"), (26, "squeak_left"), (32, "squeak_right")]
WIN_AT = 38.75       # the win screen appears; the inflating sound plays on to the pop
                     # (39 in the original; 0.25 s earlier since the sound's silent start was trimmed)
CHEER_AFTER_WIN = 1  # the crowd cheers 1 second into the win screen; Space works again from then on
COOLDOWN = 0.2       # the balloon inflates at least this long, and rests this long after you let go


class Round:
    """One try at holding on."""

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
        """After a win, Space works again once the cheer has started (the pop is over by then)."""
        return self.cheered
