@echo off
REM ============================================================
REM  Build AtomicPhysicsLecture.exe (offline, single file)
REM ============================================================
setlocal

echo [1/3] Ensuring PyInstaller is installed...
python -m pip install --quiet --upgrade pyinstaller || goto :error

echo [2/3] Building executable...
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name AtomicPhysicsLecture ^
  main.py || goto :error

echo [3/3] Copying editable resources next to the .exe...
if not exist "dist\lang" mkdir "dist\lang"
copy /Y "lang\en.json" "dist\lang\" >nul
copy /Y "config.json"  "dist\"      >nul

echo.
echo Done.  Your program is at:  dist\AtomicPhysicsLecture.exe
echo (The dist\lang folder and dist\config.json can be edited any time.)
goto :eof

:error
echo.
echo Build FAILED. See the messages above.
exit /b 1
