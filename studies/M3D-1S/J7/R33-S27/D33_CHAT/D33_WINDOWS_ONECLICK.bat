@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul || (echo Python is required. & pause & exit /b 1)
python -c "import trimesh,numpy,scipy,fastapi,uvicorn,plotly,vtk,PIL" >nul 2>nul || (echo Dependencies missing. Run: python -m pip install -r D33_requirements.txt & pause & exit /b 1)
if not exist "D33_BASE_ART_STUDY.glb" python d33_sculpt.py
if not exist "plotly.min.js" python d33_setup_vendor.py
python d33_visual_editor.py --port 8843
pause
