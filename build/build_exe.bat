@echo off
setlocal EnableExtensions EnableDelayedExpansion
REM ---------------------------------------------------------------
REM  Snappy AI - build a standalone Windows .exe with PyInstaller
REM
REM  Finds main.py by itself, so any of these layouts works:
REM      SnappyAI\build_exe.bat        + SnappyAI\*.py         (flat)
REM      SnappyAI\build\build_exe.bat  + SnappyAI\app\*.py     (old)
REM      SnappyAI\build\build_exe.bat  + SnappyAI\*.py
REM  or point it at the sources:  build_exe.bat C:\src\SnappyAI\app
REM
REM  Modes (optional first argument):
REM      (none)  onefile, GUI only, installs the optional backends  [default]
REM      fast    onedir and no pip installs at all - quickest rebuild
REM      debug   console variant named SnappyAI-debug, for start-up failures
REM
REM  Output lands in the project root: SnappyAI.exe
REM  (onedir/fast: SnappyAI\SnappyAI.exe)
REM
REM  Run this ON the Windows machine (double-click, or from cmd).
REM
REM  NOTE: this file must keep Windows (CRLF) line endings. cmd.exe does
REM  not parse a bare-LF batch file reliably.
REM
REM  v8.67 changes:
REM    * the module list matches the current tree - input_backend.py added,
REM      provider_logos.py dropped (its logo moved into logo.py). The old
REM      list failed preflight on EVERY build, and its --hidden-import
REM      provider_logos pointed at a file that no longer exists.
REM    * locates the sources instead of assuming build\ next to app\
REM    * version_info.txt is looked for in the source dir AND the root
REM    * icon.ico is generated from the embedded logo when there is none,
REM      so the exe carries the right icon with no manual step
REM    * dxcam and windows-capture are collected with their data files when
REM      installed - a bare --hidden-import leaves their DLLs behind and the
REM      backend then fails at runtime, silently, inside a --noconsole exe
REM    * license_client.py is deliberately NOT required and NOT bundled: it
REM      is the unused v9 HTTP-API client (CODE_REVIEW.md part D item 5)
REM ---------------------------------------------------------------

REM ---- mode -------------------------------------------------------
set "MODE=onefile"
set "ARG1=%~1"
set "ARG2=%~2"
if /i "%ARG1%"=="fast"    set "MODE=onedir"
if /i "%ARG1%"=="onedir"  set "MODE=onedir"
if /i "%ARG1%"=="debug"   set "MODE=debug"
if /i "%ARG1%"=="console" set "MODE=debug"

REM ---- locate the sources -----------------------------------------
set "HERE=%~dp0"
set "HEREDIR=%HERE:~0,-1%"
set "APP="
if not "%ARG1%"=="" if exist "%ARG1%\main.py" set "APP=%ARG1%"
if not defined APP if not "%ARG2%"=="" if exist "%ARG2%\main.py" set "APP=%ARG2%"
if not defined APP if exist "%HERE%main.py"       set "APP=%HEREDIR%"
if not defined APP if exist "%HERE%..\app\main.py" set "APP=%HERE%..\app"
if not defined APP if exist "%HERE%..\main.py"    set "APP=%HERE%.."
if not defined APP if exist "%HERE%app\main.py"   set "APP=%HERE%app"

if not defined APP (
    echo.
    echo   ERROR: main.py not found. Looked in:
    echo      %HEREDIR%
    echo      %HEREDIR%\..\app
    echo      %HEREDIR%\..
    echo      %HEREDIR%\app
    echo.
    echo   Put this file next to the program's .py files, or in build\
    echo   with the sources in app\, or pass the source folder:
    echo      build_exe.bat C:\path\to\the\python\files
    pause
    exit /b 1
)

for %%I in ("%APP%") do set "APP=%%~fI"
for %%I in ("%APP%") do set "APPBASE=%%~nxI"
for %%I in ("%APP%") do set "APPPARENT=%%~dpI"
set "APPPARENT=%APPPARENT:~0,-1%"
if /i "%APPBASE%"=="app" (set "ROOT=%APPPARENT%") else (set "ROOT=%APP%")

REM ---- where build intermediates go --------------------------------
REM Next to this script, unless this script sits among the sources - then
REM they go into build\ so obj\ and the .spec never land in the source
REM folder or in the archive you ship.
set "BUILDDIR=%HEREDIR%"
if /i "%APP%"=="%HEREDIR%" set "BUILDDIR=%ROOT%\build"
if not exist "%BUILDDIR%" mkdir "%BUILDDIR%" >nul 2>&1

set "EXENAME=SnappyAI"
set "EXE=%ROOT%\SnappyAI.exe"
set "CONSOLE_ARG=--noconsole"
if "%MODE%"=="onedir" set "EXE=%ROOT%\SnappyAI\SnappyAI.exe"
if "%MODE%"=="debug" (
    set "EXENAME=SnappyAI-debug"
    set "EXE=%ROOT%\SnappyAI-debug.exe"
    set "CONSOLE_ARG=--console"
)

echo.
echo   Mode         : %MODE%
echo   Source dir   : %APP%
echo   Project root : %ROOT%
echo   Output       : %EXE%
echo.

REM ---- preflight: every module the program actually imports --------
REM A missing file here is the most common cause of "the exe built fine
REM but does nothing": PyInstaller only bundles what it can find, and a
REM --noconsole build cannot tell you what it could not find.
echo   Checking that the source folder is complete...
set "MISSING="
set "COUNT=0"
for %%M in (
    main core config colorspec build_secrets i18n vision win32rt
    hotkeys recordings online assist input_backend console gui logo edsig
) do (
    set /a COUNT+=1
    if not exist "%APP%\%%M.py" set "MISSING=!MISSING! %%M.py"
)
if defined MISSING (
    echo.
    echo   ERROR: these modules are missing from %APP%:
    for %%M in (%MISSING%) do echo      %%M
    echo.
    echo   Copy ALL of the program's .py files into that folder and rerun.
    echo   input_backend.py is new - a source folder copied from an older
    echo   version will not have it, and the resulting exe dies at start-up.
    echo   provider_logos.py is GONE: do not restore it, its logo now lives
    echo   in logo.py.
    pause
    exit /b 1
)
echo   all !COUNT! required modules present.
if exist "%APP%\license_client.py" (
    echo   license_client.py found but not bundled - it is the unused v9
    echo   HTTP-API client and nothing imports it. Add --hidden-import
    echo   license_client below if you ever wire it up.
)

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
if "%MODE%"=="onedir" goto :fastdeps
echo [2/5] Installing build dependencies...
python -m pip install --upgrade pip pyinstaller numpy mss pillow
if errorlevel 1 (
    echo   ERROR: pip install failed. Check your internet connection,
    echo   or run:  python -m pip --version  to see what is wrong.
    pause
    exit /b 1
)
goto :depsdone

:fastdeps
echo [2/5] Fast mode - skipping every pip install.
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo   PyInstaller is not installed, so even fast mode needs it once:
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo   ERROR: could not install PyInstaller.
        pause
        exit /b 1
    )
)
for %%P in (numpy mss) do (
    python -c "import %%P" >nul 2>&1
    if errorlevel 1 echo   WARNING: %%P is not installed - the build will fail or the exe will not start.
)
:depsdone

REM ---- optional backends -------------------------------------------
REM Attempted automatically; the build carries on without them. Whatever
REM is present gets bundled, whatever is missing falls back at runtime.
set "OPTARGS="
if "%MODE%"=="onedir" goto :optdone

echo.
echo   Optional capture backends - attempted automatically, and the
echo   build carries on without them. Whatever is present gets bundled;
echo   whatever is missing simply falls back to mss at runtime.
python -m pip install dxcam
if errorlevel 1 echo   NOTE: dxcam did not install - fast capture unavailable, mss fallback stays automatic.
python -m pip install windows-capture
if errorlevel 1 echo   NOTE: windows-capture did not install - experimental WGC backend unavailable.
echo.
echo   Optional Server delivery method (websocket HID output) - attempted
echo   automatically like the capture backends above. Without it the
echo   "Server - hardware-level input via websocket" choice falls back to
echo   the standard Windows method at runtime.
python -m pip install websocket-client
if errorlevel 1 echo   NOTE: websocket-client did not install - Server delivery unavailable.

REM Collect data files and DLLs for the optional backends that are really
REM there. --collect-all on a package that is NOT installed aborts the
REM build, so each one is probed first.
python -c "import dxcam" >nul 2>&1
if not errorlevel 1 set OPTARGS=!OPTARGS! --collect-all dxcam
python -c "import windows_capture" >nul 2>&1
if not errorlevel 1 set OPTARGS=!OPTARGS! --collect-all windows_capture
python -c "import websocket" >nul 2>&1
if not errorlevel 1 set OPTARGS=!OPTARGS! --hidden-import websocket
python -c "import PIL" >nul 2>&1
if not errorlevel 1 set OPTARGS=!OPTARGS! --hidden-import PIL --hidden-import PIL.Image --hidden-import PIL.ImageDraw
:optdone

echo.
if "%MODE%"=="debug" (
    echo [3/5] Building SnappyAI-debug.exe WITH a console, so start-up
    echo       failures have somewhere to print...
) else (
    echo [3/5] Building %EXENAME%.exe ^(GUI + login, no console window^)...
)

REM ---- refuse to overwrite a RUNNING exe (the usual "locked" build) --
:unlock
if not exist "%EXE%" goto :unlocked
del /q "%EXE%" >nul 2>&1
if not exist "%EXE%" goto :unlocked
echo.
echo   %EXENAME%.exe is LOCKED - usually because it is still RUNNING.
echo   Close the app window, or end %EXENAME%.exe in Task Manager.
echo   Antivirus can also hold the file briefly.
echo   Press any key to retry...
pause >nul
goto :unlock
:unlocked

REM ---- icon: use one that exists, else write it from logo.ICO_B64 ----
set "ICONFILE="
if exist "%APP%\icon.ico" set "ICONFILE=%APP%\icon.ico"
if not defined ICONFILE if exist "%ROOT%\icon.ico" set "ICONFILE=%ROOT%\icon.ico"
if not defined ICONFILE if exist "%APP%\SnappyAI_logo_16x16.ico" set "ICONFILE=%APP%\SnappyAI_logo_16x16.ico"
if not defined ICONFILE for %%I in ("%APP%\*.ico") do if not defined ICONFILE set "ICONFILE=%%~I"
if defined ICONFILE goto :icondone

echo   no .ico found - writing %ROOT%\icon.ico from the embedded logo...
python -c "import sys,base64;sys.path.insert(0,r'%APP%');import logo;open(r'%ROOT%\icon.ico','wb').write(base64.b64decode(logo.ICO_B64))" >nul 2>&1
if not errorlevel 1 if exist "%ROOT%\icon.ico" set "ICONFILE=%ROOT%\icon.ico"
:icondone

set "ICON_ARG="
if defined ICONFILE set ICON_ARG=--icon "%ICONFILE%"
if defined ICONFILE (echo   icon: %ICONFILE%) else (echo   no icon available - building without one.)

REM ---- version resource: source dir first, then the project root -----
set "VERFILE="
if exist "%APP%\version_info.txt" set "VERFILE=%APP%\version_info.txt"
if not defined VERFILE if exist "%ROOT%\version_info.txt" set "VERFILE=%ROOT%\version_info.txt"
set "VER_ARG="
if defined VERFILE set VER_ARG=--version-file "%VERFILE%"
if defined VERFILE (echo   version resource: %VERFILE%) else (echo   no version_info.txt - Explorer will show PyInstaller defaults.)

REM ---- assemble the argument list, then invoke on ONE physical line --
REM --paths     : main.py imports its siblings by bare name (from core
REM               import ..., from config import ...), so the source folder
REM               must be on PyInstaller's search path.
REM --hidden-import : gui / console / input_backend are imported lazily or
REM               from inside a function, and build_secrets / colorspec /
REM               i18n are only ever reached from inside another module.
REM               Naming all of them explicitly means a refactor cannot
REM               silently drop one from the bundle.
REM --noconfirm : never prompt before replacing the output. Without it a
REM               double-clicked build can sit waiting for a Y you cannot
REM               see, which looks exactly like a hung build.
REM --clean     : drop PyInstaller's cached analysis, so a module you
REM               deleted or renamed cannot survive from a previous build.
REM --distpath  : the exe lands in the project root, not next to this file.
REM --workpath / --specpath : every intermediate stays in BUILDDIR, which
REM               is this script's own folder unless the script sits among
REM               the sources (then it is build\). Neither path is quoted
REM               with a trailing backslash - the C runtime would read that
REM               as an escaped quote.

set "ARGS=--noconfirm --clean --name %EXENAME% %CONSOLE_ARG%"
if not "%MODE%"=="onedir" set "ARGS=%ARGS% --onefile"
if "%MODE%"=="onedir" set "ARGS=%ARGS% --onedir"
set ARGS=%ARGS% --paths "%APP%"
set ARGS=%ARGS% --hidden-import core --hidden-import config --hidden-import vision
set ARGS=%ARGS% --hidden-import hotkeys --hidden-import win32rt --hidden-import input_backend
set ARGS=%ARGS% --hidden-import online --hidden-import assist --hidden-import console
set ARGS=%ARGS% --hidden-import gui --hidden-import logo --hidden-import recordings
set ARGS=%ARGS% --hidden-import i18n --hidden-import colorspec --hidden-import build_secrets
set ARGS=%ARGS% --hidden-import edsig
set ARGS=%ARGS% %OPTARGS% %ICON_ARG% %VER_ARG%
set ARGS=%ARGS% --distpath "%ROOT%"
set ARGS=%ARGS% --workpath "%BUILDDIR%\obj"
set ARGS=%ARGS% --specpath "%BUILDDIR%"

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
if not exist "%EXE%" (
    echo   ERROR: build reported success but %EXENAME%.exe is missing
    echo   from %EXE%
    pause
    exit /b 1
)

if "%MODE%"=="debug" goto :debugdone
echo [4/5] Smoke test - starting the exe and giving it 6 seconds...
REM A --onefile exe unpacks to a temp dir before it runs, so the first
REM launch is slow. If the process is still alive after 6 s it got past
REM imports and start-up; if it died, the debug build will say why.
REM Nothing is clicked and no window is interacted with.
start "" /b "%EXE%"
timeout /t 6 /nobreak >nul
tasklist /fi "imagename eq %EXENAME%.exe" 2>nul | find /i "%EXENAME%.exe" >nul
if errorlevel 1 (
    echo.
    echo   WARNING: %EXENAME%.exe is NOT running - it exited during start-up.
    echo   A dialog should have appeared saying why. If you saw nothing,
    echo   rebuild with:  build_exe.bat debug
    echo.
    echo   Most likely causes, in order:
    echo     1. a source folder copied from an older version, missing
    echo        input_backend.py, colorspec.py or build_secrets.py
    echo     2. antivirus quarantined the exe (--onefile is flagged often;
    echo        try "build_exe.bat fast", which is --onedir, or add an
    echo        exclusion and rebuild)
    echo     3. a build constant missing - see build_secrets.py
    echo     4. another Snappy AI is already running somewhere - the
    echo        single-instance mutex makes this copy exit at once
) else (
    echo   %EXENAME%.exe is running - start-up succeeded.
    taskkill /im %EXENAME%.exe /f >nul 2>&1
)
goto :smokedone

:debugdone
echo [4/5] Debug build - not smoke-testing it, so you can read its output.
echo   Run it yourself and watch the console:
echo      %EXE%
:smokedone

echo.
echo [5/5] Done.
echo.
echo   Your exe:   %EXE%
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
echo   Build intermediates stay in %BUILDDIR%\obj and
echo   %BUILDDIR%\%EXENAME%.spec - safe to delete, and not part of
echo   the source archive.
echo.
echo Capture backends in this build:
if "%MODE%"=="onedir" (
    echo   - fast mode skipped the optional installs; whatever was already
    echo     in your Python is bundled. Run a normal build to add dxcam,
    echo     windows-capture or websocket-client.
) else (
    echo   - dxcam and windows-capture were attempted automatically above
    echo     and collected with their data files when present.
)
echo     dxcam never works over RDP/VMs - the mss fallback stays
echo     automatic either way. Set capture_backend = wgc for the
echo     experimental Windows.Graphics.Capture engine.
echo.
echo Build modes:
echo   build_exe.bat          onefile, no console           ^(the shipped exe^)
echo   build_exe.bat fast     onedir, no pip installs       ^(quickest rebuild,
echo                          fewer antivirus false positives, starts faster^)
echo   build_exe.bat debug    console build for diagnosing a start-up failure
echo.
echo If Windows SmartScreen or antivirus complains, see docs\README-BUILD.md.
echo.
pause
