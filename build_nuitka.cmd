@echo off
setlocal
cd /d "%~dp0"

rem =====================================================================
rem  SnappyAI release build - Nuitka
rem
rem  Toggles, set in the environment or edited here:
rem    SNAPPYAI_LTO=yes/no/auto  default auto. "yes" inlines across every
rem                               module, which leaves far fewer recognisable
rem                               function boundaries in the exe, but the
rem                               build gets much slower and much hungrier.
rem    SNAPPYAI_ALLOW_MINGW=1    build with MinGW64 even though no MSVC was
rem                               found. Only viable up to Python 3.12.
rem    SNAPPYAI_CERT_SUBJECT     Authenticode: subject name of a certificate
rem                               in your store, or its 40-char thumbprint.
rem    SNAPPYAI_CERT_PFX         ...or a .pfx file to sign with.
rem    SNAPPYAI_CERT_PASSWORD    password for that .pfx.
rem    SNAPPYAI_TIMESTAMP_URL    timestamp authority, default digicert.
rem
rem  Deliberately NOT passed to Nuitka:
rem    --windows-uac-admin       the app starts unelevated on purpose and
rem                               elevates one command at a time through
rem                               ShellExecuteExW "runas"
rem                               (general_utils._elevated_hidden). Running
rem                               the whole session as admin would widen
rem                               every hook, every file write and every
rem                               subprocess it spawns.
rem    static_hashes python-flag that DISABLES hash randomisation, which
rem                               Python turns on to stop collision attacks.
rem    no_annotations python-flag 42 dataclasses read __annotations__ while
rem                               the class is being created; emptying it
rem                               would silently delete every field.
rem    --mode=onefile            ViGEmClient.dll, config.ini and the logs
rem                               folder must live next to the exe the user
rem                               can see. The onefile bootstrap unpacks to
rem                               %TEMP%, so LoadLibrary would no longer
rem                               search the folder the user is looking at.
rem =====================================================================

if not defined SNAPPYAI_LTO set "SNAPPYAI_LTO=auto"

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found on PATH.
    exit /b 1
)

for /f "delims=" %%v in ('python -c "import sys; print(str(sys.version_info[0]) + chr(46) + str(sys.version_info[1]))"') do set "PYVER=%%v"
echo Python %PYVER%

rem --- C compiler ------------------------------------------------------
rem Nuitka refuses MinGW64 on Python 3.13 and newer unless an experimental
rem flag is given, so a missing MSVC is a hard stop with a real answer
rem instead of a cryptic failure ten minutes into the build.
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
set "VS_PATH="
if exist "%VSWHERE%" (
    for /f "usebackq tokens=*" %%i in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VS_PATH=%%i"
)

set "COMPILER_FLAG="
if defined VS_PATH goto have_msvc
if defined SNAPPYAI_ALLOW_MINGW goto no_msvc
echo.
echo No MSVC C++ toolset was found. Python %PYVER% may still be old
echo enough for the MinGW64 fallback (viable up to 3.12; 3.13+ refuses
echo MinGW). Install the build tools once, then run this again:
echo.
echo   winget install Microsoft.VisualStudio.2022.BuildTools --override "--quiet --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
echo.
echo To attempt MinGW64 anyway:  set SNAPPYAI_ALLOW_MINGW=1
exit /b 1

:have_msvc
echo MSVC found: %VS_PATH%
set "COMPILER_FLAG=--msvc=latest"
goto compiler_done

:no_msvc
echo WARNING: no MSVC found - using the MinGW64 fallback as requested.

:compiler_done

rem --- dependencies ----------------------------------------------------
python -c "import numpy" >nul 2>nul
if errorlevel 1 (
    echo Installing numpy...
    python -m pip install numpy
    if errorlevel 1 exit /b 1
)

python -m nuitka --version >nul 2>nul
if errorlevel 1 (
    echo Installing Nuitka...
    python -m pip install nuitka
    if errorlevel 1 exit /b 1
)

for /f "delims=" %%v in ('python -c "import system_core; print(system_core.APP_VERSION)"') do set "VER=%%v"
if not defined VER (
    echo Could not read APP_VERSION from system_core.py
    exit /b 1
)

if not exist build mkdir build

echo.
echo Building SnappyAI %VER%   LTO=%SNAPPYAI_LTO%
echo.

python -m nuitka ^
    --standalone ^
    --deployment ^
    --python-flag=no_asserts,no_docstrings,no_warnings,isolated,safe_path ^
    --noinclude-pydoc-mode=nofollow ^
    --noinclude-unittest-mode=nofollow ^
    --noinclude-pytest-mode=nofollow ^
    --noinclude-setuptools-mode=nofollow ^
    --enable-plugin=tk-inter ^
    --lto=%SNAPPYAI_LTO% %COMPILER_FLAG% ^
    --windows-console-mode=attach ^
    --windows-icon-from-ico=assets\app.ico ^
    --company-name="Snappy AI" ^
    --product-name="Snappy AI" ^
    --file-version=%VER% ^
    --product-version=%VER% ^
    --file-description="Snappy AI - accessibility click helper" ^
    --copyright="Snappy AI - free software, no warranty" ^
    --report=build\compilation-report.xml ^
    --output-filename=SnappyAI.exe ^
    --output-dir=build ^
    --remove-output ^
    --assume-yes-for-downloads ^
    main.py
if errorlevel 1 (
    echo.
    echo BUILD FAILED
    exit /b 1
)

set "DIST="
for /d %%d in (build\*.dist) do set "DIST=%%d"
if not defined DIST (
    echo Nuitka finished but no .dist folder was found under build\
    exit /b 1
)

echo.
echo Distribution: %DIST%

rem --- optional third-party DLL ---------------------------------------
rem Shipping it from vendor\ pins its SHA-256, so input_backend can refuse
rem a ViGEmClient.dll that somebody swapped after the fact.
if not exist vendor\ViGEmClient.dll goto no_vendor
copy /y vendor\ViGEmClient.dll "%DIST%\" >nul
python build_tools.py pin "%DIST%\ViGEmClient.dll"
goto vendor_done

:no_vendor
echo No vendor\ViGEmClient.dll: gamepad output stays unavailable until the
echo user drops that DLL next to SnappyAI.exe. Put it in vendor\ before
echo building to ship it with a SHA-256 pin.

:vendor_done

rem --- integrity manifest, exposure scan, signature -------------------
python build_tools.py manifest "%DIST%"
python build_tools.py scan "%DIST%\SnappyAI.exe"
python build_tools.py sign "%DIST%" --exe SnappyAI.exe

echo.
echo Done: %DIST%\SnappyAI.exe
echo Ship the whole folder. config.ini, the logs folder and ViGEmClient.dll
echo all have to sit next to the exe.
echo A recipient can prove nothing was swapped with:
echo   python build_tools.py verify "%DIST%"

endlocal
