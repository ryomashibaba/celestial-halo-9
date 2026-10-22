param([string]$BlenderPath='C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
$ErrorActionPreference='Stop'
foreach ($concept in @('N1','N2','N3','OLD','OLD1')) {
    $views='01_FRONT,02_OBLIQUE,03_SIDE,04_TOP,05_REAR,06_INTERIOR'
    if ($concept -eq 'N3') { $views+=',07_HIGH_CITY' }
    if ($concept.StartsWith('OLD')) { $views='01_FRONT,02_OBLIQUE' }
    & $BlenderPath --background --factory-startup --python-exit-code 1 --python (Join-Path $PSScriptRoot 'build_study.py') -- --concept $concept --views $views
    if ($LASTEXITCODE -ne 0) { throw "Build failed: $concept" }
}
& $BlenderPath --background --factory-startup --python-exit-code 1 --python (Join-Path $PSScriptRoot 'audit_exports.py')
if ($LASTEXITCODE -ne 0) { throw 'GLB reload audit failed' }
python (Join-Path $PSScriptRoot 'assemble_review.py')
if ($LASTEXITCODE -ne 0) { throw 'Evidence validation failed' }
