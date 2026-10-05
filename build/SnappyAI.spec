# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:/Users/root/Desktop/auth_test/build/../app/main.py'],
    pathex=['C:/Users/root/Desktop/auth_test/build/../app'],
    binaries=[],
    datas=[],
    hiddenimports=['core', 'config', 'vision', 'hotkeys', 'win32rt', 'online', 'assist', 'console', 'gui', 'logo', 'provider_logos', 'recordings', 'edsig', 'i18n', 'colorspec', 'build_secrets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SnappyAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='C:/Users/root/Desktop/auth_test/build/../app/version_info.txt',
    icon=['C:/Users/root/Desktop/auth_test/build/../app/icon.ico'],
)
