from configparser import ConfigParser, NoSectionError, NoOptionError
import numpy as np
import os
import sys


DEFAULT_CONFIG = """[communication]
# winapi
type = winapi

[focus]
screen_center_offset = 0
focus_smoothing_factor = 0.5
speed = 1.0
y_speed_multiplier = 1.0
focus_height = 0.5

[screen]
group_close_target_blobs_threshold = 3, 3
# HSV color range of the target
lower_color = 0, 120, 70
upper_color = 10, 255, 255
capture_area_x = 320
capture_area_y = 320
focus_area_x = 100
focus_area_y = 80
max_loops_per_sec = 60
auto_detect_resolution = true
resolution_x = 1920
resolution_y = 1080

[help]
# move | offset
mode = offset
help_x = 0.0
help_y = 30.0
max_offset = 100
recover = 60.0

[click]
click_delay = 60
click_randomization = 40
click_threshold = 4

[rapid_click]
target_cps = 10

[key_binds]
# Hex virtual-key codes (e.g. 01 = left mouse, 02 = right mouse, 10 = SHIFT, 52 = R)
key_reload_config = 72
key_toggle_focus = 46
key_toggle_help = 4D
key_exit = 23
key_click = 01
key_rapid_click = 02
# Comma-separated hex codes, or 'off' to disable hold-to-focus
focus_keys = off

[debug]
enabled = false
always_on = false
# game | mask
display_mode = game
debug_fullscreen_capture = false
"""


def resolve_config_path():
    """Return the config.ini path, working both from source and from a
    PyInstaller exe (where config must sit next to the exe, not in _MEI)."""
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        return os.path.join(exe_dir, 'config.ini')
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, '..', 'config.ini'))


class ConfigReader:
    def __init__(self, path=None):
        self.parser = ConfigParser()

        # Communication
        self.communication_type = 'winapi'

        # Screen
        self.group_close_target_blobs_threshold = (3, 3)
        self.upper_color = np.array([10, 255, 255])
        self.lower_color = np.array([0, 120, 70])
        self.capture_area_x = 320
        self.capture_area_y = 320
        self.focus_area_x = 100
        self.focus_area_y = 80
        self.min_loop_time = 17
        self.auto_detect_resolution = True
        self.resolution_x = 1920
        self.resolution_y = 1080

        # focus
        self.screen_center_offset = 0
        self.focus_smoothing_factor = 0.6
        self.speed = 1.0
        self.y_speed_multiplier = 1.0
        self.focus_height = 0.5

        # help
        self.help_mode = 'offset'
        self.help_x = 0.0
        self.help_y = 30.0
        self.max_offset = 100
        self.help_recover = 60.0

        # click
        self.click_delay = 60
        self.click_randomization = 40
        self.click_threshold = 4

        # Rapid click
        self.target_cps = 10

        # Key binds
        self.key_reload_config = 0x48
        self.key_toggle_focus = 0x46
        self.key_toggle_help = 0x4D
        self.key_exit = 0x23
        self.key_click = 0x01
        self.key_rapid_click = 0x02
        self.focus_keys = ['off']

        # Debug
        self.debug = False
        self.debug_always_on = False
        self.display_mode = 'game'
        self.debug_fullscreen_capture = False

        # Get config path and read it (create a default one if missing)
        self.path = path or resolve_config_path()
        if not os.path.isfile(self.path):
            try:
                os.makedirs(os.path.dirname(self.path), exist_ok=True)
                with open(self.path, 'w', encoding='utf-8') as f:
                    f.write(DEFAULT_CONFIG)
                print(f'Created default config at {self.path}')
            except OSError as e:
                print(f'WARNING: Could not create default config at {self.path}: {e}')
        read = self.parser.read(self.path, encoding='utf-8')
        if not read:
            print(f'WARNING: Could not read config file at {self.path}, using defaults')

    def read_config(self):
        # Reset mutable collections to prevent accumulation on reload
        self.focus_keys = []

        try:
            # Get communication settings
            value = self.parser.get('communication', 'type').lower()
            communication_type_list = ['winapi', 'interception_driver', 'serial', 'socket']
            if value in communication_type_list:
                self.communication_type = value
            else:
                print('WARNING: Invalid communication_type value, keeping previous: '
                      f'{self.communication_type}')

            self.screen_center_offset = self.parser.getint('focus', 'screen_center_offset')

            value = self.parser.getfloat('focus', 'focus_smoothing_factor')
            if 0 <= value <= 1:
                self.focus_smoothing_factor = 1 - value / 1.25
            else:
                print('WARNING: Invalid focus_smoothing_factor value, keeping previous: '
                      f'{self.focus_smoothing_factor}')

            self.speed = self.parser.getfloat('focus', 'speed')
            self.y_speed_multiplier = self.parser.getfloat('focus', 'y_speed_multiplier')

            value = self.parser.getfloat('focus', 'focus_height')
            if 0 <= value <= 1:
                self.focus_height = value
            else:
                print('WARNING: Invalid focus_height value, keeping previous: '
                      f'{self.focus_height}')

            # Get screen settings
            values_str = self.parser.get('screen', 'group_close_target_blobs_threshold').split(',')
            self.group_close_target_blobs_threshold = (int(values_str[0].strip()), int(values_str[1].strip()))

            self.upper_color = self._parse_color_array('screen', 'upper_color')
            self.lower_color = self._parse_color_array('screen', 'lower_color')

            self.capture_area_x = self.parser.getint('screen', 'capture_area_x')
            self.capture_area_y = self.parser.getint('screen', 'capture_area_y')
            self.focus_area_x = self.parser.getint('screen', 'focus_area_x')
            self.focus_area_y = self.parser.getint('screen', 'focus_area_y')
            max_loops_per_sec = self.parser.getint('screen', 'max_loops_per_sec')
            if max_loops_per_sec <= 0:
                print('WARNING: max_loops_per_sec must be > 0, keeping previous min_loop_time')
            else:
                self.min_loop_time = 1000 // max_loops_per_sec + 1

            self.auto_detect_resolution = self.parser.getboolean('screen', 'auto_detect_resolution')

            self.resolution_x = self.parser.getint('screen', 'resolution_x')
            self.resolution_y = self.parser.getint('screen', 'resolution_y')

            # Get help settings
            value = self.parser.get('help', 'mode').lower()
            help_mode_list = ['move', 'offset']
            if value in help_mode_list:
                self.help_mode = value
            else:
                print('WARNING: Invalid help_mode value, keeping previous: '
                      f'{self.help_mode}')

            self.help_x = self.parser.getfloat('help', 'help_x')
            self.help_y = self.parser.getfloat('help', 'help_y')
            self.max_offset = self.parser.getint('help', 'max_offset')
            self.help_recover = self.parser.getfloat('help', 'recover')

            # Get click settings
            self.click_delay = self.parser.getint('click', 'click_delay')
            self.click_randomization = self.parser.getint('click', 'click_randomization')
            self.click_threshold = self.parser.getint('click', 'click_threshold')

            # Get rapid click settings
            target_cps = self.parser.getint('rapid_click', 'target_cps')
            if target_cps <= 0:
                print('WARNING: target_cps must be > 0, keeping previous: '
                      f'{self.target_cps}')
            else:
                self.target_cps = target_cps

            # Get keybind settings
            self.key_reload_config = self.read_hex(self.parser.get('key_binds', 'key_reload_config'))
            self.key_toggle_focus = self.read_hex(self.parser.get('key_binds', 'key_toggle_focus'))
            self.key_toggle_help = self.read_hex(self.parser.get('key_binds', 'key_toggle_help'))
            self.key_exit = self.read_hex(self.parser.get('key_binds', 'key_exit'))
            self.key_click = self.read_hex(self.parser.get('key_binds', 'key_click'))
            self.key_rapid_click = self.read_hex(self.parser.get('key_binds', 'key_rapid_click'))
            focus_keys_str = self.parser.get('key_binds', 'focus_keys').strip()
            if focus_keys_str != 'off':
                for key in focus_keys_str.split(','):
                    key = key.strip()
                    if key:
                        self.focus_keys.append(self.read_hex(key))
                if not self.focus_keys:
                    self.focus_keys = ['off']
            else:
                self.focus_keys = ['off']

            # Get debug settings
            self.debug = self.parser.getboolean('debug', 'enabled')
            self.debug_always_on = self.parser.getboolean('debug', 'always_on')

            value = self.parser.get('debug', 'display_mode').lower()
            display_mode_list = ['game', 'mask']
            if value in display_mode_list:
                self.display_mode = value
            else:
                print('WARNING: Invalid display_mode value, keeping previous: '
                      f'{self.display_mode}')

            self.debug_fullscreen_capture = self.parser.getboolean('debug', 'debug_fullscreen_capture', fallback=False)
        except (NoSectionError, NoOptionError, ValueError) as e:
            raise RuntimeError(f'Invalid config file at {self.path}: {e}') from e

    def _parse_color_array(self, section, option):
        """Parse a comma-separated color string into a numpy integer array."""
        values = self.parser.get(section, option).split(',')
        return np.array([int(v.strip()) for v in values])

    @staticmethod
    def read_hex(string):
        return int(string.strip(), 16)
