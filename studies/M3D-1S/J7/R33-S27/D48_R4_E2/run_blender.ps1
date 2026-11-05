param([string]$Mode='initial',[string]$Stage='R0')
$ErrorActionPreference='Stop'
$exe='C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$psi=[System.Diagnostics.ProcessStartInfo]::new()
$psi.FileName=$exe
$psi.Arguments="--background --factory-startup --disable-autoexec --threads 2 --python `"$PSScriptRoot\atelier.py`" -- $Mode $Stage"
$psi.WorkingDirectory=$PSScriptRoot
$psi.UseShellExecute=$false
$psi.CreateNoWindow=$true
$psi.WindowStyle=[System.Diagnostics.ProcessWindowStyle]::Hidden
$psi.RedirectStandardOutput=$true
$psi.RedirectStandardError=$true
$psi.Environment['PYTHONDONTWRITEBYTECODE']='1'
$psi.Environment['PYTHONUTF8']='1'
$psi.Environment['OMP_NUM_THREADS']='2'
$p=[System.Diagnostics.Process]::Start($psi)
$p.PriorityClass=[System.Diagnostics.ProcessPriorityClass]::BelowNormal
$stdout=$p.StandardOutput.ReadToEndAsync()
$stderr=$p.StandardError.ReadToEndAsync()
$peak=0L;$samples=@()
while(-not $p.WaitForExit(5000)) {
 $p.Refresh();$peak=[Math]::Max($peak,$p.WorkingSet64)
 $samples+=@{elapsed_s=[Math]::Round(((Get-Date)-$p.StartTime).TotalSeconds,1);cpu_s=$p.TotalProcessorTime.TotalSeconds;ram_mb=[Math]::Round($p.WorkingSet64/1MB,1);priority=$p.PriorityClass.ToString()}
}
[IO.File]::WriteAllText("$PSScriptRoot\${Mode}_${Stage}.log",$stdout.Result)
[IO.File]::WriteAllText("$PSScriptRoot\${Mode}_${Stage}.stderr.log",$stderr.Result)
@{exit_code=$p.ExitCode;peak_sampled_ram_mb=[Math]::Round($peak/1MB,1);cpu_threads=2;device='CPU';priority='BelowNormal';samples=$samples} | ConvertTo-Json -Depth 5 | Set-Content "$PSScriptRoot\${Mode}_${Stage}_resources.json" -Encoding utf8
Write-Output "BLENDER_EXIT=$($p.ExitCode) MODE=$Mode STAGE=$Stage PEAK_SAMPLED_RAM_MB=$([Math]::Round($peak/1MB,1))"
Get-Content "$PSScriptRoot\${Mode}_${Stage}.stderr.log"
exit $p.ExitCode
