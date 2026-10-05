import time
import random

from assist import Snap
from configReader import ConfigReader
from keybinds import KeybindManager
from mouse import get_mouse_implementation
from screen import Screen


class SnappyAI:
    RETRY_DELAY = 5.0

    def run(self):
        self.print_license()
        while True:
            # Track delta time
            start_time = time.perf_counter()

            try:
                config = ConfigReader()
                config.read_config()
            except RuntimeError as e:
                print(f'{e}\nRetrying in {self.RETRY_DELAY:g}s...')
                time.sleep(self.RETRY_DELAY)
                continue

            keybinds = KeybindManager(config)
            assist = Snap(config)
            try:
                mouse = get_mouse_implementation(config)
                screen = Screen(config)
            except Exception as e:
                # e.g. ConnectionError (board unreachable), RuntimeError
                # (bad config / no capture backend), COMError (dxcam init)
                print(f'{e}\nRetrying in {self.RETRY_DELAY:g}s...')
                time.sleep(self.RETRY_DELAY)
                continue

            print('SnappyAI ON')
            last_frame_error = None
            last_frame_error_time = 0.0

            try:
                # assist loop
                while True:
                    now = time.perf_counter()
                    delta_time = now - start_time
                    start_time = now

                    reload_config = keybinds.check_key_binds(assist)
                    if reload_config:
                        break

                    if self._should_process_frame(keybinds, assist, config):
                        try:
                            target, click = screen.get_target(assist.help_offset)
                        except Exception as e:
                            # Transient capture failure: skip the frame instead
                            # of crashing (errors are throttled to avoid log spam).
                            now_err = time.perf_counter()
                            if now_err - last_frame_error_time > 5.0 or repr(e) != last_frame_error:
                                print(f'WARNING: frame skipped (capture error): {e}')
                                last_frame_error = repr(e)
                                last_frame_error_time = now_err
                            continue

                        if keybinds.get_click_state() and click:
                            delay_before_click = self._calculate_click_delay(config)
                            mouse.click(delay_before_click)

                        assist.calculate_focus(assist.get_focus_state(), target)

                    if keybinds.get_rapid_click_state():
                        mouse.click()

                    # Apply help
                    assist.apply_help(assist.help_state, delta_time)

                    # Move the mouse based on the previous calculations
                    if assist.move_x != 0 or assist.move_y != 0:
                        mouse.move(assist.move_x, assist.move_y)

                    # Reset move values so the focus doesn't keep drifting when no targets are on the screen
                    assist.move_x, assist.move_y = (0, 0)

                    # Do not loop above the set refresh rate
                    time_spent = (time.perf_counter() - start_time) * 1000
                    if time_spent < config.min_loop_time:
                        time.sleep((config.min_loop_time - time_spent) / 1000)
            finally:
                screen.close()
                mouse.close()
            print('Reloading')

    def _should_process_frame(self, keybinds, assist, config):
        """Returns True if the frame should be processed for target detection."""
        if keybinds.get_click_state() or assist.get_focus_state():
            return True
        if config.debug and config.debug_always_on:
            return True
        return False

    def _calculate_click_delay(self, config):
        """Calculate the randomized delay before a click."""
        if config.click_delay == 0:
            return 0
        return (random.randint(0, max(config.click_randomization - 1, 0)) + config.click_delay) / 1000

    def print_license(self):
        print('')
