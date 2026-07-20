"""TabeTabi 전역 설정 — 경로·API 키·LLM 클라이언트.

키 우선순위: .env(NVIDIA_API_KEY) → 수업 공용 03_RAG_Engineering/API.txt(NV_API_KEY).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent          # Day10_미니_캡스톤
COURSE_DIR = BASE_DIR.parent                               # 03_RAG_Engineering
TABELOG_DIR = Path(os.getenv("TABELOG_DIR") or r"C:\Users\GJ\Desktop\Nvidia_AI_Agent\Tabelog_Recommendation")

load_dotenv(BASE_DIR / ".env")

DB_PATH = Path(os.getenv("TABELOG_DB") or str(TABELOG_DIR / "app.db"))
STATION_COORDS_PATH = TABELOG_DIR / "data" / "station_coords.json"

# 검증된 기존 코드(Tabelog_Recommendation의 app.maplinks 등)를 import로 재사용
if TABELOG_DIR.exists() and str(TABELOG_DIR) not in sys.path:
    sys.path.insert(0, str(TABELOG_DIR))


def _load_nvidia_key() -> str:
    key = os.getenv("NVIDIA_API_KEY") or os.getenv("NV_API_KEY")
    if key:
        return key
    api_txt = COURSE_DIR / "API.txt"
    if api_txt.exists():
        for line in api_txt.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("NV_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError(
        "NVIDIA API 키를 찾지 못했습니다. Day10 .env의 NVIDIA_API_KEY 또는 03_RAG_Engineering/API.txt를 확인하세요."
    )


NVIDIA_API_KEY = _load_nvidia_key()
NIM_BASE_URL = os.getenv("NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "qwen/qwen3-next-80b-a3b-instruct")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") or ""

# qwen thinking 모드 비활성 (Day7 검증: 토큰 폭주 방지)
NO_THINK = {"chat_template_kwargs": {"enable_thinking": False}}

_llm = None


def get_llm():
    """AsyncOpenAI 클라이언트 (NVIDIA NIM). 전역 1개 재사용."""
    global _llm
    if _llm is None:
        from openai import AsyncOpenAI
        _llm = AsyncOpenAI(base_url=NIM_BASE_URL, api_key=NVIDIA_API_KEY)
    return _llm
