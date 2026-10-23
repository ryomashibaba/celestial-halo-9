param([string]$BlenderPath='C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
$ErrorActionPreference='Stop'
foreach ($concept in @('A','B')) {
    & $BlenderPath --background --factory-startup --python-exit-code 1 --python (Join-Path $PSScriptRoot 'build_scene.py') -- --concept $concept
    if ($LASTEXITCODE -ne 0) { throw "Massing generation failed: $concept" }
}
& $BlenderPath --background --factory-startup --python-exit-code 1 --python (Join-Path $PSScriptRoot 'audit_saved.py')
if ($LASTEXITCODE -ne 0) { throw 'Saved BLEND audit failed' }
python (Join-Path $PSScriptRoot 'assemble_review.py')
if ($LASTEXITCODE -ne 0) { throw 'Review assembly failed' }
