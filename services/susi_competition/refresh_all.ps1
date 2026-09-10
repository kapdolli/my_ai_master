# 4단계 통합 갱신 스크립트 (로컬 실행 전용)
# 실행 후 자동으로 git add — auto-commit 프로세스가 push 하면 GitHub Actions 가 Pages 배포.
#
# 사용:
#   .\refresh_all.ps1               # 기본 (git add 까지)
#   .\refresh_all.ps1 -NoStage      # git add 생략
#   .\refresh_all.ps1 -Push         # 변경분 커밋 + push (→ Actions 가 Pages 배포)
#
# 이 파일은 반드시 UTF-8 **with BOM** 으로 저장할 것.
# BOM 이 없으면 Windows PowerShell 5.1 이 CP949 로 읽어 아래 한글 인자
# (--regions 서울 …)가 깨지고 수집 대상이 0개 대학이 된다.
#
# 스케줄러 등록 예 (관리자 PowerShell, SusiRefresh 작업):
#   $a = New-ScheduledTaskAction -Execute "powershell.exe" `
#     -Argument "-NoProfile -ExecutionPolicy Bypass -File C:\Users\elf17\work\myai\my_ai_master\services\susi_competition\refresh_all.ps1 -Push"
#   $t = New-ScheduledTaskTrigger -Once -At (Get-Date) `
#     -RepetitionInterval (New-TimeSpan -Minutes 10)
#   Register-ScheduledTask -TaskName "SusiRefresh" -Action $a -Trigger $t

param([switch]$NoStage, [switch]$Push)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$env:PYTHONIOENCODING = "utf-8"

Write-Host "[1/4] 전체 데이터 refresh (~15초, 131개 대학)..." -ForegroundColor Cyan
python -X utf8 .\find_low_competition.py `
  --regions 서울 경기 인천 충남 충북 대전 세종 `
  --max-rate 999 --top 1 --refresh

Write-Host "[2/4] 농특/논술 전 전형 수집 (경쟁률 컷 없음)..." -ForegroundColor Cyan
# 경쟁률 컷은 두지 않는다 — 페이지의 '경쟁률 ≤' 입력으로 화면에서 조절한다.
# (컷을 2.0 으로 두면 건국대(서울)처럼 최저 경쟁률이 높은 대학이 통째로 빠진다)
python -X utf8 .\find_low_competition.py `
  --regions 서울 경기 충남 충북 대전 세종 `
  --admission-contains 농어촌 농특 논술 `
  --top 50 `
  --csv .\susi_2027_nong_nonsul_low.csv

Write-Host "[3/4] 제외규칙 + 주요대학(상위50)·전형 태그..." -ForegroundColor Cyan
python -X utf8 .\filter_top50.py

Write-Host "[4/4] HTML 생성..." -ForegroundColor Cyan
python -X utf8 .\build_html.py

$outputs = @("susi_2027_top50.html", "version.json",
             "susi_2027_low_competition.csv",
             "susi_2027_nong_nonsul_low.csv", "susi_2027_top50_nong_nonsul.csv")

if (-not $NoStage) {
    Write-Host "git add ..." -ForegroundColor Cyan
    git add $outputs
}

if ($Push) {
    $dirty = git diff --cached --name-only -- $outputs
    if ($dirty) {
        $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Host "git commit + push ..." -ForegroundColor Cyan
        git commit -m "susi: auto-refresh at $stamp"
        git push origin main
    } else {
        Write-Host "변경 없음 — push 생략" -ForegroundColor DarkGray
    }
}

Write-Host "완료: $here\susi_2027_top50.html" -ForegroundColor Green
Write-Host "→ auto-commit 이 push 하면 https://kapdolli.github.io/my_ai_master/ 에 배포" -ForegroundColor Green
