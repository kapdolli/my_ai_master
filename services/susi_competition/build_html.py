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
        r["quota"] = int(r["quota"])
        r["applicants"] = int(r["applicants"])
        r["rate"] = float(r["rate"])

    n_major = sum(1 for r in rows if r["주요대학"] == "O")
    n_uni = len({r["university"] for r in rows})
    print(f"[i] 전체 {len(rows)}행 / {n_uni}개 대학 (주요대학 행 {n_major})", file=sys.stderr)

    pinned = collect_pinned()
    for p in pinned:
        n = len(p["rows"])
        print(f"[i] 관심학과 '{p['label']}': {n}개 전형 매칭", file=sys.stderr)

    data_json = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    pinned_json = json.dumps(pinned, ensure_ascii=False, separators=(",", ":"))
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = (HTML_TEMPLATE
            .replace("__DATA__", data_json)
            .replace("__PINNED__", pinned_json)
            .replace("__GENERATED__", generated))
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
  table { width: 100%; border-collapse: separate; border-spacing: 0;
    font-size: 13px; }
  th, td { padding: 8px 10px; text-align: left;
    border-bottom: 1px solid var(--line); vertical-align: top;
    white-space: nowrap; }
  th { background: #f9fafb; font-weight: 600; cursor: pointer;
    user-select: none; box-shadow: inset 0 -1px 0 var(--line); }
  th.sortable { padding-right: 18px; position: relative; }
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
  tr.oq td:nth-child(7) { color: var(--danger); font-weight: 600; }
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
  .pin-card table { font-size: 11px; margin-top: 4px; }
  .pin-card th, .pin-card td { padding: 3px 4px; border-bottom: 1px solid #f3f4f6; }
  .pin-card th { background: transparent; position: static; font-weight: 500;
    color: var(--muted); }
  .pin-card .empty { padding: 8px; font-size: 12px; }
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
</style>
</head>
<body>
<header>
  <h1>2027학년도 수시 저경쟁 학과 검색</h1>
  <p><strong>전체 대학</strong> · 서울·경기·충청 · 농어촌·농특·논술 · 경쟁률 &lt;2.0
     · ★ = 주요대학(대학백과 2026 상위 50)
     · 제외: 고려대(세종), 모든 여대 · 생성: __GENERATED__</p>
</header>
<main>
  <div class="warn-banner">
    ⚠️ <strong>기회균형_혼합</strong> (노란 행)은 국가보훈·수급자·자립아동 등과 함께 지원하는
    통합 전형이라 순수 농어촌 전형과 성격이 다릅니다.
    ⚠️ <strong>정원외 "O"</strong> 표시는 별도 지원자격(농어촌 학생 등)이 필요합니다.
    ⚠️ 원서 마감 임박 시점의 경쟁률이므로 최종 확정 경쟁률과 다를 수 있습니다.
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
      <input type="number" id="max-rate" step="0.1" min="0" max="2" value="2.0">
      <label>최소 모집</label>
      <input type="number" id="min-quota" step="1" min="1" value="1">
      <label>검색</label>
      <input type="text" id="search" placeholder="학과·단과대 키워드">
      <button id="reset">초기화</button>
    </div>
    <div class="uni-panel" id="uni-panel" hidden>
      <div class="uni-tools">
        <input type="text" id="uni-search" placeholder="대학명 검색">
        <button data-act="major">★ 주요대학 모두 체크</button>
        <button data-act="all">모두 체크</button>
        <button data-act="none">모두 해제</button>
      </div>
      <div class="uni-list" id="uni-list"></div>
    </div>
  </div>

  <div class="tablewrap">
    <table id="tbl">
      <thead>
        <tr>
          <th class="sortable" data-k="rank">순위</th>
          <th class="sortable sorted-asc" data-k="rate">경쟁률</th>
          <th class="sortable" data-k="quota">모집</th>
          <th class="sortable" data-k="applicants">지원</th>
          <th class="sortable" data-k="region">지역</th>
          <th class="sortable" data-k="university">대학</th>
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
    let tbl = `<table><thead><tr>
      <th>경쟁률</th><th>모/지</th><th>대학</th><th>전형</th><th>학과/단과</th>
    </tr></thead><tbody>`;
    p.rows.forEach(r => {
      const rateCls = r.rate < 1.0 ? "rate-low" : "";
      const deptLabel = (r.college ? r.college + " / " : "") + r.department;
      tbl += `<tr>
        <td class="num ${rateCls}">${r.rate.toFixed(2)}</td>
        <td class="num">${r.quota}/${r.applicants}</td>
        <td>${escapeHtml(r.university)}</td>
        <td>${escapeHtml(r.admission_type)}</td>
        <td>${escapeHtml(deptLabel)}</td>
      </tr>`;
    });
    tbl += `</tbody></table>`;
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
  major: "all",            // all / major / other  (주요대학 = 상위50)
  unis: new Set(),         // empty = all
  maxRate: 2.0,
  minQuota: 1,
  q: "",
  sortKey: "rate",
  sortDir: 1,              // 1 asc, -1 desc
};

// --- 초기화: 칩/셀렉트 채우기 ------------------------------------------------
function unique(field) {
  return [...new Set(DATA.map(r => r[field]))].filter(x => x !== "")
    .sort((a, b) => a.localeCompare(b, "ko"));
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
      render();
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
      render();
    };
    regionEl.appendChild(el);
  });

  document.querySelectorAll("#chips-oq .chip").forEach(el => {
    el.onclick = () => {
      document.querySelectorAll("#chips-oq .chip").forEach(x => x.classList.remove("on"));
      el.classList.add("on");
      state.oq = el.dataset.v;
      render();
    };
  });

  document.querySelectorAll("#chips-major .chip").forEach(el => {
    el.onclick = () => {
      document.querySelectorAll("#chips-major .chip").forEach(x => x.classList.remove("on"));
      el.classList.add("on");
      state.major = el.dataset.v;
      render();
    };
  });

  initUniPanel();

  document.getElementById("max-rate").oninput = e => {
    state.maxRate = parseFloat(e.target.value) || 2.0; render();
  };
  document.getElementById("min-quota").oninput = e => {
    state.minQuota = parseInt(e.target.value) || 1; render();
  };
  document.getElementById("search").oninput = e => {
    state.q = e.target.value.trim(); render();
  };
  document.getElementById("reset").onclick = () => {
    state.types.clear(); state.regions.clear(); state.oq = "all";
    state.major = "all"; state.unis.clear();
    state.maxRate = 2.0; state.minQuota = 1; state.q = "";
    document.querySelectorAll("#chips-type .chip").forEach(x => x.classList.add("on"));
    document.querySelectorAll("#chips-region .chip").forEach(x => x.classList.add("on"));
    document.querySelectorAll("#chips-oq .chip").forEach(x =>
      x.classList.toggle("on", x.dataset.v === "all"));
    document.querySelectorAll("#chips-major .chip").forEach(x =>
      x.classList.toggle("on", x.dataset.v === "all"));
    document.getElementById("uni-search").value = "";
    document.querySelectorAll("#uni-list .uni-item").forEach(x => { x.hidden = false; });
    syncUniChecks(); syncUniLabel();
    document.getElementById("max-rate").value = 2.0;
    document.getElementById("min-quota").value = 1;
    document.getElementById("search").value = "";
    render();
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
      render();
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
      render();
    };
  });
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
  return DATA.filter(r => {
    if (state.types.size && !state.types.has(r["전형세부유형"])) return false;
    if (state.regions.size && !state.regions.has(r.region)) return false;
    if (state.oq === "in" && r["정원외"] === "O") return false;
    if (state.oq === "out" && r["정원외"] !== "O") return false;
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
  const oq = rows.filter(r => r["정원외"] === "O").length;
  el.innerHTML = `
    <div class="stat"><div class="k">필터 결과</div><div class="v">${rows.length}</div></div>
    <div class="stat"><div class="k">대학 수</div><div class="v">${uniCount}</div></div>
    <div class="stat"><div class="k">미달 &lt;1.0</div><div class="v" style="color:var(--good)">${under1}</div></div>
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
  rows.forEach(r => {
    const tr = document.createElement("tr");
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
      <td>${r["주요대학"] === "O" ? '<span class="major-star">★</span>' : ""}${escapeHtml(r.university)}</td>
      <td><span class="tag ${cls}">${r["전형세부유형"]}</span></td>
      <td>${r["정원외"] || ""}</td>
      <td>${escapeHtml(r.admission_type)}</td>
      <td>${escapeHtml(r.college)}</td>
      <td>${escapeHtml(r.department)}</td>
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
render();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
