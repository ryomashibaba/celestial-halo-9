@echo off
chcp 65001 >nul
cd /d "%~dp0"
python -c "import numpy,trimesh,vtk,PIL,fastapi,uvicorn" >nul 2>&1
if errorlevel 1 (
  echo Required Python packages not installed.
  echo Run: py -m pip install -r D28_requirements.txt
  pause
  exit /b 1
)
python d28_visual_workbench.py --output D28_WORK --port 8768 --open
pause
