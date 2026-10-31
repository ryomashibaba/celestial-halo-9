# R4-E0 background Blender Windows launcher (no foreground Computer Use).
# Scope: new lab folder only. No elevated privileges, no installs, no old city assets.
$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot 'r4_bg_probe.py'
if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) { throw 'Missing adjacent r4_bg_probe.py' }
$exe = $null
$cmd = Get-Command blender -ErrorAction SilentlyContinue
if ($cmd -and (Test-Path -LiteralPath $cmd.Source -PathType Leaf)) { $exe = $cmd.Source }
if (-not $exe) {
    $blenderRoot = Join-Path $env:ProgramFiles 'Blender Foundation'
    if (Test-Path -LiteralPath $blenderRoot) {
        $candidates = @(Get-ChildItem -LiteralPath $blenderRoot -Filter blender.exe -Recurse -File -ErrorAction SilentlyContinue | Sort-Object FullName -Descending)
        if ($candidates.Count -gt 0) { $exe = $candidates[0].FullName }
    }
}
if (-not $exe) { throw 'BLENDER_NOT_FOUND: no installation or configuration attempted' }

$base = Join-Path $env:LOCALAPPDATA 'CelestialHalo9\R4BackgroundProbe'
New-Item -ItemType Directory -Path $base -Force | Out-Null
$folder = Join-Path $base (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
$stdoutPath = Join-Path $base 'probe_stdout.log'
$stderrPath = Join-Path $base 'probe_stderr.log'
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $exe
$psi.Arguments = ('--background --factory-startup --disable-autoexec --threads 2 --python "{0}" -- --outdir "{1}"' -f $scriptPath, $folder)
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true
$psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.WorkingDirectory = $base
$process = [System.Diagnostics.Process]::Start($psi)
try { $process.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::BelowNormal } catch { }
try {
    $outTask = $process.StandardOutput.ReadToEndAsync()
    $errTask = $process.StandardError.ReadToEndAsync()
    if (-not $process.WaitForExit(120000)) {
        $process.Kill()
        throw 'PROBE_TIMEOUT: child process stopped; no automatic retry'
    }
    [System.IO.File]::WriteAllText($stdoutPath, $outTask.Result)
    [System.IO.File]::WriteAllText($stderrPath, $errTask.Result)
    if ($process.ExitCode -ne 0) { throw ('PROBE_FAILED_EXIT_' + $process.ExitCode) }
    $report = Join-Path $folder 'report.json'
    if (-not (Test-Path -LiteralPath $report)) { throw 'PROBE_REPORT_MISSING' }
    $data = Get-Content -LiteralPath $report -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($data.status -ne 'LOCAL_BACKGROUND_TEST_PASS_NOT_ART_PASS' -or -not $data.headless) { throw 'PROBE_INVALID_RESULT' }
    Write-Output ('R4_BG_PROBE_PASS_NOT_ART: ' + $report)
} finally {
    $process.Dispose()
}
