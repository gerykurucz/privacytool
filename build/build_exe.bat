@echo off
setlocal EnableExtensions EnableDelayedExpansion
REM ---------------------------------------------------------------
REM  Snappy AI - build a standalone Windows .exe with PyInstaller
REM
REM  Layout assumed (this file lives in build\):
REM      SnappyAI\
REM        build\build_exe.bat   <- you are here
REM        app\*.py              <- the program
REM        SnappyAI.exe          <- output lands HERE (project root)
REM
REM  Run this ON the Windows machine (double-click, or from cmd).
REM
REM  NOTE: this file must keep Windows (CRLF) line endings. cmd.exe does
REM  not parse a bare-LF batch file reliably.
REM
REM  v8.49.1 changes:
REM    * preflight now checks for EVERY module the program imports, so a
REM      half-copied app\ fails here with a list instead of producing an
REM      exe that dies on launch
REM    * --noconfirm --clean: no overwrite prompt (which looks like a hang
REM      when you double-click) and no stale analysis cache
REM    * the new build_secrets / colorspec / i18n modules are named as
REM      hidden imports
REM    * a "diagnostic build" option, because --noconsole means a start-up
REM      failure has nowhere to print
REM    * the log-file location is printed at the end
REM ---------------------------------------------------------------

set "ROOT=%~dp0.."
set "APP=%~dp0..\app"

cd /d "%ROOT%"

echo.
echo   Project root : %ROOT%
echo   Source dir   : %APP%
echo   Output       : %ROOT%\SnappyAI.exe
echo.

if not exist "%APP%\main.py" (
    echo   ERROR: %APP%\main.py not found.
    echo   build_exe.bat must sit in the build\ folder of the project,
    echo   with all program modules in app\ next to it.
    pause
    exit /b 1
)

REM ---- preflight: every module the program actually imports ----------
REM A missing file here is the most common cause of "the exe built fine
REM but does nothing": PyInstaller only bundles what it can find, and a
REM --noconsole build cannot tell you what it could not find.
echo   Checking that app\ is complete...
set "MISSING="
for %%M in (
    main snappyai core config colorspec build_secrets i18n vision win32rt
    hotkeys recordings online assist console gui logo provider_logos edsig
) do (
    if not exist "%APP%\%%M.py" set "MISSING=!MISSING! %%M.py"
)
if defined MISSING (
    echo.
    echo   ERROR: these modules are missing from %APP%:
    for %%M in (%MISSING%) do echo      %%M
    echo.
    echo   Copy ALL of the program's .py files into app\ and rerun.
    echo   colorspec.py and build_secrets.py are new in v8.49 - an app\
    echo   folder copied from an earlier version will not have them, and
    echo   the resulting exe dies during start-up.
    pause
    exit /b 1
)
echo   all 18 modules present.

echo.
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo   ERROR: 'python' was not found on PATH.
    echo   Install Python 3 from https://www.python.org/downloads/
    echo   and TICK "Add python.exe to PATH" during setup, then rerun.
    pause
    exit /b 1
)
python --version

echo.
echo [2/5] Installing build dependencies...
python -m pip install --upgrade pip pyinstaller numpy mss pillow
if errorlevel 1 (
    echo   ERROR: pip install failed. Check your internet connection,
    echo   or run:  python -m pip --version  to see what is wrong.
    pause
    exit /b 1
)

echo.
echo   Optional capture backends - attempted automatically, and the
echo   build carries on without them. Whatever is present gets bundled;
echo   whatever is missing simply falls back to mss at runtime.
python -m pip install dxcam
if errorlevel 1 echo   NOTE: dxcam did not install - fast capture unavailable, mss fallback stays automatic.
python -m pip install windows-capture
if errorlevel 1 echo   NOTE: windows-capture did not install - experimental WGC backend unavailable.

echo.
echo [3/5] Building SnappyAI.exe (GUI + login, no console window)...

REM ---- refuse to overwrite a RUNNING exe (the usual "locked" build) ----
:unlock
if not exist "%ROOT%\SnappyAI.exe" goto :unlocked
del /q "%ROOT%\SnappyAI.exe" >nul 2>&1
if not exist "%ROOT%\SnappyAI.exe" goto :unlocked
echo.
echo   SnappyAI.exe is LOCKED - usually because it is still RUNNING.
echo   Close the app window, or end SnappyAI.exe in Task Manager.
echo   Antivirus can also hold the file briefly.
echo   Press any key to retry...
pause >nul
goto :unlock
:unlocked

REM ---- locate an icon: icon.ico, then the logo name, then any .ico ----
set "ICONFILE="
if exist "%APP%\icon.ico" set "ICONFILE=%APP%\icon.ico"
if not defined ICONFILE if exist "%APP%\SnappyAI_logo_16x16.ico" set "ICONFILE=%APP%\SnappyAI_logo_16x16.ico"
if not defined ICONFILE for %%I in ("%APP%\*.ico") do if not defined ICONFILE set "ICONFILE=%%~I"

set "ICON_ARG="
if defined ICONFILE set ICON_ARG=--icon "%ICONFILE%"
if defined ICONFILE echo   icon: %ICONFILE%
if not defined ICONFILE echo   no .ico in app\ - building WITHOUT a custom icon.
if not defined ICONFILE echo   generate one from the embedded logo with:
if not defined ICONFILE echo     python -c "import base64,sys;sys.path.insert(0,r'%APP%');import logo;open(r'%APP%\icon.ico','wb').write(base64.b64decode(logo.ICO_B64))"

set "VER_ARG="
if exist "%APP%\version_info.txt" set VER_ARG=--version-file "%APP%\version_info.txt"
if exist "%APP%\version_info.txt" echo   version resource: %APP%\version_info.txt

REM ---- assemble the argument list, then invoke on ONE physical line ----
REM --paths     : main.py imports its siblings by bare name (from core
REM               import ..., from config import ...), so app\ must be on
REM               PyInstaller's search path.
REM --hidden-import : gui / console / provider_logos are imported lazily or
REM               optionally, and build_secrets / colorspec / i18n are only
REM               ever reached from inside another module. Naming all of
REM               them explicitly means a refactor cannot silently drop one
REM               from the bundle.
REM --noconfirm : never prompt before replacing the output. Without it a
REM               double-clicked build can sit waiting for a Y you cannot
REM               see, which looks exactly like a hung build.
REM --clean     : drop PyInstaller's cached analysis, so a module you
REM               deleted or renamed cannot survive from a previous build.
REM --distpath  : the exe lands in the project root, not in build\.
REM --workpath / --specpath : every intermediate stays inside build\.
REM               (%~dp0. rather than %~dp0 - a quoted trailing backslash
REM               would be read as an escaped quote by the C runtime.)

set "ARGS=--onefile --noconsole --name SnappyAI --noconfirm --clean"
set ARGS=%ARGS% --paths "%APP%"
set ARGS=%ARGS% --hidden-import core --hidden-import config --hidden-import vision
set ARGS=%ARGS% --hidden-import hotkeys --hidden-import win32rt
set ARGS=%ARGS% --hidden-import online --hidden-import assist --hidden-import console
set ARGS=%ARGS% --hidden-import gui --hidden-import logo --hidden-import provider_logos
set ARGS=%ARGS% --hidden-import recordings --hidden-import edsig
set ARGS=%ARGS% --hidden-import i18n --hidden-import colorspec --hidden-import build_secrets
set ARGS=%ARGS% %ICON_ARG% %VER_ARG%
set ARGS=%ARGS% --distpath "%ROOT%"
set ARGS=%ARGS% --workpath "%~dp0obj"
set ARGS=%ARGS% --specpath "%~dp0."

echo.
echo   python -m PyInstaller %ARGS% "%APP%\main.py"
echo.
python -m PyInstaller %ARGS% "%APP%\main.py"
if errorlevel 1 (
    echo.
    echo   ERROR: the build failed - see the PyInstaller messages above.
    pause
    exit /b 1
)

echo.
if not exist "%ROOT%\SnappyAI.exe" (
    echo   ERROR: build reported success but SnappyAI.exe is missing
    echo   from %ROOT%
    pause
    exit /b 1
)

echo [4/5] Smoke test - starting the exe and giving it 6 seconds...
REM A --onefile exe unpacks to a temp dir before it runs, so the first
REM launch is slow. If the process is still alive after 6 s it got past
REM imports and start-up; if it died, the diagnostic build below will say
REM why. Nothing is clicked and no window is interacted with.
start "" /b "%ROOT%\SnappyAI.exe"
timeout /t 6 /nobreak >nul
tasklist /fi "imagename eq SnappyAI.exe" 2>nul | find /i "SnappyAI.exe" >nul
if errorlevel 1 (
    echo.
    echo   WARNING: SnappyAI.exe is NOT running - it exited during start-up.
    echo   A dialog should have appeared saying why. If you saw nothing,
    echo   build the diagnostic variant described below and read its output.
    echo.
    echo   Most likely causes, in order:
    echo     1. an app\ folder copied from an older version, missing
    echo        colorspec.py or build_secrets.py
    echo     2. antivirus quarantined the exe (--onefile is flagged often;
    echo        try --onedir, or add an exclusion and rebuild)
    echo     3. a build constant missing - see build_secrets.py
) else (
    echo   SnappyAI.exe is running - start-up succeeded.
    taskkill /im SnappyAI.exe /f >nul 2>&1
)

echo.
echo [5/5] Done.
echo.
echo   Your exe:   %ROOT%\SnappyAI.exe
echo.
echo   Data files: config.json / config.ini / macros.json are read and
echo               written NEXT TO the exe (i.e. in the project root), or
echo               in %%APPDATA%%\SnappyAI if that folder is read-only.
echo               session.json (the only credential file) always goes to
echo               %%LOCALAPPDATA%%\SnappyAI, so forwarding the exe never
echo               forwards your sign-in.
echo.
echo   LOG FILE:   %%LOCALAPPDATA%%\SnappyAI\logs\snappyai.log
echo               Every start-up, capture-backend, scan and build problem
echo               is written there. When the app misbehaves, that file is
echo               the evidence - it is capped at 512 KB and keeps its tail.
echo.
echo   Build intermediates stay in build\obj\ and build\SnappyAI.spec -
echo   safe to delete, and not part of the source archive.
echo.
echo Capture backends in this build:
echo   - dxcam and windows-capture were attempted automatically above.
echo     dxcam never works over RDP/VMs - the mss fallback stays
echo     automatic either way. Set capture_backend = wgc for the
echo     experimental Windows.Graphics.Capture engine.
echo.
echo IF THE EXE DOES NOT START, build this and read what it prints:
echo   python -m PyInstaller --onefile --console --name SnappyAI-debug --noconfirm --clean --paths "%APP%" --hidden-import i18n --hidden-import colorspec --hidden-import build_secrets --distpath "%ROOT%" --workpath "%~dp0obj" --specpath "%~dp0." "%APP%\main.py"
echo   then:  %ROOT%\SnappyAI-debug.exe
echo A --console build has a real stdout, so every diagnostic line that the
echo shipped --noconsole exe cannot show will appear in that window.
echo.
echo Other variants:
echo   - a folder build (starts faster, far fewer antivirus false positives):
echo       replace --onefile with --onedir; the exe lands in
echo       %ROOT%\SnappyAI\SnappyAI.exe
echo.
echo If Windows SmartScreen or antivirus complains, see docs\README-BUILD.md.
echo.
pause
