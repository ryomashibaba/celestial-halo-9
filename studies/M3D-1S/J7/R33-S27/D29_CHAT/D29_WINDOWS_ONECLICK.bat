@echo off
chcp 65001 >nul
cd /d "%~dp0"
python -c "import numpy,trimesh,vtk,PIL,fastapi,uvicorn" >nul 2>&1
if errorlevel 1 (
  echo Required packages are missing. Run: py -m pip install -r D29_requirements.txt
  pause
  exit /b 1
)
python d29_visual_workbench.py --output D29_WORK --port 8769 --open
pause
