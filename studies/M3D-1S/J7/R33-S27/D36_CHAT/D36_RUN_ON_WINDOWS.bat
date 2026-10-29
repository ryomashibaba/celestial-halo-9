@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "BLENDER_EXE="
for %%B in (blender.exe) do set "BLENDER_EXE=%%~$PATH:B"
if not defined BLENDER_EXE if exist "%ProgramFiles%\Blender Foundation\Blender 5.2\blender.exe" set "BLENDER_EXE=%ProgramFiles%\Blender Foundation\Blender 5.2\blender.exe"
if not defined BLENDER_EXE if exist "%ProgramFiles%\Blender Foundation\Blender 5.3\blender.exe" set "BLENDER_EXE=%ProgramFiles%\Blender Foundation\Blender 5.3\blender.exe"
if not defined BLENDER_EXE (
  echo Blender executable not found in PATH or common installation locations.
  echo Please set BLENDER_EXE manually inside this batch file. No source GLB was modified.
  pause
  exit /b 2
)
set "RESULT_DIR=%~dp0D36_BLENDER_RUN_%RANDOM%%RANDOM%"
if exist "%RESULT_DIR%" (
  echo Output folder already exists. It will NOT be overwritten.
  pause
  exit /b 3
)
echo Using Blender: "%BLENDER_EXE%"
"%BLENDER_EXE%" --background --factory-startup --python-exit-code 12 --python "%~dp0d36_blender_bridge.py" -- "%~dp0D36_EDIT_PLAN.json" "%RESULT_DIR%"
set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" (
  echo Blender verification did NOT pass. Code %ERR%. Review terminal output.
  pause
  exit /b %ERR%
)
if not exist "%RESULT_DIR%\D36_BLENDER_AUDIT.json" exit /b 4
if not exist "%RESULT_DIR%\D36_EDITABLE_SCULPT_STUDY.blend" exit /b 5
"%BLENDER_EXE%" --background --factory-startup --python-exit-code 12 "%RESULT_DIR%\D36_EDITABLE_SCULPT_STUDY.blend" --python "%~dp0d36_blender_verify.py" -- "%~dp0D36_EDIT_PLAN.json" "%RESULT_DIR%"
if errorlevel 1 (echo Blender native reopen validation FAILED. & pause & exit /b 6)
echo Finished. Open the BLEND in the new folder to freely edit the study.
pause
