"""웹 API — 기존 CLI 교정 엔진을 그대로 재사용하는 FastAPI 서버.

PRD.md §4의 아키텍처 원칙("교정 로직은 CLI와 분리된 순수 라이브러리 모듈로 설계")을
그대로 활용한다. 여기서는 engine/parsers를 호출만 하고, 새 교정 로직은 추가하지 않는다.
"""

import tempfile
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles

from . import store
from .engine import correct_entries
from .parsers import parse_srt, write_srt

app = FastAPI(title="한국어 자막 교정 API")

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.post("/api/correct")
async def correct_subtitle(file: UploadFile):
    if not file.filename.lower().endswith(".srt"):
        raise HTTPException(400, "SRT 파일만 지원합니다.")

    raw = await file.read()
    with tempfile.TemporaryDirectory() as tmp:
        in_path = Path(tmp) / "input.srt"
        in_path.write_bytes(raw)

        entries = parse_srt(in_path)
        corrected_entries, flags, applied_log = correct_entries(entries)

        out_path = Path(tmp) / "output.srt"
        write_srt(corrected_entries, out_path)
        corrected_srt = out_path.read_text(encoding="utf-8")

    original_srt = raw.decode("utf-8-sig")
    report_id = store.save_report(
        original_srt=original_srt,
        corrected_srt=corrected_srt,
        flags=flags,
        applied_log=applied_log,
    )
    return {
        "id": report_id,
        "original_srt": original_srt,
        "corrected_srt": corrected_srt,
        "flags": [asdict(f) for f in flags],
        "applied_log": applied_log,
    }


@app.get("/api/reports/{report_id}")
def get_report(report_id: str):
    row = store.get_report(report_id)
    if not row:
        raise HTTPException(404, "해당 id의 리포트를 찾을 수 없습니다.")
    return row


# 정적 프론트엔드 (업로드 화면). API 라우트보다 아래에 있어야
# "/api/..." 요청이 정적 파일 서빙보다 먼저 매칭된다.
app.mount("/", StaticFiles(directory=_STATIC_DIR, html=True), name="static")
