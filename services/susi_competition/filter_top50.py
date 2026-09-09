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
EXCLUDE_FILE = HERE / "exclusions.txt"
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


def load_exclusions() -> tuple[set[str], set[tuple[str, str]], bool]:
    """
    Return (exclude_all_campuses, exclude_specific_campuses, exclude_women_univ).
    - exclude_all_campuses:  {"홍익대학교", ...}  — 캠퍼스 무관 전체 제외
    - exclude_specific:      {("고려대학교", "세종"), ...}
    - exclude_women:         True 면 '여자대학교'로 끝나는 모든 대학 제외
    """
    if not EXCLUDE_FILE.exists():
        return set(), set(), False
    all_camp: set[str] = set()
    spec: set[tuple[str, str]] = set()
    women = False
    for raw in EXCLUDE_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line == "all_women_univ":
            women = True
            continue
        m = re.match(r"^([^(]+?)\s*(?:\(([^)]+)\))?\s*$", line)
        if not m:
            continue
        base = m.group(1).strip()
        campus = (m.group(2) or "").strip()
        if campus:
            spec.add((base, campus))
        else:
            all_camp.add(base)
    return all_camp, spec, women


def is_excluded(uni_name: str,
                excl_all: set[str],
                excl_spec: set[tuple[str, str]],
                excl_women: bool) -> bool:
    m = re.match(r"^([^(]+?)\s*(?:\(([^)]+)\))?\s*$", uni_name)
    if not m:
        return False
    base = m.group(1).strip()
    campus = (m.group(2) or "").strip()
    if base in excl_all:
        return True
    if (base, campus) in excl_spec:
        return True
    if excl_women and base.endswith("여자대학교"):
        return True
    return False


# ---------------------------------------------------------------------------
# 전형 태깅
# ---------------------------------------------------------------------------
# 대학마다 표기가 다양해서 (12+가지) Excel에서 걸러 볼 수 있도록 태그를 붙인다.
#
# 전형대분류:   논술 | 농어촌
# 전형세부유형: 논술 | 농어촌_교과 | 농어촌_종합 | 농어촌_일반 | 기회균형_혼합
# 정원외:       O | (빈 값=정원내)
#
# 특히 '기회균형_혼합' 은 "농어촌" 이 이름에 있지만 국가보훈/수급자/자립아동
# 등 다른 자격 지원자도 함께 경쟁하는 통합 전형(예: 경희대 기회균형전형Ⅰ).

_OTHER_ELIGIBILITY_TOKENS = (
    "국가보훈", "보훈", "수급자", "기초생활", "차상위",
    "자립", "다문화", "특성화", "특수교육", "장애",
    "서해5도", "북한이탈", "새터민",
)


def tag_admission(admission_type: str) -> tuple[str, str, str]:
    """Return (전형대분류, 전형세부유형, 정원외)."""
    t = admission_type
    is_out_of_quota = ("정원외" in t) or ("정원 외" in t)
    out_flag = "O" if is_out_of_quota else ""

    if "논술" in t:
        return "논술", "논술", out_flag

    # 농어촌 계열
    if "농어촌" in t or "농특" in t:
        # 다른 자격이 함께 나열되어 있으면 '기회균형 혼합'.
        # ('농어촌 및 특수교육대상자' 같이 다른 자격 토큰이 등장하는 경우 포함)
        if any(tok in t for tok in _OTHER_ELIGIBILITY_TOKENS):
            return "농어촌", "기회균형_혼합", out_flag
        # 학생부교과 vs 학생부종합 vs 기타로 세분.
        if "학생부교과" in t or "교과" in t:
            # '(교과)' 표기(가천대 '농어촌(교과) 전형' 등)와
            # '학생부교과(농어촌학생전형)' 를 모두 잡는다.
            return "농어촌", "농어촌_교과", out_flag
        if "학생부종합" in t or "(종합)" in t or "종합" in t:
            return "농어촌", "농어촌_종합", out_flag
        return "농어촌", "농어촌_일반", out_flag

    return "기타", "기타", out_flag


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

    excl_all, excl_spec, excl_women = load_exclusions()
    print(f"[i] 제외 규칙: 전체캠퍼스={sorted(excl_all)} / 특정캠퍼스={sorted(excl_spec)}"
          f" / 여대전체={excl_women}", file=sys.stderr)

    with DEPT_CSV.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    print(f"[i] 소스 CSV 로드: {len(rows)}개 학과", file=sys.stderr)

    matched: list[dict] = []
    excluded_hits = 0
    for r in rows:
        rank = uni_match(r["university"], r["region"], ranks)
        if rank is None:
            continue
        if is_excluded(r["university"], excl_all, excl_spec, excl_women):
            excluded_hits += 1
            continue
        r = dict(r)
        r["rank"] = rank
        r["전형대분류"], r["전형세부유형"], r["정원외"] = tag_admission(r["admission_type"])
        matched.append(r)
    print(f"[i] 제외 규칙에 걸린 학과: {excluded_hits}", file=sys.stderr)

    matched.sort(key=lambda x: (float(x["rate"]), x["rank"]))
    print(f"[i] top50 대학에 속한 학과: {len(matched)}", file=sys.stderr)

    # 대학별 확인
    from collections import Counter
    seen = Counter((r["rank"], r["university"]) for r in matched)
    unmatched_ranks = set(range(1, 51)) - {rk for (rk, _) in seen}
    print(f"[i] top50 중 매칭 학과가 있는 대학: {len({u for (_, u) in seen})}", file=sys.stderr)
    if unmatched_ranks:
        print(f"[i] 매칭 없는 순위: {sorted(unmatched_ranks)}", file=sys.stderr)

    # 태그 분포 요약
    from collections import Counter
    tag_dist = Counter(r["전형세부유형"] for r in matched)
    print(f"[i] 전형세부유형 분포: {dict(tag_dist)}", file=sys.stderr)

    ordered = ["rank", "전형대분류", "전형세부유형", "정원외"]
    with OUT_CSV.open("w", newline="", encoding="utf-8-sig") as f:
        fields = ordered + [k for k in matched[0].keys() if k not in ordered]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(matched)
    print(f"[i] 결과 저장: {OUT_CSV}", file=sys.stderr)

    # 콘솔 표 (상위 50)
    print()
    print(f"{'#':>3}  {'순위':>3}  {'경쟁률':>5}  {'모/지':>5}  "
          f"{'지역':<4}  {'세부유형':<10}  {'정외':<3}  "
          f"{'대학':<15}  {'학과'}")
    print("-" * 130)
    for i, d in enumerate(matched[:50], 1):
        mj = f"{int(d['quota'])}/{int(d['applicants'])}"
        dept = (d['college'] + ' / ' if d['college'] else '') + d['department']
        print(
            f"{i:>3}  #{d['rank']:>2}  {float(d['rate']):>5.2f}  {mj:>5}  "
            f"{d['region']:<4}  {d['전형세부유형']:<10}  {d['정원외']:<3}  "
            f"{d['university'][:15]:<15}  {dept[:55]}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
