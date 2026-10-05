import win32api


class Snap:
    def __init__(self, config):
        self.cfg = config
        self.move_x, self.move_y = (0, 0)
        self.previous_x, self.previous_y = (0, 0)
        self.help_offset = 0
        self.focus_state = False
        self.help_state = False

    def toggle_focus(self):
        self.focus_state = not self.focus_state
        if not self.focus_state:
            self.previous_x, self.previous_y = (0, 0)
        print(f"focus: {self.focus_state}")

    def toggle_help(self):
        self.help_state = not self.help_state
        print(f"help: {self.help_state}")

    def get_focus_state(self):
        if not self.focus_state:
            return False
        if self.cfg.focus_keys[0] == 'off':
            return True
        return any(win32api.GetAsyncKeyState(key) < 0 for key in self.cfg.focus_keys)

    def calculate_focus(self, state, target):
        if not state or target is None:
            return

        x, y = target
        x *= self.cfg.speed
        y *= self.cfg.speed * self.cfg.y_speed_multiplier

        x = (1 - self.cfg.focus_smoothing_factor) * self.previous_x + self.cfg.focus_smoothing_factor * x
        y = (1 - self.cfg.focus_smoothing_factor) * self.previous_y + self.cfg.focus_smoothing_factor * y

        self.previous_x, self.previous_y = (x, y)
        self.move_x, self.move_y = (x, y)

    def apply_help(self, state, delta_time):
        if not state or delta_time == 0:
            self.help_offset = 0
            return

        if self.cfg.help_mode == 'move' and win32api.GetAsyncKeyState(0x01) < 0:
            self.move_x += self.cfg.help_x * delta_time
            self.move_y += self.cfg.help_y * delta_time
        elif self.cfg.help_mode == 'offset':
            self._update_help_offset(delta_time)

    def _update_help_offset(self, delta_time):
        mouse1_down = win32api.GetAsyncKeyState(0x01) < 0

        if mouse1_down:
            self.help_offset += self.cfg.help_y * delta_time
            self.help_offset = min(self.help_offset, self.cfg.max_offset)
        else:
            self.help_offset -= self.cfg.help_recover * delta_time
            self.help_offset = max(self.help_offset, 0)
