import win32api
import time


class Snap:
    # Smoothing time constant in seconds: the EMA weight is derived from
    # the real frame delta, so behavior no longer changes with refresh rate.
    SMOOTH_TAU = 0.05
    # When no target is visible, decay the last move toward zero at this
    # rate (1/s) instead of retaining it - prevents drift-then-freeze.
    DECAY_RATE = 8.0

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

    def calculate_focus(self, state, target, delta_time=0.0):
        """Time-aware smoothing (ported from the main app's approach).

        The old fixed EMA weight made the response depend on frame rate;
        deriving alpha from delta_time keeps feel identical at 60/144 Hz.
        On a lost target the stored move now decays toward zero instead
        of being retained and re-applied when the next blob appears.
        """
        if not state:
            return

        if delta_time <= 0:
            delta_time = 1.0 / 60.0

        if target is None:
            # Decay smoothly to a stop rather than freezing mid-motion.
            k = max(0.0, 1.0 - self.DECAY_RATE * delta_time)
            self.previous_x *= k
            self.previous_y *= k
            self.move_x, self.move_y = self.previous_x, self.previous_y
            return

        x, y = target
        x *= self.cfg.speed
        y *= self.cfg.speed * self.cfg.y_speed_multiplier

        cfg_factor = self.cfg.focus_smoothing_factor
        if cfg_factor > 0:
            tau = -delta_time / (cfg_factor - 1.0)      # map config factor to a time constant
            alpha = 1.0 - pow(2.718281828459045, -delta_time / tau)
        else:
            alpha = 1.0
        alpha = min(max(alpha, 0.0), 1.0)

        x = (1 - alpha) * self.previous_x + alpha * x
        y = (1 - alpha) * self.previous_y + alpha * y

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
