"""
2027학년도 수시 경쟁률 낮은 학과 검색기
- 데이터 출처: 경기도교육청 Apps Script (2027 수시전형 경쟁률 검색기)
- 학과별 경쟁률: addon.jinhakapply.com (진학사)

사용법:
    python find_low_competition.py                       # 서울/경기/충청 전체
    python find_low_competition.py --regions 서울 경기    # 특정 지역
    python find_low_competition.py --top 50              # 상위 50개
    python find_low_competition.py --max-rate 1.0        # 경쟁률 1.0 미만
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import json
import re
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

import requests
from bs4 import BeautifulSoup

# Windows consoles default to CP949 which chokes on em-dashes / Korean glyphs.
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

APP_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbyqBz_2PLml1gqDcEryFNyLMsPwW_OE6tVQx7nUUBnhznfOv9CWP0NfX5khzqiBga2amw/exec"
)

DEFAULT_REGIONS = ["서울", "경기", "인천", "충남", "충북", "대전", "세종"]

CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Extract university list embedded in the Apps Script HTML
# ---------------------------------------------------------------------------

_JS_ESCAPES = {
    "n": "\n", "r": "\r", "t": "\t", "b": "\b", "f": "\f",
    "/": "/", '"': '"', "'": "'", "\\": "\\", "`": "`",
    "0": "\0",
}
_ESC_RE = re.compile(r"\\(x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}|.)", re.DOTALL)


def _js_unescape(text: str) -> str:
    def repl(m: re.Match) -> str:
        e = m.group(1)
        if e[0] == "x":
            return chr(int(e[1:], 16))
        if e[0] == "u":
            return chr(int(e[1:], 16))
        return _JS_ESCAPES.get(e, e)
    return _ESC_RE.sub(repl, text)


def fetch_main_page(force_refresh: bool = False) -> str:
    cache_file = CACHE_DIR / "main_page.html"
    if cache_file.exists() and not force_refresh:
        return cache_file.read_text(encoding="utf-8")
    r = requests.get(APP_URL, timeout=30, allow_redirects=True, headers=_HTTP_HEADERS)
    r.raise_for_status()
    cache_file.write_text(r.text, encoding="utf-8")
    return r.text


def extract_universities(html: str) -> list[dict]:
    """Extract the university list from the doubly-escaped BOOTSTRAP JSON in the page."""
    # The BOOTSTRAP block is embedded as a JS string literal that itself
    # contains JS source, which itself contains a JSON.parse-style literal.
    # Two rounds of JS-string unescaping restore valid JSON.
    idx = html.find("const BOOTSTRAP")
    if idx < 0:
        raise RuntimeError("BOOTSTRAP not found in page — the site markup may have changed.")

    # Slice a chunk generous enough to contain the full data array.
    end_idx = html.find(r"\x3c\\/script\x3e", idx)
    if end_idx < 0:
        end_idx = idx + 2_000_000
    chunk = html[idx:end_idx]

    # Round 1: outer JS-string unescape.
    stage1 = _js_unescape(chunk)
    # Round 2: inner JSON escape unescape (\", \\, \/, \n ...).
    stage2 = _js_unescape(stage1)

    # After two rounds we have valid JS such as:
    #   const BOOTSTRAP = {"ok":true,"data":[ {...}, {...} ]};
    m = re.search(r"const\s+BOOTSTRAP\s*=\s*(\{.*?\})\s*;", stage2, re.DOTALL)
    if not m:
        raise RuntimeError("Could not locate BOOTSTRAP object literal after unescaping.")
    obj = json.loads(m.group(1))
    return obj.get("data", [])


# ---------------------------------------------------------------------------
# 2. Parse a jinhakapply competition-rate page
# ---------------------------------------------------------------------------

@dataclass
class Department:
    region: str
    founder: str  # 국립/사립 ...
    university: str
    admission_type: str  # 학생부교과, 학생부종합 etc.
    college: str          # 단과대 (may be empty)
    department: str       # 모집단위
    quota: int
    applicants: int
    rate: float           # 경쟁률 (지원인원/모집인원)
    # 원서 마감 — 대학 단위 값 (경기도교육청 BOOTSTRAP 의 lastday/lasttime).
    deadline_day: str = ""    # 예: "9.11.(금)"
    deadline_time: str = ""   # 예: "18:00" (드물게 "16:00(송도)/18:00(강화)")
    # 경쟁률 페이지 자체가 알려주는 값 (대학·제공사마다 다르다).
    rate_asof: str = ""       # 표시된 경쟁률의 기준시각. 예: "09-09 21:00"
    rate_until: str = ""      # 경쟁률 공개 종료 시각. 예: "9/11 11:00" (모르면 빈 값)
    rate_notice: str = ""     # 근거가 된 안내 문구 원문 (툴팁용)


# ---------------------------------------------------------------------------
# 2-a. 경쟁률 페이지가 스스로 알려주는 기준시각 / 공개 종료 시각
# ---------------------------------------------------------------------------
# 대학마다 경쟁률을 갱신·공개하는 시간대가 제각각이다. 예:
#   진학사 "2026-09-09 오후 9:00 현황" / 유웨이 "2026년 09월 09일 21시 00분 기준"
#   "경쟁률은 9월 11일(금) 오전 11시까지만 제공되며 ..."
#   "경쟁률은 원서접수 마감일 15시까지 제공됩니다."
#   "경쟁률은 10분 단위로 업데이트 됩니다.(단, 원서접수 마감일은 12:00까지 공개)"
# 파싱에 실패하면 빈 값으로 두고 원문(rate_notice)만 넘긴다 — 추측하지 않는다.

_ASOF_JINHAK = re.compile(r"(\d{4})-(\d{1,2})-(\d{1,2})\s*(오전|오후)\s*(\d{1,2}):(\d{2})")
_ASOF_UWAY = re.compile(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일\s*(\d{1,2})시\s*(\d{1,2})분")

# 경쟁률 공개 종료를 말하는 문장만 추린다 (갱신 주기 안내와 구분).
_NOTICE_SPLIT = re.compile(r"[※□■●▶]")
# 안내 문구 뒤에 페이지 본문이 이어붙는 경우가 있어 여기서 끊는다.
_CUT_RE = re.compile(
    r"(원서접수 바로가기|대학홈페이지|입학처|\d{4}-\d{1,2}-\d{1,2}\s*(?:오전|오후)"
    r"|\d{4}년\s*\d{1,2}월\s*\d{1,2}일\s*\d{1,2}시)"
)
# "9시", "오후 4시", "17:00" 형태의 시각
_TIME_RE = re.compile(r"(오전|오후)?\s*(?:(\d{1,2})\s*시(?!간)(?:\s*(\d{1,2})\s*분)?|(\d{1,2}):(\d{2}))")


def _to_24h(ampm: str, hour: int) -> int:
    if ampm == "오후" and hour < 12:
        return hour + 12
    if ampm == "오전" and hour == 12:
        return 0
    return hour


def _extract_asof(text: str) -> str:
    m = _ASOF_JINHAK.search(text)
    if m:
        _, mon, day, ampm, hh, mm = m.groups()
        return f"{int(mon):02d}-{int(day):02d} {_to_24h(ampm, int(hh)):02d}:{mm}"
    m = _ASOF_UWAY.search(text)
    if m:
        _, mon, day, hh, mm = m.groups()
        return f"{int(mon):02d}-{int(day):02d} {int(hh):02d}:{int(mm):02d}"
    return ""


def _last_time(segment: str) -> tuple[int, int] | None:
    """구간 안의 마지막 시각. '10시, 14시만' → 14:00, '오후 4시' → 16:00."""
    found = None
    if "정오" in segment:
        found = (12, 0)
    for m in _TIME_RE.finditer(segment):
        ampm, h1, m1, h2, m2 = m.groups()
        if h1 is not None:
            hh, mm = int(h1), int(m1 or 0)
        else:
            hh, mm = int(h2), int(m2)
        if hh > 24 or mm > 59:
            continue
        found = (_to_24h(ampm or "", hh), mm)
    return found


# 원서접수 기간을 말하는 구절 — 경쟁률 공개 종료와 헷갈리면 안 된다.
_APPLY_WORDS = ("접수기간", "접수 기간", "모집기간", "모집 기간")
_RATE_WORDS = ("경쟁률", "현황")


def _extract_rate_until(text: str, deadline_day: str,
                        deadline_time: str = "") -> tuple[str, str]:
    """(경쟁률 공개 종료 라벨, 근거 문구). 확신이 없으면 ('', 문구) — 추측하지 않는다."""
    cands = []
    for raw in _NOTICE_SPLIT.split(text):
        if "경쟁률" not in raw:
            continue
        cut = _CUT_RE.search(raw)
        c = (raw[:cut.start()] if cut else raw).strip()
        if ("까지" in c or "만)" in c or re.search(r"시\s*만", c)
                or "마감시간" in c or "마감 시간" in c
                or ("마감일" in c and "갱신" in c)):
            cands.append(c)
    notice = " / ".join(c[:160] for c in cands[:2])

    dm = re.search(r"(\d{1,2})\s*\.\s*(\d{1,2})", deadline_day or "")
    dl = (int(dm.group(1)), int(dm.group(2))) if dm else None

    # "원서접수 마감 1시간 전까지 공지" — 마감시각에서 빼서 계산한다.
    dt = re.search(r"(\d{1,2}):(\d{2})", deadline_time or "")
    for c in cands:
        m = re.search(r"마감\s*(\d{1,2})\s*시간\s*전", c)
        if m and dl and dt:
            total = int(dt.group(1)) * 60 + int(dt.group(2)) - int(m.group(1)) * 60
            if total >= 0:
                return f"{dl[0]}/{dl[1]} {total // 60:02d}:{total % 60:02d}", notice

    for c in cands:
        seg = None
        for m in re.finditer("까지", c):
            k = m.start()
            anchor = max(c.rfind(w, 0, k) for w in _RATE_WORDS)
            if anchor >= 0:
                between = c[anchor:k]
                # "원서접수기간 … 17:00까지" 는 접수 마감이지 경쟁률 마감이 아니다.
                if not any(w in between for w in _APPLY_WORDS):
                    seg = between
                    break
            # "정오(12시)까지 경쟁률이 공지됩니다" — 경쟁률이 '까지' 뒤에 오는 표현.
            # 단, 그 '까지' 가 원서접수 기간 문구 안이면 접수 마감이지 경쟁률 마감이 아니다.
            if (any(w in c[k:k + 30] for w in _RATE_WORDS)
                    and not any(w in c[max(0, k - 60):k] for w in _APPLY_WORDS)):
                seg = c[:k]
                break
        if seg is None:
            for kw in ("마감시간", "마감 시간", "마감일"):
                k = c.find(kw)
                if k < 0:
                    continue
                # '입학원서접수 마감시간' 처럼 접수 얘기면 건너뛴다.
                lead = c[max(0, k - 60):k]
                if any(w in lead for w in _APPLY_WORDS) or "원서접수 마감시간" in c:
                    continue
                if not any(w in lead for w in _RATE_WORDS):
                    continue
                seg = c[k:]
                break
        if seg is None:
            continue

        t = _last_time(seg)
        if not t:
            continue
        hh, mm = t
        md = re.search(r"(\d{1,2})월\s*(\d{1,2})일", seg)
        if md:
            mon, day = int(md.group(1)), int(md.group(2))
        elif dl:
            mon, day = dl        # "마감일 15시까지" 처럼 날짜가 생략된 경우
        else:
            continue
        # 경쟁률 공개 종료는 원서 마감일에 일어난다. 날짜가 다르면 '1일차/2일차 …'
        # 같은 갱신 일정표를 잘못 읽은 것이므로 버린다.
        if dl and (mon, day) != dl:
            continue
        return f"{mon}/{day} {hh:02d}:{mm:02d}", notice
    return "", notice


# Column header aliases across providers (진학사 uses 대학; 유웨이 uses 계열).
_COLLEGE_HEADERS = {"대학", "계열", "단과대학"}
_HDR_UNIT = "모집단위"
_HDR_QUOTA = "모집인원"
_HDR_APPS = "지원인원"
_HDR_RATE = "경쟁률"


# Browser-like headers — some Korean admission servers 403 requests without them,
# which is what killed 60% of the universities in the GitHub Actions run.
_HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
}


# 경쟁률 페이지 캐시 수명(초). 기본 5분 — 한 번의 실행 안에서 1·2단계가 같은 대학을
# 두 번 받지 않게 해주면서, 10분 주기의 다음 실행은 반드시 새로 받게 한다.
# (만료가 없던 시절 캐시가 하루 종일 재사용되어 경쟁률이 갱신되지 않았다.)
DEFAULT_CACHE_TTL = 300.0


def _fetch_comp_page(url: str, cache_ttl: float = DEFAULT_CACHE_TTL) -> str:
    key = re.sub(r"[^0-9A-Za-z]+", "_", url)[-80:]
    cache_file = CACHE_DIR / f"comp_{key}.html"
    if cache_file.exists() and cache_ttl > 0:
        age = time.time() - cache_file.stat().st_mtime
        if age < cache_ttl:
            return cache_file.read_text(encoding="utf-8")

    # Retry on transient errors — jinhak/uway occasionally throw 503s under load.
    import time as _time
    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=30, headers=_HTTP_HEADERS)
            r.raise_for_status()
            break
        except Exception as e:
            last_exc = e
            if attempt < 2:
                _time.sleep(1.5 * (attempt + 1))
    else:
        raise last_exc  # type: ignore[misc]

    # Only trust r.encoding when the server actually declared a charset;
    # requests defaults to ISO-8859-1 for `text/html`, which mangles UTF-8.
    declared = None
    ctype = r.headers.get("Content-Type", "").lower()
    if "charset=" in ctype:
        declared = ctype.split("charset=", 1)[1].split(";", 1)[0].strip()
    r.encoding = declared or r.apparent_encoding or "utf-8"
    text = r.text
    cache_file.write_text(text, encoding="utf-8")
    return text


def _parse_rate(cell: str) -> float | None:
    m = re.search(r"([\d,]+(?:\.\d+)?)\s*:\s*1", cell)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None


def _parse_int(cell: str) -> int | None:
    # Require at least one digit — `[\d,]+` alone matches lone commas.
    m = re.search(r"\d[\d,]*", cell)
    if not m:
        return None
    try:
        return int(m.group(0).replace(",", ""))
    except ValueError:
        return None


def _table_headers(table) -> list[str]:
    """Return column headers from the first row that has any <th>."""
    thead = table.find("thead")
    if thead:
        first_tr = thead.find("tr")
    else:
        first_tr = table.find("tr")
    if not first_tr:
        return []
    return [th.get_text(" ", strip=True) for th in first_tr.find_all("th")]


def _unit_colspan(table) -> int:
    """Return colspan of the 모집단위 <th> — 성균관대 논술처럼 계열+학과 두
    셀을 하나의 논리적 모집단위로 묶는 케이스를 처리하기 위함."""
    thead = table.find("thead")
    first_tr = thead.find("tr") if thead else table.find("tr")
    if not first_tr:
        return 1
    for th in first_tr.find_all("th"):
        if th.get_text(" ", strip=True) == _HDR_UNIT:
            try:
                return int(th.get("colspan") or 1)
            except ValueError:
                return 1
    return 1


def _visible_tds(tr) -> list:
    """Skip <td style="display:none"> spacer cells (진학사 논술 테이블 패턴)."""
    out = []
    for td in tr.find_all("td"):
        style = (td.get("style") or "").lower().replace(" ", "")
        if "display:none" in style:
            continue
        out.append(td)
    return out


def _preceding_section_title(table) -> str:
    """Find the nearest heading (h2/h3) preceding this table, e.g. 전형 name."""
    node = table.previous_element
    while node is not None:
        try:
            name = getattr(node, "name", None)
        except Exception:
            name = None
        if name in {"h1", "h2", "h3", "h4"}:
            return node.get_text(" ", strip=True)
        node = node.previous_element
    return ""


def parse_departments(
    html: str, university: str, region: str, founder: str,
    deadline_day: str = "", deadline_time: str = "",
) -> list[Department]:
    soup = BeautifulSoup(html, "html.parser")
    out: list[Department] = []

    page_text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    rate_asof = _extract_asof(page_text)
    rate_until, rate_notice = _extract_rate_until(page_text, deadline_day, deadline_time)

    for table in soup.find_all("table"):
        headers = _table_headers(table)
        if _HDR_UNIT not in headers:
            continue
        needed = [_HDR_UNIT, _HDR_QUOTA, _HDR_APPS, _HDR_RATE]
        if not all(k in headers for k in needed):
            continue

        # Determine whether the first column is a college/category column
        # (rowspan-grouped). Both 진학사 and 유웨이 layouts put it first.
        college_hdr = headers[0] if headers[0] in _COLLEGE_HEADERS else ""
        has_college_col = bool(college_hdr)
        # 성균관대 논술처럼 모집단위가 colspan=2 (계열+학과 두 셀)인 케이스.
        unit_span = _unit_colspan(table)

        title = _preceding_section_title(table)
        # Strip trailing "경쟁률 현황" boilerplate but keep "[정원내]" etc.
        admission_type = re.sub(r"경쟁률\s*현황\s*$", "", title).strip()

        current_college = ""
        college_remaining = 0

        # Only iterate <tbody> rows if the table separates head/body,
        # otherwise fall back to all <tr>.
        body_rows = table.find("tbody")
        rows = body_rows.find_all("tr") if body_rows else table.find_all("tr")[1:]

        for tr in rows:
            tds = _visible_tds(tr)
            if not tds:
                continue

            cells = tds
            if has_college_col:
                if college_remaining <= 0:
                    first = tds[0]
                    span_attr = first.get("rowspan")
                    try:
                        rowspan = int(span_attr) if span_attr else 1
                    except ValueError:
                        rowspan = 1
                    current_college = first.get_text(" ", strip=True)
                    college_remaining = rowspan
                    cells = tds[1:]
                else:
                    cells = tds
                college_remaining -= 1

            # 모집단위가 colspan=2 이면 앞의 두 셀을 합쳐서 학과명 구성.
            if unit_span >= 2 and len(cells) >= 5:
                parts = [c.get_text(" ", strip=True) for c in cells[:2]]
                dept_name = " / ".join(p for p in parts if p) or parts[-1]
                q_idx, a_idx, r_idx = 2, 3, 4
            else:
                if len(cells) < 4:
                    continue
                dept_name = cells[0].get_text(" ", strip=True)
                q_idx, a_idx, r_idx = 1, 2, 3
            quota = _parse_int(cells[q_idx].get_text())
            apps = _parse_int(cells[a_idx].get_text())
            rate = _parse_rate(cells[r_idx].get_text())
            # '인문캠퍼스(서울) 소계' 처럼 앞에 수식어가 붙은 집계 행도 걸러낸다.
            # (모집 147명/지원 387명 같은 캠퍼스 합계가 학과인 척 섞여 있었다)
            if dept_name in {"", "총계", "소계", "합계", "계"} or                dept_name.endswith(("소계", "총계", "합계")):
                continue
            # Rows starting with 총계 header may contain <th> in tbody — skip.
            if not dept_name or quota is None or apps is None or rate is None:
                continue

            out.append(
                Department(
                    region=region,
                    founder=founder,
                    university=university,
                    admission_type=admission_type,
                    college=current_college if has_college_col else "",
                    department=dept_name,
                    quota=quota,
                    applicants=apps,
                    rate=rate,
                    deadline_day=deadline_day,
                    deadline_time=deadline_time,
                    rate_asof=rate_asof,
                    rate_until=rate_until,
                    rate_notice=rate_notice,
                )
            )
    return out


# ---------------------------------------------------------------------------
# 3. Orchestration
# ---------------------------------------------------------------------------

def collect(
    universities: list[dict],
    regions: Iterable[str],
    workers: int,
    include_zero_apps: bool,
    cache_ttl: float = DEFAULT_CACHE_TTL,
) -> list[Department]:
    region_set = set(regions)
    targets = [
        u for u in universities
        if u.get("region") in region_set and (u.get("comp2027") or "").startswith("http")
    ]
    print(f"[i] {len(targets)}개 대학의 2027 경쟁률 페이지를 수집합니다...", file=sys.stderr)

    results: list[Department] = []
    errors: list[tuple[str, str]] = []

    def _work(u: dict) -> list[Department]:
        try:
            html = _fetch_comp_page(u["comp2027"], cache_ttl)
            return parse_departments(
                html,
                university=u.get("name", "?"),
                region=u.get("region", "?"),
                founder=u.get("founder", ""),
                deadline_day=u.get("lastday", ""),
                deadline_time=u.get("lasttime", ""),
            )
        except Exception as exc:  # noqa: BLE001 — collect and continue
            errors.append((u.get("name", "?"), str(exc)))
            return []

    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for i, depts in enumerate(ex.map(_work, targets), 1):
            results.extend(depts)
            if i % 10 == 0:
                print(f"    {i}/{len(targets)}", file=sys.stderr)

    if not include_zero_apps:
        # A rate of 0 typically means applications haven't opened yet or
        # the department reports separately — drop them so we surface only
        # meaningfully low competition, not "no data".
        results = [d for d in results if d.applicants > 0]

    for name, msg in errors:
        print(f"[!] {name}: {msg}", file=sys.stderr)
    return results


def write_csv(rows: list[Department], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        w.writeheader()
        for r in rows:
            w.writerow(asdict(r))


def print_table(rows: list[Department], limit: int) -> None:
    print()
    print(f"{'순위':>4}  {'경쟁률':>7}  {'모집':>4}  {'지원':>4}  "
          f"{'지역':<4}  {'대학':<18}  {'전형':<28}  {'학과'}")
    print("-" * 130)
    for i, d in enumerate(rows[:limit], 1):
        print(
            f"{i:>4}  {d.rate:>7.2f}  {d.quota:>4}  {d.applicants:>4}  "
            f"{d.region:<4}  {d.university[:18]:<18}  "
            f"{d.admission_type[:28]:<28}  "
            f"{(d.college + ' / ' if d.college else '') + d.department}"
        )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--regions", nargs="+", default=DEFAULT_REGIONS,
                   help=f"검색 지역 (기본값: {' '.join(DEFAULT_REGIONS)})")
    p.add_argument("--top", type=int, default=30, help="화면에 출력할 상위 N개")
    p.add_argument("--max-rate", type=float, default=None,
                   help="이 경쟁률 미만인 학과만 (예: 1.0)")
    p.add_argument("--min-quota", type=int, default=1,
                   help="최소 모집인원 (기본 1)")
    p.add_argument("--admission-contains", nargs="+", default=None,
                   help="전형명에 이 키워드 중 하나가 들어간 학과만 (예: 농어촌 논술)")
    p.add_argument("--include-zero-apps", action="store_true",
                   help="지원자 0명 학과도 포함 (기본 제외 — 아직 미개시 케이스)")
    p.add_argument("--workers", type=int, default=12, help="병렬 다운로드 스레드 수")
    p.add_argument("--refresh", action="store_true", help="캐시 무시하고 다시 받기")
    p.add_argument("--cache-ttl", type=float, default=DEFAULT_CACHE_TTL,
                   help=f"경쟁률 페이지 캐시 수명(초, 기본 {DEFAULT_CACHE_TTL:.0f}). "
                        "--refresh 를 주면 0 으로 취급")
    p.add_argument("--csv", type=Path, default=Path(__file__).parent / "susi_2027_low_competition.csv",
                   help="CSV 저장 경로")
    args = p.parse_args(argv)

    t0 = time.time()
    html = fetch_main_page(force_refresh=args.refresh)
    universities = extract_universities(html)
    print(f"[i] 총 {len(universities)}개 대학 등록됨", file=sys.stderr)

    depts = collect(universities, args.regions, args.workers, args.include_zero_apps,
                    cache_ttl=0.0 if args.refresh else args.cache_ttl)
    depts = [d for d in depts if d.quota >= args.min_quota]
    if args.max_rate is not None:
        depts = [d for d in depts if d.rate < args.max_rate]
    if args.admission_contains:
        kws = args.admission_contains
        depts = [d for d in depts if any(k in d.admission_type for k in kws)]

    depts.sort(key=lambda d: (d.rate, -d.quota))
    print(f"[i] 필터 후 {len(depts)}개 학과 (총 소요 {time.time()-t0:.1f}s)", file=sys.stderr)

    if not depts:
        print("조건에 맞는 학과가 없습니다.")
        return 0

    write_csv(depts, args.csv)
    print(f"[i] 전체 결과 CSV: {args.csv}", file=sys.stderr)
    print_table(depts, args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
