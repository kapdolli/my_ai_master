# 아이디어검색가 일일 실행 래퍼 — 작업 스케줄러 `idea-search-agent` 가 이 파일을 부른다.
#
# pythonw.exe 를 스케줄러에 직접 등록하면 실패 출력이 어디에도 남지 않아
# 서비스가 조용히 죽어도 알아챌 수 없다. 이 래퍼는 stdout/stderr 를 파일로 남기고
# 실행 종료 코드를 logs/_runs.log 에 한 줄씩 누적한다.
#
# Usage:
#   .\run_daily.ps1            # 정상 실행 (텔레그램 발송까지)
#   .\run_daily.ps1 -DryRun    # 리포트만 생성, 발송 생략

param([switch] $DryRun)

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Split-Path -Parent (Split-Path -Parent $here)

# 스케줄러 세션에서는 PATH 가 다를 수 있으므로 절대경로로 고정한다.
$py = 'C:\Users\elf17\AppData\Local\Programs\Python\Python310\python.exe'
$env:CLAUDE_BIN = 'C:\Users\elf17\.local\bin\claude.exe'
$env:PYTHONIOENCODING = 'utf-8'

$logDir = Join-Path $here 'logs'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$outFile = Join-Path $logDir '_last_run.out.txt'
$errFile = Join-Path $logDir '_last_run.err.txt'
$runLog  = Join-Path $logDir '_runs.log'

$argList = @((Join-Path $here 'run_local.py'))
if ($DryRun) { $argList += '--dry-run' }

$start = Get-Date
$proc = Start-Process -FilePath $py -ArgumentList $argList -WorkingDirectory $repo `
    -NoNewWindow -Wait -PassThru `
    -RedirectStandardOutput $outFile -RedirectStandardError $errFile
$code = $proc.ExitCode
$secs = [int]((Get-Date) - $start).TotalSeconds

$status = if ($code -eq 0) { 'OK' } else { 'FAIL' }
"{0} {1} exit={2} {3}s" -f $start.ToString('yyyy-MM-dd HH:mm:ss'), $status, $code, $secs |
    Add-Content -Path $runLog -Encoding utf8

Get-Content $outFile -ErrorAction SilentlyContinue
if ($code -ne 0) {
    Write-Host "[fail] exit=$code — stderr:"
    Get-Content $errFile -ErrorAction SilentlyContinue
}
exit $code
