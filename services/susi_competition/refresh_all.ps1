# 4단계 통합 갱신 스크립트 (로컬/CI 공용)
# 사용: PowerShell 에서 실행
#   .\refresh_all.ps1
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$env:PYTHONIOENCODING = "utf-8"
Write-Host "[1/4] 전체 데이터 refresh..." -ForegroundColor Cyan
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

Write-Host "완료: $here\susi_2027_top50.html" -ForegroundColor Green
