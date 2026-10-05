import win32api
from time import sleep


class KeybindManager:
    """Handles all keyboard and mouse input state checking."""

    def __init__(self, config):
        self.cfg = config
        self.delay = 0.25

    def check_key_binds(self, assist):
        """Check for reload, toggle, and exit key presses.
        Returns True if the config should be reloaded."""
        if win32api.GetAsyncKeyState(self.cfg.key_reload_config) < 0:
            return True

        if win32api.GetAsyncKeyState(self.cfg.key_toggle_focus) < 0:
            assist.toggle_focus()
            sleep(self.delay)

        if win32api.GetAsyncKeyState(self.cfg.key_toggle_help) < 0:
            assist.toggle_help()
            sleep(self.delay)

        if win32api.GetAsyncKeyState(self.cfg.key_exit) < 0:
            print("Exiting")
            raise SystemExit(0)

        return False

    def get_click_state(self):
        return win32api.GetAsyncKeyState(self.cfg.key_click) < 0

    def get_rapid_click_state(self):
        return win32api.GetAsyncKeyState(self.cfg.key_rapid_click) < 0
