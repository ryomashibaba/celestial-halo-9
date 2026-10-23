param([string]$BlenderPath='C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
$ErrorActionPreference='Stop'
foreach ($candidate in @('A','B','C')) {
    & $BlenderPath --background --factory-startup --python-exit-code 1 --python (Join-Path $PSScriptRoot 'build_scene.py') -- --candidate $candidate --views '02_OBLIQUE,01_FRONT'
    if ($LASTEXITCODE -ne 0) { throw "Macro build failed: $candidate" }
}
& $BlenderPath --background --factory-startup --python-exit-code 1 --python (Join-Path $PSScriptRoot 'build_scene.py') -- --candidate C --detail --views '00_CITY,01_FRONT,02_OBLIQUE,03_SIDE,04_REAR,05_TOP,06_GROUND_A,07_HIGH_B,08_HALL,09_SECTION,10_ALLEY'
if ($LASTEXITCODE -ne 0) { throw 'C build failed' }
& $BlenderPath --background --factory-startup --python-exit-code 1 --python (Join-Path $PSScriptRoot 'frame_views.py') -- '07_HIGH_B,08_HALL,10_ALLEY'
if ($LASTEXITCODE -ne 0) { throw 'Inspection framing failed' }
& $BlenderPath --background --factory-startup --python-exit-code 1 --python (Join-Path $PSScriptRoot 'audit_meshes.py')
if ($LASTEXITCODE -ne 0) { throw 'Reload audit failed' }
python (Join-Path $PSScriptRoot 'assemble_review.py')
if ($LASTEXITCODE -ne 0) { throw 'Evidence assembly failed' }
