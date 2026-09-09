"""
'top50_univ100_2026.txt' 순위표에 있는 대학만 골라서
농특·논술 · 서울/경기/충청 · 경쟁률 <2.0 결과와 교집합을 만든다.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

HERE = Path(__file__).parent
RANK_FILE = HERE / "top50_univ100_2026.txt"
DEPT_CSV = HERE / "susi_2027_nong_nonsul_low.csv"
OUT_CSV = HERE / "susi_2027_top50_nong_nonsul.csv"

# 약칭 → 정식명(내 CSV의 표기와 일치해야 함) 예외 사전.
# 매핑되지 않은 이름은 자동 규칙(대→대학교, 여대→여자대학교)으로 처리.
NAME_ALIASES = {
    "서울대": "서울대학교",
    "카이스트": "한국과학기술원",
    "포스텍": "포항공과대학교",
    "유니스트": "울산과학기술원",
    "디지스트": "대구경북과학기술원",
    "지스트": "광주과학기술원",
    "켄텍": "한국에너지공과대학교",
    "서울과기대": "서울과학기술대학교",
    "서울시립대": "서울시립대학교",
    "한국외대": "한국외국어대학교",
    "한국교통대": "국립한국교통대학교",
    "한국항공대": "한국항공대학교",
    "한국공학대": "한국공학대학교",
}


def short_to_full(short: str) -> str:
    if short in NAME_ALIASES:
        return NAME_ALIASES[short]
    if short.endswith("여대"):
        return short[:-2] + "여자대학교"
    if short.endswith("대"):
        return short + "학교"
    return short


def parse_rank_line(line: str) -> tuple[int, str, list[str]] | None:
    """Return (rank, short_name, campus_hints)."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    # "1\t서울대(서울/경기)" or "1. 서울대(서울/경기)"
    m = re.match(r"^(\d+)[\.\t\s]+([^\(]+?)(?:\(([^)]+)\))?\s*$", line)
    if not m:
        return None
    rank = int(m.group(1))
    short = m.group(2).strip()
    hints = [h.strip() for h in (m.group(3) or "").split("/") if h.strip()]
    return rank, short, hints


def load_ranks(top_n: int = 50) -> dict[tuple[str, str | None], int]:
    """
    Build a map from (full_name, campus_key_or_None) -> rank.

    - 순위표에 지역이 하나면 (full, region) 로 등록 → 캠퍼스 매칭
    - 여러 지역이면 (full, None) 로 등록 → 어느 캠퍼스든 매칭
    """
    ranks: dict[tuple[str, str | None], int] = {}
    for line in RANK_FILE.read_text(encoding="utf-8").splitlines():
        parsed = parse_rank_line(line)
        if not parsed:
            continue
        rank, short, hints = parsed
        if rank > top_n:
            break
        full = short_to_full(short)
        if len(hints) == 1:
            ranks[(full, hints[0])] = rank
        else:
            ranks[(full, None)] = rank
    return ranks


def uni_match(uni_name: str, uni_region: str,
              ranks: dict[tuple[str, str | None], int]) -> int | None:
    """Return the rank if this CSV university matches an entry, else None."""
    # Strip trailing '(캠퍼스)' from the CSV name.
    m = re.match(r"^([^(]+?)\s*(?:\(([^)]+)\))?\s*$", uni_name)
    if not m:
        return None
    base = m.group(1).strip()
    campus = (m.group(2) or "").strip()

    # 1) Exact-campus rank (e.g. 고려대(세종), 연세대(강원))
    #    We match by both region and campus keyword to avoid confusing branches.
    for (rank_full, rank_hint), r in ranks.items():
        if rank_full != base:
            continue
        if rank_hint is None:
            # multi-region entry — any campus qualifies
            return r
        # single-region entry: match either the region in ranking hint (지역)
        # or a campus-name substring inside the CSV's paren.
        if uni_region == rank_hint or rank_hint in campus:
            return r
    return None


def main() -> int:
    ranks = load_ranks(50)
    print(f"[i] 순위표 로드: {len(ranks)}개 항목 (top 50)", file=sys.stderr)

    with DEPT_CSV.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    print(f"[i] 소스 CSV 로드: {len(rows)}개 학과", file=sys.stderr)

    matched: list[dict] = []
    for r in rows:
        rank = uni_match(r["university"], r["region"], ranks)
        if rank is not None:
            r = dict(r)
            r["rank"] = rank
            matched.append(r)

    matched.sort(key=lambda x: (float(x["rate"]), x["rank"]))
    print(f"[i] top50 대학에 속한 학과: {len(matched)}", file=sys.stderr)

    # 대학별 확인
    from collections import Counter
    seen = Counter((r["rank"], r["university"]) for r in matched)
    unmatched_ranks = set(range(1, 51)) - {rk for (rk, _) in seen}
    print(f"[i] top50 중 매칭 학과가 있는 대학: {len({u for (_, u) in seen})}", file=sys.stderr)
    if unmatched_ranks:
        print(f"[i] 매칭 없는 순위: {sorted(unmatched_ranks)}", file=sys.stderr)

    with OUT_CSV.open("w", newline="", encoding="utf-8-sig") as f:
        fields = ["rank"] + [k for k in matched[0].keys() if k != "rank"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(matched)
    print(f"[i] 결과 저장: {OUT_CSV}", file=sys.stderr)

    # 콘솔 표
    print()
    print(f"{'순위':>4}  {'경쟁률':>6}  {'모집':>4}  {'지원':>4}  "
          f"{'지역':<4}  {'대학':<18}  {'전형':<24}  {'학과'}")
    print("-" * 130)
    for i, d in enumerate(matched, 1):
        print(
            f"{d['rank']:>4}  {float(d['rate']):>6.2f}  {int(d['quota']):>4}  "
            f"{int(d['applicants']):>4}  {d['region']:<4}  "
            f"{d['university'][:18]:<18}  {d['admission_type'][:24]:<24}  "
            f"{(d['college'] + ' / ' if d['college'] else '') + d['department']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
