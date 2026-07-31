"""로컬 실행: 아이디어 서치 에이전트.

매일 18:00 KST에 Windows 작업 스케줄러로 이 스크립트를 실행하면
`claude -p` (Claude Code CLI 헤드리스 모드)로 리포트를 생성하고
텔레그램 봇 API로 직접 발송한다.

Anthropic API 키가 아니라 Claude Code subscription 인증을 사용한다.
`claude setup-token` 으로 한 번 로그인해두면 이후 헤드리스로 계속 돈다.

Usage:
    python run_local.py                # 정상 실행
    python run_local.py --dry-run      # 리포트만 생성, 텔레그램 발송은 생략
    python run_local.py --show-cmd     # 실제로 실행할 claude 명령을 출력하고 종료

환경변수:
    CLAUDE_BIN            claude CLI 실행 파일 경로 (기본 "claude")
    IDEA_SEARCH_MODEL     예: sonnet, opus, claude-sonnet-4-6 (미지정 시 subscription 기본)
    IDEA_SEARCH_TIMEOUT   초 단위 (기본 900 = 15분)
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent.parent
PROMPT_FILE = BASE_DIR / "prompt.md"
LOG_DIR = BASE_DIR / "logs"

TELEGRAM_CONFIG = REPO_ROOT / "shared" / "telegram" / "config.local.json"

CLAUDE_BIN = os.environ.get("CLAUDE_BIN", "claude")
MODEL = os.environ.get("IDEA_SEARCH_MODEL", "").strip()
TIMEOUT = int(os.environ.get("IDEA_SEARCH_TIMEOUT", "900"))
TELEGRAM_CHUNK = 3800
KST = datetime.timezone(datetime.timedelta(hours=9))


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def build_prompt(today_kst: datetime.date) -> str:
    body = PROMPT_FILE.read_text(encoding="utf-8")
    header = (
        f"오늘 날짜(KST): {today_kst.isoformat()}\n\n"
        "아래는 아이디어 서치 에이전트의 실행 사양이다. "
        "STEP 1(검색)과 STEP 2(분석·평가)를 수행한 뒤, "
        "STEP 3에 정의된 리포트 포맷 그대로 최종 응답 텍스트로 출력하라. "
        "발송/전송 코드는 실행하지 않는다 — 로컬 스크립트가 이 응답 본문을 받아 텔레그램으로 보낸다.\n\n"
        "----\n\n"
    )
    return header + body


def build_claude_cmd() -> list[str]:
    cmd = [CLAUDE_BIN, "-p", "--output-format", "text"]
    if MODEL:
        cmd += ["--model", MODEL]
    return cmd


def generate_report(prompt: str) -> str:
    cmd = build_claude_cmd()
    print(f"[claude] exec: {' '.join(cmd)} (stdin={len(prompt)} chars, timeout={TIMEOUT}s)")
    try:
        proc = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=TIMEOUT,
        )
    except FileNotFoundError as e:
        raise RuntimeError(
            f"claude CLI를 찾을 수 없다: {CLAUDE_BIN!r}. "
            "PATH에 claude가 있는지 확인하거나 CLAUDE_BIN 환경변수로 절대경로를 지정하라."
        ) from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"claude CLI 응답 대기 시간 초과 ({TIMEOUT}s)") from e

    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()
        raise RuntimeError(f"claude CLI 실패 (exit={proc.returncode}): {stderr[:500]}")

    return (proc.stdout or "").strip()


def chunk_text(text: str, size: int) -> list[str]:
    chunks: list[str] = []
    remaining = text
    while remaining:
        if len(remaining) <= size:
            chunks.append(remaining)
            break
        cutoff = remaining.rfind("\n", 0, size)
        if cutoff < size // 2:
            cutoff = size
        chunks.append(remaining[:cutoff])
        remaining = remaining[cutoff:].lstrip("\n")
    return chunks


def send_telegram(report: str, cfg: dict) -> None:
    token = cfg["bot_token"]
    chat_id = cfg["chat_id"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    chunks = chunk_text(report, TELEGRAM_CHUNK)
    for i, chunk in enumerate(chunks, 1):
        payload = json.dumps({"chat_id": chat_id, "text": chunk}).encode("utf-8")
        req = urlrequest.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            with urlrequest.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
                if resp.status != 200:
                    raise RuntimeError(f"telegram HTTP {resp.status}: {body}")
        except HTTPError as e:
            raise RuntimeError(
                f"telegram HTTP {e.code}: {e.read().decode('utf-8', 'replace')}"
            ) from e
        except URLError as e:
            raise RuntimeError(f"telegram URL error: {e}") from e
        print(f"[telegram] chunk {i}/{len(chunks)} sent ({len(chunk)} chars)")


def write_log(today_kst: datetime.date, report: str, status: str) -> Path:
    LOG_DIR.mkdir(exist_ok=True)
    log_path = LOG_DIR / f"{today_kst.isoformat()}.md"
    log_path.write_text(
        f"# {today_kst.isoformat()} — {status}\n\n{report}\n",
        encoding="utf-8",
    )
    return log_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="텔레그램 발송 생략")
    parser.add_argument(
        "--show-cmd",
        action="store_true",
        help="실행할 claude 명령만 출력하고 종료(진단용)",
    )
    args = parser.parse_args()

    if args.show_cmd:
        print(" ".join(build_claude_cmd()))
        return 0

    today = datetime.datetime.now(KST).date()
    print(f"[start] {today} claude_bin={CLAUDE_BIN} model={MODEL or '(default)'} dry_run={args.dry_run}")

    prompt = build_prompt(today)
    report = generate_report(prompt)
    if not report:
        write_log(today, "(빈 응답)", "empty")
        print("[error] 리포트 본문이 비었다", file=sys.stderr)
        return 2

    log_path = write_log(today, report, "generated")
    print(f"[log] {log_path} ({len(report)} chars)")

    if args.dry_run:
        print("[dry-run] 텔레그램 발송 생략")
        return 0

    if not TELEGRAM_CONFIG.exists():
        print(
            f"[error] {TELEGRAM_CONFIG} 이 없다. shared/telegram/README.md 참조",
            file=sys.stderr,
        )
        return 1
    telegram_cfg = load_json(TELEGRAM_CONFIG)
    send_telegram(report, telegram_cfg)
    print("[done]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
