@echo off
setlocal
title HALO-9 M3D-0 Blender Environment Check
echo ============================================================
echo HALO-9 M3D-0 / READ-ONLY BLENDER ENVIRONMENT CHECK
echo ============================================================
echo This check does NOT install, update, save, or modify Blender.
echo It does NOT access Minecraft or any project models.
echo.
echo [1/6] Blender running process
powershell.exe -NoProfile -Command "if(Get-Process -Name blender -ErrorAction SilentlyContinue){'RUNNING'}else{'NOT_RUNNING'}"
echo.
echo [2/6] Blender executable detected
where blender.exe >nul 2>&1
if %errorlevel%==0 (echo FOUND_IN_PATH) else (echo NOT_IN_PATH)
if exist "%ProgramFiles%\Blender Foundation\Blender 5.2\blender.exe" (echo BLENDER_5_2_STANDARD_PATH_FOUND) else (echo BLENDER_5_2_STANDARD_PATH_NOT_FOUND)
echo.
echo [3/6] Blender MCP addon in older user addon folders
powershell.exe -NoProfile -Command "$v=@('5.2','5.3','5.4','4.5');foreach($i in $v){$p=Join-Path $env:APPDATA ('Blender Foundation\Blender\'+$i+'\scripts\addons\blender_mcp.py');if(Test-Path -LiteralPath $p){'ADDON_'+$i+'=FOUND'}else{'ADDON_'+$i+'=NOT_FOUND'}}"
echo.
echo [4/6] uvx executable
where uvx.exe >nul 2>&1
if %errorlevel%==0 (echo UVX_FOUND_IN_PATH) else (echo UVX_NOT_IN_PATH)
if exist "%USERPROFILE%\.local\bin\uvx.exe" (echo UVX_USER_LOCAL_FOUND) else (echo UVX_USER_LOCAL_NOT_FOUND)
echo.
echo [5/6] Codex MCP configuration (presence only, no contents printed)
powershell.exe -NoProfile -Command "$p=Join-Path $env:USERPROFILE '.codex\config.toml';if(Test-Path -LiteralPath $p){'CODEX_CONFIG=FOUND';if(Select-String -LiteralPath $p -Pattern 'mcp_servers.blender','blender-mcp','mcp-for-blender' -Quiet){'BLENDER_MCP_REFERENCE=FOUND'}else{'BLENDER_MCP_REFERENCE=NOT_FOUND'}}else{'CODEX_CONFIG=NOT_FOUND'}"
echo.
echo [6/6] Local Blender MCP port 9876 (listener status only)
powershell.exe -NoProfile -Command "$x=Get-NetTCPConnection -LocalPort 9876 -State Listen -ErrorAction SilentlyContinue;if($x){'PORT_9876=LISTENING'}else{'PORT_9876=NOT_LISTENING_OR_NOT_VISIBLE'}"
echo.
echo ============================================================
echo FINISHED. Take a screenshot of the results above.
echo Nothing has been installed or modified.
echo ============================================================
echo.
pause
endlocal
