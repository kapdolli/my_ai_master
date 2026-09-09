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
    r = requests.get(APP_URL, timeout=30, allow_redirects=True)
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


# Column header aliases across providers (진학사 uses 대학; 유웨이 uses 계열).
_COLLEGE_HEADERS = {"대학", "계열", "단과대학"}
_HDR_UNIT = "모집단위"
_HDR_QUOTA = "모집인원"
_HDR_APPS = "지원인원"
_HDR_RATE = "경쟁률"


def _fetch_comp_page(url: str) -> str:
    key = re.sub(r"[^0-9A-Za-z]+", "_", url)[-80:]
    cache_file = CACHE_DIR / f"comp_{key}.html"
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8")
    r = requests.get(url, timeout=30)
    r.raise_for_status()
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
    html: str, university: str, region: str, founder: str
) -> list[Department]:
    soup = BeautifulSoup(html, "html.parser")
    out: list[Department] = []

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
            tds = tr.find_all("td")
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

            if len(cells) < 4:
                continue
            dept_name = cells[0].get_text(" ", strip=True)
            quota = _parse_int(cells[1].get_text())
            apps = _parse_int(cells[2].get_text())
            rate = _parse_rate(cells[3].get_text())
            if dept_name in {"", "총계", "소계", "합계", "계"}:
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
            html = _fetch_comp_page(u["comp2027"])
            return parse_departments(
                html,
                university=u.get("name", "?"),
                region=u.get("region", "?"),
                founder=u.get("founder", ""),
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
    p.add_argument("--csv", type=Path, default=Path(__file__).parent / "susi_2027_low_competition.csv",
                   help="CSV 저장 경로")
    args = p.parse_args(argv)

    t0 = time.time()
    html = fetch_main_page(force_refresh=args.refresh)
    universities = extract_universities(html)
    print(f"[i] 총 {len(universities)}개 대학 등록됨", file=sys.stderr)

    depts = collect(universities, args.regions, args.workers, args.include_zero_apps)
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
