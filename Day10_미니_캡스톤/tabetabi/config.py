"""TabeTabi 전역 설정 — 경로·API 키·LLM 클라이언트.

키 우선순위: .env(NVIDIA_API_KEY) → 수업 공용 03_RAG_Engineering/API.txt(NV_API_KEY).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent          # Day10_미니_캡스톤
COURSE_DIR = BASE_DIR.parent                               # 리포 루트 (03_RAG_Engineering)

load_dotenv(BASE_DIR / ".env")


def conf(name: str) -> str:
    """설정값 조회: 환경변수 → Streamlit secrets 순.

    Streamlit Community Cloud는 Secrets를 st.secrets로 주입하는데, 환경변수 매핑이
    보장되지 않아 os.getenv만 보면 배포에서 키를 못 찾는다 (실측: NVIDIA 키 미발견 크래시).
    CLI(run_demo 등)처럼 streamlit이 없거나 secrets 파일이 없으면 조용히 빈 문자열.
    """
    v = os.getenv(name)
    if v:
        return v
    try:
        import streamlit as st
        return str(st.secrets.get(name, "") or "")
    except Exception:
        return ""


def _find_tabelog_dir() -> Path:
    """Tabelog_Recommendation 위치 자동 탐지: 설정값 → 리포 내 형제 폴더 → 레거시 로컬 경로.

    배포(리눅스 마운트)에서는 리포 루트의 형제 폴더가 정답이라, TABELOG_DIR을 안 넣어도 동작한다.
    """
    configured = conf("TABELOG_DIR")
    candidates = [Path(configured)] if configured else []
    candidates += [COURSE_DIR / "Tabelog_Recommendation",
                   Path(r"C:\Users\GJ\Desktop\Nvidia_AI_Agent\Tabelog_Recommendation")]
    for c in candidates:
        if (c / "app.db").exists():
            return c
    return candidates[0]   # 못 찾으면 첫 후보 — DB 연결 시점에 친절한 에러가 난다


TABELOG_DIR = _find_tabelog_dir()

DB_PATH = Path(conf("TABELOG_DB") or str(TABELOG_DIR / "app.db"))
STATION_COORDS_PATH = TABELOG_DIR / "data" / "station_coords.json"

# 검증된 기존 코드(Tabelog_Recommendation의 app.maplinks 등)를 import로 재사용
if TABELOG_DIR.exists() and str(TABELOG_DIR) not in sys.path:
    sys.path.insert(0, str(TABELOG_DIR))


def _load_nvidia_key() -> str:
    key = conf("NVIDIA_API_KEY") or conf("NV_API_KEY")
    if key:
        return key
    api_txt = COURSE_DIR / "API.txt"
    if api_txt.exists():
        for line in api_txt.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("NV_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError(
        "NVIDIA API 키를 찾지 못했습니다. 로컬은 Day10 .env의 NVIDIA_API_KEY, "
        "Streamlit Cloud는 앱 Settings → Secrets에 NVIDIA_API_KEY를 넣어주세요."
    )


NVIDIA_API_KEY = _load_nvidia_key()
NIM_BASE_URL = conf("NIM_BASE_URL") or "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = conf("LLM_MODEL") or "qwen/qwen3-next-80b-a3b-instruct"
TAVILY_API_KEY = conf("TAVILY_API_KEY")

# qwen thinking 모드 비활성 (Day7 검증: 토큰 폭주 방지)
NO_THINK = {"chat_template_kwargs": {"enable_thinking": False}}

_llm = None


def get_llm():
    """AsyncOpenAI 클라이언트 (NVIDIA NIM). 전역 1개 재사용."""
    global _llm
    if _llm is None:
        from openai import AsyncOpenAI
        # timeout: NIM 장애(DEGRADED) 시 응답이 무기한 안 오는 행 상태가 관측됨 — 기본 600초 대신
        # 120초에서 끊어 APITimeoutError(→ APIConnectionError)로 만들고 루프의 백오프 재시도에 태운다.
        _llm = AsyncOpenAI(base_url=NIM_BASE_URL, api_key=NVIDIA_API_KEY,
                           timeout=float(os.getenv("LLM_TIMEOUT", "120")), max_retries=0)
    return _llm
