# 4단계 통합 갱신 스크립트 (로컬 실행 전용)
# 실행 후 자동으로 git add — auto-commit 프로세스가 push 하면 GitHub Actions 가 Pages 배포.
#
# 사용:
#   .\refresh_all.ps1               # 기본
#   .\refresh_all.ps1 -NoStage      # git add 생략
#
# 스케줄러 등록 예 (관리자 PowerShell):
#   $a = New-ScheduledTaskAction -Execute "powershell.exe" `
#     -Argument "-NoProfile -File D:\MyBench\work\my_ai_master\services\susi_competition\refresh_all.ps1"
#   $t = New-ScheduledTaskTrigger -Once -At (Get-Date) `
#     -RepetitionInterval (New-TimeSpan -Minutes 15)
#   Register-ScheduledTask -TaskName "SusiRefresh" -Action $a -Trigger $t

param([switch]$NoStage)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$env:PYTHONIOENCODING = "utf-8"

Write-Host "[1/4] 전체 데이터 refresh (~15초, 131개 대학)..." -ForegroundColor Cyan
python -X utf8 .\find_low_competition.py `
  --regions 서울 경기 인천 충남 충북 대전 세종 `
  --max-rate 999 --top 1 --refresh

Write-Host "[2/4] 농특/논술 <2.0 필터..." -ForegroundColor Cyan
python -X utf8 .\find_low_competition.py `
  --regions 서울 경기 충남 충북 대전 세종 `
  --admission-contains 농어촌 농특 논술 `
  --max-rate 2.0 --top 800 `
  --csv .\susi_2027_nong_nonsul_low.csv

Write-Host "[3/4] top50 대학 필터 + 태그..." -ForegroundColor Cyan
python -X utf8 .\filter_top50.py

Write-Host "[4/4] HTML 생성..." -ForegroundColor Cyan
python -X utf8 .\build_html.py

if (-not $NoStage) {
    Write-Host "git add ..." -ForegroundColor Cyan
    git add susi_2027_top50.html susi_2027_low_competition.csv `
        susi_2027_nong_nonsul_low.csv susi_2027_top50_nong_nonsul.csv 2>$null
}

Write-Host "완료: $here\susi_2027_top50.html" -ForegroundColor Green
Write-Host "→ auto-commit 이 push 하면 https://kapdolli.github.io/my_ai_master/ 에 배포" -ForegroundColor Green
