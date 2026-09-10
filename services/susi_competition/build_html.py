"""
susi_2027_top50_nong_nonsul.csv → 자체 완결형 HTML 뷰어 생성.
- 파일 하나(index.html) 만 배포하면 다른 사람도 브라우저에서 바로 열람.
- 정렬/검색/필터 (지역·전형세부유형·정원외·대학군·대학·경쟁률 최댓값·키워드).
- 소스 CSV 는 **전체 대학**을 담고, 상위50 대학에는 주요대학="O" + rank 가 붙어 있다.
  순위가 없는 대학은 rank 를 999 로 채워 정렬 시 뒤로 보낸다.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

HERE = Path(__file__).parent
CSV_PATH = HERE / "susi_2027_top50_nong_nonsul.csv"     # 태그 결과 전체 (본 테이블)
FULL_CSV = HERE / "susi_2027_low_competition.csv"        # 전체 (관심 학과 조회용)
OUT_HTML = HERE / "susi_2027_top50.html"
UNI_DEFAULTS = HERE / "uni_defaults.txt"      # 페이지 최초 진입 시 체크될 대학

# 상단 고정 관심 학과.
#   uni:            대학명 부분매치
#   match:          department OR college 부분매치
#   admission_kw:   (선택) admission_type 안에 반드시 있어야 하는 문자열
#   prefer_campus:  (선택) 대학의 캠퍼스명 부분매치 (같은 학과가 여러 캠퍼스 중복모집일 때)
PINNED = [
    {"label": "가천대 반도체대학 (논술)",
     "uni": "가천대", "match": "반도체대학",
     "admission_kw": "논술", "prefer_campus": "성남"},
    {"label": "성균관대 건설환경공학부 (논술위주 수리형)",
     "uni": "성균관", "match": "건설환경",
     "admission_kw": "수리형", "prefer_campus": "서울"},
    {"label": "건국대 KU자유전공",
     "uni": "건국대", "match": "KU자유전공학부",
     "admission_kw": "", "prefer_campus": "서울"},
    {"label": "세종대 자유전공",
     "uni": "세종대", "match": "자유전공",
     "admission_kw": "", "prefer_campus": ""},
]


_DAY_RE = re.compile(r"(\d{1,2})\s*\.\s*(\d{1,2})")
_TIME_RE = re.compile(r"(\d{1,2}):(\d{2})")


def deadline_label(day: str, time: str) -> tuple[str, int]:
    """('9.11.(금)', '18:00') → ('9/11 18:00', 정렬키).

    '16:00(송도)/18:00(강화)' 처럼 캠퍼스별로 다른 값은 앞의 시각을 대표로 쓴다.
    표에는 원문을 그대로 보여주므로 정보가 사라지지는 않는다.
    """
    dm = _DAY_RE.search(day or "")
    if not dm:
        return "미상", 10 ** 9
    mon, d = int(dm.group(1)), int(dm.group(2))
    tm = _TIME_RE.search(time or "")
    if tm:
        hh, mm = int(tm.group(1)), int(tm.group(2))
        label = f"{mon}/{d} {hh:02d}:{mm:02d}"
    else:
        hh, mm = 23, 59
        label = f"{mon}/{d} 시간미상"
    return label, (mon * 100 + d) * 10000 + hh * 100 + mm


_UNTIL_RE = re.compile(r"(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2})")


def until_key(label: str) -> int:
    """'9/11 12:00' → 마감키와 같은 형식의 정렬키. 빈 값/미상은 맨 뒤."""
    m = _UNTIL_RE.match(label or "")
    if not m:
        return 10 ** 9
    mon, day, hh, mm = (int(g) for g in m.groups())
    return (mon * 100 + day) * 10000 + hh * 100 + mm


def load_uni_defaults() -> list[str]:
    """uni_defaults.txt → 기본 체크 대학 목록 (없거나 비어 있으면 전체)."""
    if not UNI_DEFAULTS.exists():
        return []
    out = []
    for raw in UNI_DEFAULTS.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            out.append(line)
    return out


def _match(row: dict, p: dict) -> bool:
    if p["uni"] not in row["university"]:
        return False
    if p["match"] not in row["department"] and p["match"] not in row["college"]:
        return False
    if p.get("admission_kw") and p["admission_kw"] not in row["admission_type"]:
        return False
    return True


def collect_pinned() -> list[dict]:
    """Return one bundle per pinned target with all its 전형 rows."""
    with FULL_CSV.open(encoding="utf-8-sig") as f:
        all_rows = list(csv.DictReader(f))

    out = []
    for p in PINNED:
        hits = [r for r in all_rows if _match(r, p)]
        # 중복 캠퍼스(성남/인천 통합모집 등)는 우선 캠퍼스만 남긴다.
        if p.get("prefer_campus"):
            filtered = [r for r in hits if p["prefer_campus"] in r["university"]]
            if filtered:
                hits = filtered
        # 세종대 자유전공 특수: 학과/단과대에 '자유전공' 이 들어간 정확 매칭만.
        if p["uni"] == "세종대":
            hits = [r for r in hits if "자유전공" in r["department"]]
        for r in hits:
            r["rate"] = float(r["rate"])
            r["quota"] = int(r["quota"])
            r["applicants"] = int(r["applicants"])
        hits.sort(key=lambda r: r["rate"])
        out.append({"label": p["label"], "rows": hits})
    return out


def build() -> None:
    with CSV_PATH.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    for r in rows:
        # 주요대학(상위50)이 아니면 rank 가 비어 있다 → 정렬용 sentinel.
        r["rank"] = int(r["rank"]) if r["rank"] else 999
        r["마감"], r["마감키"] = deadline_label(r.get("deadline_day", ""),
                                               r.get("deadline_time", ""))
        # 경쟁률 페이지가 알려주는 공개 종료 시각 (대학마다 다르다)
        r["경쟁률마감"] = r.get("rate_until", "") or ""
        r["경쟁률마감키"] = until_key(r["경쟁률마감"])
        r["기준"] = r.get("rate_asof", "") or ""
        # 표에는 원문 시각을 그대로 (예: "16:00(송도)/18:00(강화)")
        raw_t = (r.get("deadline_time") or "").strip()
        r["마감표시"] = r["마감"]
        if raw_t and not _TIME_RE.fullmatch(raw_t) and r["마감키"] < 10 ** 9:
            r["마감표시"] = r["마감"].split(" ")[0] + " " + raw_t
        r["quota"] = int(r["quota"])
        r["applicants"] = int(r["applicants"])
        r["rate"] = float(r["rate"])

    # 안내 문구는 대학 단위라 행마다 넣으면 용량만 커진다 → 대학별 맵으로 한 번만.
    notices = {}
    asof = {}
    for r in rows:
        if r.get("rate_notice") and r["university"] not in notices:
            notices[r["university"]] = r["rate_notice"]
        if r.get("기준") and r["university"] not in asof:
            asof[r["university"]] = r["기준"]
    n_until = len({r["university"] for r in rows if r["경쟁률마감키"] < 10 ** 9})
    print(f"[i] 경쟁률 공개마감 파싱: {n_until}/{len({r['university'] for r in rows})}개 대학",
          file=sys.stderr)
    if asof:
        print(f"[i] 경쟁률 기준시각: {min(asof.values())} ~ {max(asof.values())}", file=sys.stderr)

    from collections import Counter
    dl = Counter(r["마감"] for r in rows)
    print("[i] 마감시간 분포: "
          + ", ".join(f"{k}={v}" for k, v in sorted(dl.items(), key=lambda x: -x[1])),
          file=sys.stderr)

    n_major = sum(1 for r in rows if r["주요대학"] == "O")
    major_unis = {r["university"] for r in rows if r["주요대학"] == "O"}
    n_uni = len({r["university"] for r in rows})
    print(f"[i] 전체 {len(rows)}행 / {n_uni}개 대학 (주요대학 행 {n_major})", file=sys.stderr)

    pinned = collect_pinned()
    for p in pinned:
        n = len(p["rows"])
        print(f"[i] 관심학과 '{p['label']}': {n}개 전형 매칭", file=sys.stderr)

    uni_defaults = load_uni_defaults()
    known = {r["university"] for r in rows}
    unknown = [u for u in uni_defaults if u not in known]
    if unknown:
        print(f"[!] uni_defaults.txt 에 데이터에 없는 대학: {unknown}", file=sys.stderr)
    print(f"[i] 기본 체크 대학: {len(uni_defaults)}개", file=sys.stderr)

    # 원본 마감 컬럼은 마감/마감표시/마감키로 이미 흡수됐다 — 페이지 용량만 차지하므로 제외.
    slim = [{k: v for k, v in r.items()
             if k not in ("deadline_day", "deadline_time", "founder", "기준",
                          "rate_asof", "rate_until", "rate_notice")} for r in rows]
    data_json = json.dumps(slim, ensure_ascii=False, separators=(",", ":"))
    pinned_json = json.dumps(pinned, ensure_ascii=False, separators=(",", ":"))
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = (HTML_TEMPLATE
            .replace("__DATA__", data_json)
            .replace("__PINNED__", pinned_json)
            .replace("__NOTICES__",
                     json.dumps(notices, ensure_ascii=False, separators=(",", ":")))
            .replace("__ASOF_BY_UNI__",
                     json.dumps(asof, ensure_ascii=False, separators=(",", ":")))
            .replace("__ASOF__",
                     json.dumps(sorted(set(asof.values())), ensure_ascii=False,
                                separators=(",", ":")))
            .replace("__UNI_DEFAULTS__",
                     json.dumps(uni_defaults, ensure_ascii=False, separators=(",", ":")))
            .replace("__GENERATED__", generated)
            .replace("__MAJOR_N__", str(len(major_unis))))
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"[i] {len(rows)}행 → {OUT_HTML}", file=sys.stderr)
    print(f"[i] 파일 크기: {OUT_HTML.stat().st_size / 1024:.1f} KB", file=sys.stderr)


HTML_TEMPLATE = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>2027 수시 저경쟁 학과 · 전체대학 · 농특/논술 · 수도권+충청</title>
<style>
  :root {
    --bg: #f7f9fc; --panel: #fff; --line: #e3e8ef; --ink: #1f2937;
    --muted: #6b7280; --accent: #2563eb; --warn: #f59e0b; --danger: #dc2626;
    --good: #059669;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; background: var(--bg); color: var(--ink);
    font: 14px/1.5 "Pretendard","Malgun Gothic","맑은 고딕",-apple-system,
      "Segoe UI",Roboto,sans-serif; }
  header { background: var(--panel); border-bottom: 1px solid var(--line);
    padding: 16px 20px; position: sticky; top: 0; z-index: 30; }
  header h1 { margin: 0 0 4px; font-size: 18px; }
  header p { margin: 0; color: var(--muted); font-size: 12px; }
  main { max-width: 1400px; margin: 0 auto; padding: 16px; }
  .stats { display: grid; grid-template-columns: repeat(auto-fit,minmax(140px,1fr));
    gap: 8px; margin-bottom: 12px; }
  .stat { background: var(--panel); border: 1px solid var(--line); border-radius: 8px;
    padding: 10px 12px; }
  .stat .k { font-size: 11px; color: var(--muted); }
  .stat .v { font-size: 20px; font-weight: 600; }
  .filters { background: var(--panel); border: 1px solid var(--line); border-radius: 8px;
    padding: 12px; margin-bottom: 12px; }
  .row { display: flex; flex-wrap: wrap; gap: 12px; align-items: center;
    margin-bottom: 8px; }
  .row:last-child { margin-bottom: 0; }
  .row label { font-size: 12px; color: var(--muted); margin-right: 4px; }
  .chips { display: flex; flex-wrap: wrap; gap: 4px; }
  .chip { padding: 4px 10px; border: 1px solid var(--line); border-radius: 999px;
    background: #fff; cursor: pointer; font-size: 12px; user-select: none; }
  .chip.on { background: var(--accent); color: #fff; border-color: var(--accent); }
  .chip.warn { border-color: var(--warn); }
  .chip.warn.on { background: var(--warn); border-color: var(--warn); }
  input[type="text"], input[type="number"], select {
    padding: 6px 10px; border: 1px solid var(--line); border-radius: 6px;
    background: #fff; font: inherit; }
  input[type="text"] { min-width: 200px; }
  input[type="number"] { width: 80px; }
  button { padding: 6px 12px; border: 1px solid var(--line); border-radius: 6px;
    background: #fff; cursor: pointer; font: inherit; }
  button:hover { background: #f3f4f6; }
  .tablewrap { background: var(--panel); border: 1px solid var(--line);
    border-radius: 8px; overflow-x: auto; }
  /* table-layout: fixed + colgroup % → 컨테이너 폭에 정확히 맞춰 가로 스크롤이
     생기지 않는다. 좁은 화면(<860px)에서만 tablewrap 이 스크롤된다. */
  table { width: 100%; min-width: 860px; table-layout: fixed;
    border-collapse: separate; border-spacing: 0; font-size: 13px; }
  th, td { padding: 8px 8px; text-align: left;
    border-bottom: 1px solid var(--line); vertical-align: top;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  thead th { white-space: normal; }   /* 헤더는 접히게 두어 글자가 잘리지 않도록 */
  th { background: #f9fafb; font-weight: 600; cursor: pointer;
    user-select: none; box-shadow: inset 0 -1px 0 var(--line); }
  th.sortable { padding-right: 15px; position: relative; }
  th.sortable::after {
    content: "⇅"; color: #d1d5db; font-size: 11px;
    position: absolute; right: 6px; top: 50%; transform: translateY(-50%);
  }
  th.sorted-asc::after { content: "▲"; color: var(--accent); }
  th.sorted-desc::after { content: "▼"; color: var(--accent); }
  th:first-child, td:first-child { padding-left: 12px; }
  /* 순위 column: number stays right-aligned to avoid arrow overlap */
  th:first-child { text-align: center; }
  td:first-child { text-align: center; }
  td.num { text-align: right; font-variant-numeric: tabular-nums; }

  tr:hover { background: #fefce8; }
  tr.mixed { background: #fef3c7; }
  tr.mixed:hover { background: #fde68a; }
  tr.oq td.oq-cell { color: var(--danger); font-weight: 600; }
  .rate-low { color: var(--good); font-weight: 700; }
  .rate-mid { color: var(--ink); }
  .rank { color: var(--muted); font-size: 12px; }
  .empty { padding: 40px; text-align: center; color: var(--muted); }
  .tag { display: inline-block; padding: 1px 6px; border-radius: 4px;
    font-size: 11px; background: #eef2ff; color: #3730a3; }
  .tag.mix { background: #fef3c7; color: #92400e; }
  .tag.nsul { background: #dbeafe; color: #1e40af; }
  .tag.gyoh { background: #dcfce7; color: #166534; }
  .tag.jonh { background: #f3e8ff; color: #6b21a8; }
  .tag.gen { background: #f1f5f9; color: #334155; }
  footer { text-align: center; color: var(--muted); font-size: 11px;
    padding: 20px 0; }
  .warn-banner { background: #fef3c7; border: 1px solid #fbbf24;
    padding: 8px 12px; border-radius: 6px; margin-bottom: 12px; font-size: 12px;
    color: #92400e; }
  .pin-section { background: var(--panel); border: 2px solid var(--accent);
    border-radius: 8px; padding: 12px 16px; margin-bottom: 12px; }
  .pin-section h2 { margin: 0 0 8px; font-size: 14px; color: var(--accent);
    display: flex; align-items: center; gap: 6px; }
  .pin-grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(320px,1fr));
    gap: 10px; }
  .pin-card { border: 1px solid var(--line); border-radius: 6px; padding: 8px 10px; }
  .pin-card .lbl { font-weight: 600; margin-bottom: 4px; color: var(--ink); }
  .pin-card .min { font-size: 12px; color: var(--muted); margin-bottom: 4px; }
  .pin-card .min strong.low { color: var(--good); font-size: 15px; }
  .pin-card .min strong.high { color: var(--danger); font-size: 15px; }
  .pin-card .empty { padding: 8px; font-size: 12px; }
  /* 카드 폭(≈320px)에 5열 표를 넣으면 글자가 카드 밖으로 밀린다 → 블록으로 쌓는다. */
  .pin-row { border-top: 1px solid #f3f4f6; padding: 5px 0; }
  .pin-row:first-child { border-top: 0; }
  .pin-row-top { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 8px; }
  .pin-row-top .rate { font-size: 14px; font-weight: 700;
    font-variant-numeric: tabular-nums; }
  .pin-row-top .mj { font-size: 11px; color: var(--muted);
    font-variant-numeric: tabular-nums; }
  .pin-row-top .uni { font-size: 11px; color: var(--ink); }
  .pin-row-sub { font-size: 11px; color: var(--muted); margin-top: 2px;
    word-break: keep-all; overflow-wrap: anywhere; }
  .pin-row-sub .sep { color: #d1d5db; margin: 0 3px; }
  .uni-toggle { display: inline-flex; align-items: center; gap: 6px; }
  .uni-toggle.active { border-color: var(--accent); color: var(--accent); }
  .uni-panel { border: 1px solid var(--line); border-radius: 6px; padding: 8px;
    margin-top: 4px; background: #fbfcfe; }
  .uni-tools { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
  .uni-tools input[type="text"] { min-width: 140px; flex: 1 1 140px; }
  .uni-list { display: grid; grid-template-columns: repeat(auto-fill,minmax(210px,1fr));
    gap: 2px 8px; max-height: 260px; overflow-y: auto; }
  .uni-item { display: flex; align-items: center; gap: 6px; font-size: 12px;
    padding: 3px 4px; border-radius: 4px; cursor: pointer; }
  .uni-item:hover { background: #eef2ff; }
  .uni-item input { margin: 0; }
  .uni-item .cnt { color: var(--muted); font-size: 11px; }
  .uni-item .star { color: var(--warn); }
  .major-star { color: var(--warn); margin-right: 2px; }
  button.primary { background: var(--accent); color: #fff; border-color: var(--accent);
    font-weight: 600; }
  button.primary:hover { background: #1d4ed8; }
  button.primary.dirty { background: var(--warn); border-color: var(--warn); }
  button.primary.dirty::after { content: " •"; }
  .hint { font-size: 11px; color: var(--muted); }
  /* 접수마감이 지난 행 — 색을 모두 회색으로 눌러 한눈에 구분되게. */
  tr.past, tr.past:hover, tr.mixed.past, tr.mixed.past:hover { background: #f8fafc; }
  tr.past td, tr.past td span, tr.past td .rank { color: #9ca3af; }
  tr.past td .tag { background: #f1f5f9; color: #94a3b8; }
  tr.past td.ru, tr.past td.ru.unknown, tr.past td.dl.soon { color: #9ca3af; }
  tr.past td .badge { background: #f1f5f9; color: #94a3b8; }
  .dl { font-variant-numeric: tabular-nums; }
  .dl.soon { color: var(--danger); font-weight: 700; }
  /* 이미 지난 마감 칩은 선택돼 있어도 파랗게 두지 않는다. */
  .chip.past, .chip.on.past { background: #f1f5f9; border-color: #e2e8f0;
    color: #94a3b8; text-decoration: line-through; }
  .ru { font-variant-numeric: tabular-nums; }
  .ru.closed { color: var(--muted); }
  .ru.unknown { color: #c2410c; }
  .badge { display: inline-block; padding: 0 5px; border-radius: 4px; font-size: 10px;
    margin-left: 4px; background: #e5e7eb; color: #374151; }
  .asof { font-size: 11px; color: var(--muted); }
  .hint.saved { color: var(--accent); }
  .export-box { margin-top: 8px; }
  .export-box textarea { width: 100%; height: 90px; font: 12px/1.4 ui-monospace,
    Consolas,monospace; border: 1px solid var(--line); border-radius: 6px; padding: 6px; }
</style>
</head>
<body>
<header>
  <h1>2027학년도 수시 저경쟁 학과 검색</h1>
  <p><strong>전체 대학</strong> · 서울·경기·충청 · 농어촌·농특·논술 <strong>전 전형</strong>
     (경쟁률 컷 없음 — 화면 기본값 <strong>≤ 2.0</strong>, 숫자를 올리면 더 보입니다)
     · ★ = 주요대학 __MAJOR_N__개교 (지정 목록)
     · 제외: 고려대(세종), 모든 여대 · 생성: __GENERATED__</p>
  <p class="asof">경쟁률 기준시각(대학별 상이): <span id="asof-range"></span>
     · 경쟁률 공개는 대학마다 접수마감보다 이르게 끝납니다 — <strong>경쟁률마감</strong> 열 참고
     (칸에 마우스를 올리면 대학 공지 원문)</p>
</header>
<main>
  <div class="warn-banner">
    ⚠️ <strong>기회균형_혼합</strong> (노란 행)은 국가보훈·수급자·자립아동 등과 함께 지원하는
    통합 전형이라 순수 농어촌 전형과 성격이 다릅니다.
    ⚠️ <strong>정원외 "O"</strong> 표시는 별도 지원자격(농어촌 학생 등)이 필요합니다.
    ⚠️ 원서 마감 임박 시점의 경쟁률이므로 최종 확정 경쟁률과 다를 수 있습니다.
    ⚠️ 필터를 바꾼 뒤에는 <strong>[검색]</strong> 을 눌러야 표에 반영됩니다.
    ⚠️ <strong>경쟁률마감</strong>이 지난 대학은 숫자가 더 이상 오르지 않습니다 (그 시점의 값에서 멈춤).
  </div>

  <div class="pin-section">
    <h2>📌 관심 학과 현재 경쟁률</h2>
    <div class="pin-grid" id="pin-grid"></div>
  </div>

  <div class="stats" id="stats"></div>

  <div class="filters">
    <div class="row">
      <label>세부유형</label>
      <div class="chips" id="chips-type"></div>
    </div>
    <div class="row">
      <label>지역</label>
      <div class="chips" id="chips-region"></div>
    </div>
    <div class="row">
      <label>정원외</label>
      <div class="chips" id="chips-oq">
        <span class="chip on" data-v="all">전체</span>
        <span class="chip" data-v="in">정원내만</span>
        <span class="chip" data-v="out">정원외만</span>
      </div>
    </div>
    <div class="row">
      <label>마감</label>
      <div class="chips" id="chips-deadline"></div>
    </div>
    <div class="row">
      <label>경쟁률공개</label>
      <div class="chips" id="chips-ru">
        <span class="chip on" data-v="all">전체</span>
        <span class="chip" data-v="open">공개중</span>
        <span class="chip" data-v="closed">공개종료</span>
        <span class="chip" data-v="unknown">공개마감 미상</span>
      </div>
    </div>
    <div class="row">
      <label>대학군</label>
      <div class="chips" id="chips-major">
        <span class="chip on" data-v="all">전체</span>
        <span class="chip" data-v="major">★ 주요대학만</span>
        <span class="chip" data-v="other">그 외 대학만</span>
      </div>
    </div>
    <div class="row">
      <label>대학</label>
      <button id="uni-toggle" class="uni-toggle">전체 대학 ▾</button>
      <label>경쟁률 ≤</label>
      <input type="number" id="max-rate" step="0.1" min="0" value="2.0">
      <label>최소 모집</label>
      <input type="number" id="min-quota" step="1" min="1" value="1">
      <label>검색</label>
      <input type="text" id="search" placeholder="학과·단과대 키워드">
      <button id="search-btn" class="primary">검색</button>
      <button id="reset">초기화</button>
      <span class="hint" id="restored-hint" hidden>저장된 선택을 불러왔습니다</span>
    </div>
    <div class="uni-panel" id="uni-panel" hidden>
      <div class="uni-tools">
        <input type="text" id="uni-search" placeholder="대학명 검색">
        <button data-act="major">★ 주요대학 모두 체크</button>
        <button data-act="all">모두 체크</button>
        <button data-act="none">모두 해제</button>
        <button id="uni-export">선택 내보내기</button>
      </div>
      <div class="uni-list" id="uni-list"></div>
      <div class="export-box" id="export-box" hidden>
        <div class="hint">아래 목록을 <code>services/susi_competition/uni_defaults.txt</code>
          에 붙여넣고 커밋하면 모든 브라우저에서 이 선택으로 시작합니다.</div>
        <textarea id="export-text" readonly></textarea>
      </div>
    </div>
  </div>

  <div class="tablewrap">
    <table id="tbl">
      <colgroup>
        <col style="width:4%"><col style="width:5.5%"><col style="width:4%">
        <col style="width:4%"><col style="width:4.5%"><col style="width:12%">
        <col style="width:8.5%"><col style="width:9%"><col style="width:9%">
        <col style="width:3.5%"><col style="width:13.5%"><col style="width:9.5%">
        <col style="width:13%">
      </colgroup>
      <thead>
        <tr>
          <th class="sortable" data-k="rank">순위</th>
          <th class="sortable sorted-asc" data-k="rate">경쟁률</th>
          <th class="sortable" data-k="quota">모집</th>
          <th class="sortable" data-k="applicants">지원</th>
          <th class="sortable" data-k="region">지역</th>
          <th class="sortable" data-k="university">대학</th>
          <th class="sortable" data-k="마감키">접수마감</th>
          <th class="sortable" data-k="경쟁률마감키">경쟁률마감</th>
          <th class="sortable" data-k="전형세부유형">세부유형</th>
          <th class="sortable" data-k="정원외">정외</th>
          <th class="sortable" data-k="admission_type">전형명</th>
          <th class="sortable" data-k="college">단과대</th>
          <th class="sortable" data-k="department">학과</th>
        </tr>
      </thead>
      <tbody id="tb"></tbody>
    </table>
    <div id="empty" class="empty" style="display:none">조건에 맞는 학과가 없습니다.</div>
  </div>

  <footer>
    데이터: 경기도교육청 2027 수시 경쟁률 검색기 + 진학사/유웨이 학과별 페이지<br>
    대학순위: 대학백과 (univ100.kr / 커뮤니티 2224934)
  </footer>
</main>

<script>
const DATA = __DATA__;
const PINNED = __PINNED__;
const NOTICES = __NOTICES__;             // 대학 → 경쟁률 공개 안내 원문
const ASOF = __ASOF__;                   // 경쟁률 기준시각 목록 (대학마다 다름)
const ASOF_BY_UNI = __ASOF_BY_UNI__;     // 대학 → 이 대학 경쟁률의 기준시각
const DEFAULT_UNIS = __UNI_DEFAULTS__;   // uni_defaults.txt (모든 브라우저 공통 기본값)
const STORE_KEY = "susi2027.filters.v1"; // 이 브라우저에서의 마지막 선택

// --- 관심 학과 카드 렌더링 --------------------------------------------------
function renderPinned() {
  const grid = document.getElementById("pin-grid");
  PINNED.forEach(p => {
    const card = document.createElement("div");
    card.className = "pin-card";
    if (!p.rows.length) {
      card.innerHTML = `<div class="lbl">${escapeHtml(p.label)}</div>
        <div class="empty">데이터 없음 (전형 미개시 또는 미포함)</div>`;
      grid.appendChild(card);
      return;
    }
    const minRate = Math.min(...p.rows.map(r => r.rate));
    const maxRate = Math.max(...p.rows.map(r => r.rate));
    const cls = minRate < 1.0 ? "low" : "high";
    let tbl = "";
    p.rows.forEach(r => {
      const rateCls = r.rate < 1.0 ? "rate-low" : "";
      const deptLabel = (r.college ? r.college + " / " : "") + r.department;
      tbl += `<div class="pin-row">
        <div class="pin-row-top">
          <span class="rate ${rateCls}">${r.rate.toFixed(2)}</span>
          <span class="mj">모집 ${r.quota} / 지원 ${r.applicants}</span>
          <span class="uni">${escapeHtml(r.university)}</span>
        </div>
        <div class="pin-row-sub">${escapeHtml(r.admission_type)}<span class="sep">·</span>${escapeHtml(deptLabel)}</div>
      </div>`;
    });
    card.innerHTML = `
      <div class="lbl">${escapeHtml(p.label)}</div>
      <div class="min">최저 <strong class="${cls}">${minRate.toFixed(2)}</strong>
        · 최고 ${maxRate.toFixed(2)} · ${p.rows.length}개 전형</div>
      ${tbl}
    `;
    grid.appendChild(card);
  });
}

const state = {
  types: new Set(),        // empty = all
  regions: new Set(),      // empty = all
  oq: "all",               // all / in / out
  deadlines: new Set(),    // empty = all  (접수마감 라벨)
  ru: "all",               // all / open / closed / unknown  (경쟁률 공개 상태)
  major: "all",            // all / major / other  (주요대학 = 상위50)
  unis: new Set(),         // empty = all
  maxRate: 2.0,
  minQuota: 1,
  q: "",
  sortKey: "rate",
  sortDir: 1,              // 1 asc, -1 desc
};

// --- 상태 저장/복원 (localStorage) -------------------------------------------
// localStorage 는 브라우저별로 분리돼 있고 사생활 보호 모드에서는 던질 수 있으므로
// 전부 try/catch 로 감싸고, 실패하면 조용히 기본값으로 동작한다.
function saveState() {
  try {
    localStorage.setItem(STORE_KEY, JSON.stringify({
      types: [...state.types], regions: [...state.regions],
      deadlines: [...state.deadlines], ru: state.ru,
      oq: state.oq, major: state.major, unis: [...state.unis],
      maxRate: state.maxRate, minQuota: state.minQuota, q: state.q,
    }));
  } catch (e) { /* 저장 불가 — 무시 */ }
}

function clearSaved() {
  try { localStorage.removeItem(STORE_KEY); } catch (e) { /* 무시 */ }
}

function restoreState() {
  const names = new Set(UNIS.map(u => u.name));
  let saved = null;
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (raw) saved = JSON.parse(raw);
  } catch (e) { saved = null; }

  if (!saved) {
    // 저장된 게 없으면 저장소 기본값(uni_defaults.txt)으로 시작.
    DEFAULT_UNIS.filter(u => names.has(u)).forEach(u => state.unis.add(u));
    return false;
  }
  state.types = new Set((saved.types || []).filter(t => TYPE_ORDER.includes(t)));
  state.regions = new Set(saved.regions || []);
  const dlNames = new Set(DEADLINES.map(d => d.label));
  state.deadlines = new Set((saved.deadlines || []).filter(d => dlNames.has(d)));
  state.oq = ["all", "in", "out"].includes(saved.oq) ? saved.oq : "all";
  state.ru = ["all", "open", "closed", "unknown"].includes(saved.ru) ? saved.ru : "all";
  state.major = ["all", "major", "other"].includes(saved.major) ? saved.major : "all";
  state.unis = new Set((saved.unis || []).filter(u => names.has(u)));
  if (typeof saved.maxRate === "number" && isFinite(saved.maxRate)) state.maxRate = saved.maxRate;
  if (typeof saved.minQuota === "number" && isFinite(saved.minQuota)) state.minQuota = saved.minQuota;
  state.q = typeof saved.q === "string" ? saved.q : "";
  return true;
}

// 상태 → 화면 컨트롤 반영 (복원/초기화 직후 호출)
function syncUiFromState() {
  const onOff = (sel, set) => document.querySelectorAll(sel).forEach(el => {
    el.classList.toggle("on", set.size === 0 || set.has(el.dataset.v));
  });
  onOff("#chips-type .chip", state.types);
  onOff("#chips-region .chip", state.regions);
  onOff("#chips-deadline .chip", state.deadlines);
  document.querySelectorAll("#chips-oq .chip").forEach(el =>
    el.classList.toggle("on", el.dataset.v === state.oq));
  document.querySelectorAll("#chips-ru .chip").forEach(el =>
    el.classList.toggle("on", el.dataset.v === state.ru));
  document.querySelectorAll("#chips-major .chip").forEach(el =>
    el.classList.toggle("on", el.dataset.v === state.major));
  document.getElementById("max-rate").value = state.maxRate;
  document.getElementById("min-quota").value = state.minQuota;
  document.getElementById("search").value = state.q;
  syncUniChecks();
  syncUniLabel();
}

// --- 검색 버튼: 필터 변경은 모아뒀다가 [검색] 에서 한 번에 반영 ------------------
function markDirty() {
  document.getElementById("search-btn").classList.add("dirty");
}

function applyFilters(save = true) {
  document.getElementById("search-btn").classList.remove("dirty");
  if (save) saveState();
  render();
}

// --- 초기화: 칩/셀렉트 채우기 ------------------------------------------------
function unique(field) {
  return [...new Set(DATA.map(r => r[field]))].filter(x => x !== "")
    .sort((a, b) => a.localeCompare(b, "ko"));
}

// 마감 라벨 목록 (이른 순) — 칩 필터용
const DEADLINES = [...new Map(DATA.map(r => [r["마감"], r["마감키"]])).entries()]
  .sort((a, b) => a[1] - b[1])
  .map(([label, key]) => ({ label, key, n: DATA.filter(r => r["마감"] === label).length }));

const UNKNOWN_KEY = 1000000000;

// 경쟁률마감 셀 표시/색
function ruText(r, nk) {
  if (r["경쟁률마감키"] >= UNKNOWN_KEY) return "미상";
  const closed = r["경쟁률마감키"] < nk;
  return r["경쟁률마감"] + (closed ? '<span class="badge">종료</span>' : "");
}
function ruTip(r) {
  const parts = [];
  if (ASOF_BY_UNI[r.university]) parts.push("경쟁률 기준시각: " + ASOF_BY_UNI[r.university]);
  if (NOTICES[r.university]) parts.push(NOTICES[r.university]);
  return parts.join(String.fromCharCode(10));
}
function ruCls(r, nk) {
  if (r["경쟁률마감키"] >= UNKNOWN_KEY) return " unknown";
  return r["경쟁률마감키"] < nk ? " closed" : "";
}

// '지금'을 같은 형식의 정렬키로 (뷰어의 로컬 시각 기준)
function nowKey() {
  const d = new Date();
  return ((d.getMonth() + 1) * 100 + d.getDate()) * 10000 + d.getHours() * 100 + d.getMinutes();
}

// 가나다순 전체 대학 + 주요대학 여부/행수
const UNIS = unique("university").map(u => ({
  name: u,
  major: DATA.some(r => r.university === u && r["주요대학"] === "O"),
  n: DATA.filter(r => r.university === u).length,
}));

const TYPE_ORDER = ["논술", "농어촌_교과", "농어촌_종합", "농어촌_일반", "기회균형_혼합"];
const TYPE_CLASS = {
  "논술": "nsul",
  "농어촌_교과": "gyoh",
  "농어촌_종합": "jonh",
  "농어촌_일반": "gen",
  "기회균형_혼합": "mix",
};

function initChips() {
  const typeEl = document.getElementById("chips-type");
  TYPE_ORDER.forEach(t => {
    if (!DATA.some(r => r["전형세부유형"] === t)) return;
    const el = document.createElement("span");
    el.className = "chip on" + (t === "기회균형_혼합" ? " warn" : "");
    el.textContent = t + " (" + DATA.filter(r => r["전형세부유형"] === t).length + ")";
    el.dataset.v = t;
    el.onclick = () => {
      el.classList.toggle("on");
      const on = document.querySelectorAll("#chips-type .chip.on");
      state.types = new Set([...on].map(x => x.dataset.v));
      // 전체 켜져있으면 무필터로 취급
      if (state.types.size === TYPE_ORDER.filter(t=>DATA.some(r=>r["전형세부유형"]===t)).length)
        state.types = new Set();
      markDirty();
    };
    typeEl.appendChild(el);
  });

  const regionEl = document.getElementById("chips-region");
  unique("region").forEach(r => {
    const el = document.createElement("span");
    el.className = "chip on";
    el.textContent = r + " (" + DATA.filter(x => x.region === r).length + ")";
    el.dataset.v = r;
    el.onclick = () => {
      el.classList.toggle("on");
      const on = document.querySelectorAll("#chips-region .chip.on");
      state.regions = new Set([...on].map(x => x.dataset.v));
      if (state.regions.size === unique("region").length) state.regions = new Set();
      markDirty();
    };
    regionEl.appendChild(el);
  });

  document.querySelectorAll("#chips-oq .chip").forEach(el => {
    el.onclick = () => {
      document.querySelectorAll("#chips-oq .chip").forEach(x => x.classList.remove("on"));
      el.classList.add("on");
      state.oq = el.dataset.v;
      markDirty();
    };
  });

  const dlEl = document.getElementById("chips-deadline");
  const nk = nowKey();
  DEADLINES.forEach(d => {
    const el = document.createElement("span");
    el.className = "chip on" + (d.key < nk ? " past" : "");
    el.textContent = d.label + " (" + d.n + ")";
    el.dataset.v = d.label;
    el.title = d.key < nk ? "이미 마감된 시각" : "";
    el.onclick = () => {
      el.classList.toggle("on");
      const on = document.querySelectorAll("#chips-deadline .chip.on");
      state.deadlines = new Set([...on].map(x => x.dataset.v));
      if (state.deadlines.size === DEADLINES.length) state.deadlines = new Set();
      markDirty();
    };
    dlEl.appendChild(el);
  });

  document.querySelectorAll("#chips-ru .chip").forEach(el => {
    el.onclick = () => {
      document.querySelectorAll("#chips-ru .chip").forEach(x => x.classList.remove("on"));
      el.classList.add("on");
      state.ru = el.dataset.v;
      markDirty();
    };
  });

  document.getElementById("asof-range").textContent =
    ASOF.length ? (ASOF.length === 1 ? ASOF[0] : ASOF[0] + " ~ " + ASOF[ASOF.length - 1])
                : "(정보 없음)";

  document.querySelectorAll("#chips-major .chip").forEach(el => {
    el.onclick = () => {
      document.querySelectorAll("#chips-major .chip").forEach(x => x.classList.remove("on"));
      el.classList.add("on");
      state.major = el.dataset.v;
      markDirty();
    };
  });

  initUniPanel();

  document.getElementById("max-rate").oninput = e => {
    const v = parseFloat(e.target.value);
    state.maxRate = isFinite(v) ? v : 2.0; markDirty();
  };
  document.getElementById("min-quota").oninput = e => {
    state.minQuota = parseInt(e.target.value) || 1; markDirty();
  };
  document.getElementById("search").oninput = e => {
    state.q = e.target.value.trim(); markDirty();
  };
  // 입력칸에서 Enter → 바로 검색
  ["max-rate", "min-quota", "search"].forEach(id => {
    document.getElementById(id).onkeydown = e => {
      if (e.key === "Enter") { e.preventDefault(); applyFilters(); }
    };
  });
  document.getElementById("search-btn").onclick = () => applyFilters();
  // 초기화 = 이 브라우저의 저장분을 지우고 저장소 기본값(uni_defaults.txt)으로.
  document.getElementById("reset").onclick = () => {
    clearSaved();
    document.getElementById("restored-hint").hidden = true;
    document.getElementById("export-box").hidden = true;
    state.types.clear(); state.regions.clear(); state.deadlines.clear();
    state.oq = "all"; state.ru = "all"; state.major = "all"; state.unis.clear();
    DEFAULT_UNIS.filter(u => UNIS.some(x => x.name === u)).forEach(u => state.unis.add(u));
    state.maxRate = 2.0; state.minQuota = 1; state.q = "";
    document.getElementById("uni-search").value = "";
    document.querySelectorAll("#uni-list .uni-item").forEach(x => { x.hidden = false; });
    syncUiFromState();
    applyFilters(false);   // 초기화 결과는 저장하지 않는다
  };

  document.querySelectorAll("th.sortable").forEach(th => {
    th.onclick = () => {
      const k = th.dataset.k;
      if (state.sortKey === k) state.sortDir = -state.sortDir;
      else { state.sortKey = k; state.sortDir = 1; }
      document.querySelectorAll("th").forEach(x => {
        x.classList.remove("sorted-asc", "sorted-desc");
      });
      th.classList.add(state.sortDir === 1 ? "sorted-asc" : "sorted-desc");
      render();
    };
  });
}

// --- 대학 선택 패널 (가나다순 전체 대학 · 체크박스) ---------------------------
function initUniPanel() {
  const list = document.getElementById("uni-list");
  UNIS.forEach(u => {
    const item = document.createElement("label");
    item.className = "uni-item";
    item.dataset.name = u.name;
    item.innerHTML = `<input type="checkbox" value="${escapeHtml(u.name)}">
      <span>${u.major ? '<span class="star">★</span>' : ""}${escapeHtml(u.name)}</span>
      <span class="cnt">(${u.n})</span>`;
    item.querySelector("input").onchange = e => {
      if (e.target.checked) state.unis.add(u.name);
      else state.unis.delete(u.name);
      syncUniLabel();
      markDirty();
    };
    list.appendChild(item);
  });

  const toggle = document.getElementById("uni-toggle");
  const panel = document.getElementById("uni-panel");
  toggle.onclick = () => { panel.hidden = !panel.hidden; };

  document.getElementById("uni-search").oninput = e => {
    const q = e.target.value.trim().toLowerCase();
    document.querySelectorAll("#uni-list .uni-item").forEach(el => {
      el.hidden = q ? !el.dataset.name.toLowerCase().includes(q) : false;
    });
  };

  document.querySelectorAll("#uni-panel .uni-tools button").forEach(btn => {
    btn.onclick = () => {
      const act = btn.dataset.act;
      state.unis.clear();
      if (act === "all") UNIS.forEach(u => state.unis.add(u.name));
      if (act === "major") UNIS.filter(u => u.major).forEach(u => state.unis.add(u.name));
      syncUniChecks();
      syncUniLabel();
      markDirty();
    };
  });

  // 선택 내보내기 — uni_defaults.txt 에 붙여넣으면 모든 브라우저의 기본값이 된다.
  document.getElementById("uni-export").onclick = () => {
    const box = document.getElementById("export-box");
    const ta = document.getElementById("export-text");
    const picked = UNIS.filter(u => state.unis.has(u.name)).map(u => u.name);
    const NL = String.fromCharCode(10);
    ta.value = picked.length ? picked.join(NL) : "# 체크된 대학이 없습니다 (= 전체 대학).";
    box.hidden = false;
    ta.select();
    try { navigator.clipboard.writeText(ta.value); } catch (e) { /* 수동 복사 */ }
  };

  syncUniLabel();
}

function syncUniChecks() {
  document.querySelectorAll("#uni-list input").forEach(cb => {
    cb.checked = state.unis.has(cb.value);
  });
}

function syncUniLabel() {
  const toggle = document.getElementById("uni-toggle");
  const n = state.unis.size;
  const picked = n > 0 && n < UNIS.length;
  toggle.textContent = picked ? `${n}개 대학 선택 ▾` : `전체 대학 (${UNIS.length}) ▾`;
  toggle.classList.toggle("active", picked);
}

// --- 필터/정렬/렌더 ---------------------------------------------------------
function filtered() {
  const q = state.q.toLowerCase();
  const nowKeyCached = nowKey();
  return DATA.filter(r => {
    if (state.types.size && !state.types.has(r["전형세부유형"])) return false;
    if (state.regions.size && !state.regions.has(r.region)) return false;
    if (state.oq === "in" && r["정원외"] === "O") return false;
    if (state.oq === "out" && r["정원외"] !== "O") return false;
    if (state.deadlines.size && !state.deadlines.has(r["마감"])) return false;
    if (state.ru !== "all") {
      const k = r["경쟁률마감키"];
      if (state.ru === "unknown" && k < UNKNOWN_KEY) return false;
      if (state.ru === "open" && (k >= UNKNOWN_KEY || k < nowKeyCached)) return false;
      if (state.ru === "closed" && (k >= UNKNOWN_KEY || k >= nowKeyCached)) return false;
    }
    if (state.major === "major" && r["주요대학"] !== "O") return false;
    if (state.major === "other" && r["주요대학"] === "O") return false;
    // 전부 체크 = 무필터로 취급
    if (state.unis.size && state.unis.size < UNIS.length
        && !state.unis.has(r.university)) return false;
    if (r.rate > state.maxRate) return false;
    if (r.quota < state.minQuota) return false;
    if (q && !(
      r.department.toLowerCase().includes(q) ||
      r.college.toLowerCase().includes(q) ||
      r.admission_type.toLowerCase().includes(q) ||
      r.university.toLowerCase().includes(q)
    )) return false;
    return true;
  }).sort((a, b) => {
    let va = a[state.sortKey], vb = b[state.sortKey];
    if (typeof va === "string") { va = va || ""; vb = vb || ""; return va.localeCompare(vb) * state.sortDir; }
    return (va - vb) * state.sortDir;
  });
}

function renderStats(rows) {
  const el = document.getElementById("stats");
  const uniCount = new Set(rows.map(r => r.university)).size;
  const under1 = rows.filter(r => r.rate < 1.0).length;
  const nsul = rows.filter(r => r["전형세부유형"] === "논술").length;
  const nong = rows.filter(r => r["전형대분류"] === "농어촌").length;
  const majorN = rows.filter(r => r["주요대학"] === "O").length;
  const nk2 = nowKey();
  const live = rows.filter(r => r["마감키"] >= nk2).length;
  const oq = rows.filter(r => r["정원외"] === "O").length;
  el.innerHTML = `
    <div class="stat"><div class="k">필터 결과</div><div class="v">${rows.length}</div></div>
    <div class="stat"><div class="k">대학 수</div><div class="v">${uniCount}</div></div>
    <div class="stat"><div class="k">미달 &lt;1.0</div><div class="v" style="color:var(--good)">${under1}</div></div>
    <div class="stat"><div class="k">아직 접수중</div><div class="v" style="color:var(--accent)">${live}</div></div>
    <div class="stat"><div class="k">★ 주요대학</div><div class="v">${majorN}</div></div>
    <div class="stat"><div class="k">논술</div><div class="v">${nsul}</div></div>
    <div class="stat"><div class="k">농어촌계</div><div class="v">${nong}</div></div>
    <div class="stat"><div class="k">정원외</div><div class="v">${oq}</div></div>
  `;
}

function render() {
  const rows = filtered();
  renderStats(rows);
  const tb = document.getElementById("tb");
  const empty = document.getElementById("empty");
  if (!rows.length) { tb.innerHTML = ""; empty.style.display = "block"; return; }
  empty.style.display = "none";
  const frag = document.createDocumentFragment();
  const nk = nowKey();
  const soonKey = nk + 200;            // 앞으로 2시간 이내 마감 → 빨간색
  rows.forEach(r => {
    const past = r["마감키"] < nk;
    const tr = document.createElement("tr");
    if (past) tr.classList.add("past");
    if (r["전형세부유형"] === "기회균형_혼합") tr.classList.add("mixed");
    if (r["정원외"] === "O") tr.classList.add("oq");
    const rateCls = r.rate < 1.0 ? "rate-low" : "rate-mid";
    const cls = TYPE_CLASS[r["전형세부유형"]] || "gen";
    tr.innerHTML = `
      <td><span class="rank">${r.rank < 999 ? "#" + r.rank : "—"}</span></td>
      <td class="num ${rateCls}">${r.rate.toFixed(2)}</td>
      <td class="num">${r.quota}</td>
      <td class="num">${r.applicants}</td>
      <td>${r.region}</td>
      <td title="${escapeHtml(r.university)}">${r["주요대학"] === "O" ? '<span class="major-star">★</span>' : ""}${escapeHtml(r.university)}</td>
      <td class="dl${past ? "" : (r["마감키"] < soonKey ? " soon" : "")}">${escapeHtml(r["마감표시"] || r["마감"])}</td>
      <td class="ru${ruCls(r, nk)}" title="${escapeHtml(ruTip(r))}">${ruText(r, nk)}</td>
      <td title="${r["전형세부유형"]}"><span class="tag ${cls}">${r["전형세부유형"]}</span></td>
      <td class="oq-cell">${r["정원외"] || ""}</td>
      <td title="${escapeHtml(r.admission_type)}">${escapeHtml(r.admission_type)}</td>
      <td title="${escapeHtml(r.college)}">${escapeHtml(r.college)}</td>
      <td title="${escapeHtml(r.department)}">${escapeHtml(r.department)}</td>
    `;
    frag.appendChild(tr);
  });
  tb.innerHTML = "";
  tb.appendChild(frag);
}

function escapeHtml(s) {
  return String(s || "").replace(/[&<>"']/g, c =>
    ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}

renderPinned();
initChips();
const restored = restoreState();
syncUiFromState();
if (restored) document.getElementById("restored-hint").hidden = false;
render();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
