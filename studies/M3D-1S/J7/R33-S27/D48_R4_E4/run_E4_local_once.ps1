# Optional OFFLINE user-initiated fallback. No Work, no foreground Blender and no E2/world reads.
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$source = Join-Path $root 'author.py'
$encoded = Join-Path $root 'author.py.zlib.b64'
$expected = 'b32873c16dedc29ac49f6d4c65c1596c6fc0877fb1709de044f5f434f81f6750'
if (-not (Test-Path $source)) {
    if (-not (Test-Path $encoded)) { throw 'Neither plain nor encoded author source is present.' }
    $raw = [Convert]::FromBase64String((Get-Content $encoded -Raw).Trim())
    $python = Get-Command 'python.exe' -ErrorAction SilentlyContinue
    if (-not $python) { throw 'Download the plain author.py from the GitHub workflow or chat ZIP. No installation was attempted.' }
    & $python.Source -c "import base64,zlib,pathlib; p=pathlib.Path(r'$root'); (p/'author.py').write_bytes(zlib.decompress(base64.b64decode((p/'author.py.zlib.b64').read_text())))"
    if ($LASTEXITCODE -ne 0) { throw 'Source decoding failed.' }
}
if ((Get-FileHash $source -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected) { throw 'Author source SHA256 mismatch.' }
$blender = $null
$c = Get-Command blender.exe -ErrorAction SilentlyContinue
if ($c) { $blender = $c.Source }
if (-not $blender) {
    foreach($p in @("$env:ProgramFiles\Blender Foundation\Blender 5.2\blender.exe", "$env:ProgramFiles\Blender Foundation\Blender 5.2.1\blender.exe")) {
        if (Test-Path $p) { $blender = $p; break }
    }
}
if (-not $blender) { throw 'Installed Blender not found. No installation performed.' }
$out = Join-Path $root 'output'
if (Test-Path (Join-Path $out 'E4_R0_WORKING.blend')) { throw 'Existing BLEND refuses overwrite.' }
New-Item -ItemType Directory -Path $out -Force | Out-Null
$args = @('--background','--threads','2','--python',"`"$source`"",'--','--output',"`"$out`"')
$p = Start-Process -FilePath $blender -ArgumentList $args -PassThru -WindowStyle Hidden -RedirectStandardOutput (Join-Path $root 'E4.stdout.txt') -RedirectStandardError (Join-Path $root 'E4.stderr.txt')
try { $p.PriorityClass = 'BelowNormal' } catch { Write-Warning 'Could not lower priority.' }
$p.WaitForExit()
if ($p.ExitCode -ne 0) { throw "Blender returned $($p.ExitCode). ART review is pending." }
Write-Output "R0 NATIVE OUTPUT GENERATED - ART NOT REVIEWED: $out"
