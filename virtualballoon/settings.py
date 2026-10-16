"""The game's settings, kept in the Windows registry under the current user (no admin
rights needed): ``HKEY_CURRENT_USER\\Software\\tsatria03\\VirtualBalloon``."""
import winreg

SETTINGS_KEY = r"Software\tsatria03\VirtualBalloon"


def load_setting(name, default):
    """Reads a number saved with save_setting, or returns default if there isn't one."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, SETTINGS_KEY) as key:
            value, kind = winreg.QueryValueEx(key, name)
            return value if kind == winreg.REG_DWORD else default
    except OSError:
        return default


def save_setting(name, value):
    """Saves a number in the registry; a failure only means it isn't remembered."""
    try:
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, SETTINGS_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, int(value))
    except OSError:
        pass
