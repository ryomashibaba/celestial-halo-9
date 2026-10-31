@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_background_probe_v2.ps1"
if errorlevel 1 (
  echo E1B test did not pass. Do not retry automatically.
  pause
  exit /b 1
)
echo E1B test completed. This is NOT an art-quality PASS.
pause
