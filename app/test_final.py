import sys
sys.path.insert(0, '.')

# Test key imports
from assist import start_app, App
from config import Config, DEFAULT_CONFIG
from vision import scan_region
from colorspec import parse_accent, parse_accents
from input_backend import make_input_backend
from gamepad import read, normalise_axis
from hotkeys import _parse_hotkey, effective_mode_key
from recordings import RecordingStore
from license_client import LicenseError
from online import redact_url
import gui
import console
import i18n
import main
import core
import build_secrets
import win32rt
import logo

print('All imports OK')

# Test parse_accents
print('parse_accents("off"):', parse_accents("off"))
print('parse_accents("red"):', parse_accents("red"))
print('parse_accents([60, 120, 220]):', parse_accents([60, 120, 220]))
print('parse_accents("60,120,220"):', parse_accents("60,120,220"))
print('parse_accents("60.0,120.0,220.0"):', parse_accents("60.0,120.0,220.0"))

# Test config
cfg = Config()
print('Config radius:', cfg.get('radius'))
print('Config mode:', cfg.get('mode'))

# Test scan_region
import numpy as np
warm = np.full((64, 64, 3), 128, dtype=np.uint8)
result = scan_region(warm, 32, 32, cfg.values, 50)
print('scan_region result:', result.kind)

# Test redact_url
print('redact_url:', redact_url('https://example.com?prefilled_email=test@test.com&client_reference_id=foo'))

print('All tests passed!')