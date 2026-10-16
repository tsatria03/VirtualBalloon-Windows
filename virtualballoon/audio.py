"""Volumes in decibels, and how the music fades."""

MUSIC_DB = -10          # the music's normal volume
MUSIC_SILENT_DB = -100  # where it fades to while you blow up the balloon
DEFLATE_CUT_FADE_MS = 30  # the deflating sound fades out this quickly when it's cut short


def db_to_volume(db):
    """Turns decibels (0 = full, negative = quieter) into pygame's 0.0 to 1.0."""
    return 10 ** (db / 20)


def fade_db(start_db, end_db, elapsed, length):
    """A steady fade (in dB) from start_db to end_db that takes length seconds.
    The music fades out over the inflating sound, and back in over the deflating one."""
    part = min(elapsed / length, 1)
    return start_db + (end_db - start_db) * part
