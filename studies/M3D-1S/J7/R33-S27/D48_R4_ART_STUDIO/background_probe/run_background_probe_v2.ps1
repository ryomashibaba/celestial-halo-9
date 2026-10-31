# Run ONLY with user-approved local Work/Codex/terminal. No desktop-control tools.
$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot 'r4_bg_probe_v2.py'
if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) { throw 'PROBE_SCRIPT_MISSING' }
$exe = $null
$cmd = Get-Command blender -ErrorAction SilentlyContinue
if ($cmd -and (Test-Path -LiteralPath $cmd.Source -PathType Leaf)) { $exe = $cmd.Source }
if (-not $exe) {
    $root = Join-Path $env:ProgramFiles 'Blender Foundation'
    if (Test-Path -LiteralPath $root) {
        $candidates = @(Get-ChildItem -LiteralPath $root -Filter blender.exe -Recurse -File -ErrorAction SilentlyContinue | Sort-Object FullName -Descending)
        if ($candidates.Count -gt 0) { $exe = $candidates[0].FullName }
    }
}
if (-not $exe) { throw 'BLENDER_NOT_FOUND: no download or installation attempted' }
$base = Join-Path $env:LOCALAPPDATA 'CelestialHalo9\R4BackgroundProbe'
[System.IO.Directory]::CreateDirectory($base) | Out-Null
$stamp = [Guid]::NewGuid().ToString('N')
$out = Join-Path $base ('test_' + $stamp)
$stdoutPath = Join-Path $base ('test_' + $stamp + '.stdout.log')
$stderrPath = Join-Path $base ('test_' + $stamp + '.stderr.log')
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $exe
$psi.Arguments = ('--background --factory-startup --disable-autoexec --threads 2 --python "{0}" -- --outdir "{1}"' -f $scriptPath, $out)
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true
$psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.WorkingDirectory = $base
$p = [System.Diagnostics.Process]::Start($psi)
if ($null -eq $p) { throw 'BLENDER_PROCESS_NOT_CREATED' }
try {
    try { $p.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::BelowNormal } catch { }
    $stdoutTask = $p.StandardOutput.ReadToEndAsync()
    $stderrTask = $p.StandardError.ReadToEndAsync()
    if (-not $p.WaitForExit(120000)) {
        $p.Kill()
        $p.WaitForExit()
        throw 'PROBE_TIMEOUT: Blender stopped without retry'
    }
    [System.IO.File]::WriteAllText($stdoutPath, $stdoutTask.Result)
    [System.IO.File]::WriteAllText($stderrPath, $stderrTask.Result)
    if ($p.ExitCode -ne 0) { throw ('PROBE_EXIT_' + $p.ExitCode + '; inspect ' + $stderrPath) }
    $reportPath = Join-Path $out 'report.json'
    if (-not (Test-Path -LiteralPath $reportPath -PathType Leaf)) { throw 'NO_REPORT' }
    $result = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($result.status -ne 'E1B_NATIVE_IO_PROBE_PASS_NOT_ART' -or -not $result.headless) { throw 'INVALID_REPORT' }
    # Package only these disposable generated assets; never read personal or canonical files.
    $bundle = Join-Path $PSScriptRoot ('E1B_Result_' + $stamp + '.zip')
    $items = @(
        (Join-Path $out 'report.json'),
        (Join-Path $out 'before.blend'), (Join-Path $out 'after.blend'),
        (Join-Path $out 'before.png'), (Join-Path $out 'after.png')
    )
    foreach ($item in $items) {
        if (-not (Test-Path -LiteralPath $item -PathType Leaf)) { throw ('BUNDLE_INPUT_MISSING: ' + $item) }
    }
    Compress-Archive -LiteralPath $items -DestinationPath $bundle -CompressionLevel Optimal
    if (-not (Test-Path -LiteralPath $bundle -PathType Leaf)) { throw 'RESULT_BUNDLE_MISSING' }
    Write-Output ('E1B_RESULT_READY_TO_SHARE: ' + $bundle)
    Write-Output ('PROBE_PASS_NOT_ART: ' + $reportPath)
} finally {
    $p.Dispose()
}
