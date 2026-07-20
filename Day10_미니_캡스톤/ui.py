"""TabeTabi — Streamlit 채팅 UI.

실행: streamlit run ui.py
"""
from __future__ import annotations

import asyncio
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
import streamlit as st

from tabetabi.agents.concierge import concierge_reply, run_pipeline
from tabetabi.config import DEFAULT_MODEL, TAVILY_API_KEY
from tabetabi.contract import TripContract
from tabetabi.render import itinerary_md, map_points
from tabetabi.tools.tabelog_server import db_stats

st.set_page_config(page_title="TabeTabi — 미식 여행 컨시어지", page_icon="🍜", layout="wide")

GREETING = """안녕하세요! 🍜 **TabeTabi 미식 여행 컨시어지**입니다.

타베로그 고신뢰 리뷰어 데이터(유니크 식당 **45,725곳**)를 기반으로, 맛집을 중심에 둔 여행 일정을 만들어 드려요.

이렇게 말씀해 보세요:

> 8월 22일부터 23일까지 도쿄 1박 2일, 성인 2명이야. 라멘·스시·야키니쿠 좋아하고 저녁 예산은 1인 8,000엔 이하. 1일차 점심은 'らぁ麺や 嶋'로 고정해줘. 신주쿠 쪽에서 묵을 예정이고 서울에서 출발해!

가고 싶은 식당·장소·일정을 **고정**하시면 그대로 반영하고, 나머지만 추천해 드립니다."""

ss = st.session_state
if "msgs" not in ss:
    ss.msgs = [{"role": "assistant", "content": GREETING}]
    ss.draft = {}
    ss.ready = False
    ss.itinerary = None
    ss.map_df = None
    ss.logs = []

# ---------- 사이드바 ----------
with st.sidebar:
    st.title("🍜 TabeTabi")
    st.caption("멀티에이전트 미식 여행 컨시어지 · Day10 미니 캡스톤")
    stats = db_stats()
    c1, c2 = st.columns(2)
    c1.metric("식당 데이터", f"{stats['restaurants']:,}곳")
    c2.metric("지역(pref)", f"{stats['prefs']}개")
    st.caption(f"LLM: `{DEFAULT_MODEL}` · NVIDIA NIM")
    if TAVILY_API_KEY:
        st.success("웹검색: Tavily 활성", icon="🔎")
    else:
        st.warning("웹검색: 폴백 모드 — .env에 TAVILY_API_KEY 추가", icon="🔗")
    st.divider()
    st.subheader("📋 SHARED CONTRACT")
    if ss.draft:
        st.markdown(TripContract.from_dict(ss.draft).summary_md())
    else:
        st.caption("대화를 시작하면 계약이 여기에 채워집니다.")
    st.divider()
    with st.expander("👥 에이전트 팀 구성"):
        st.markdown(
            "- **@concierge** — 대화·계약·병합 지휘\n"
            "- **@foodie** — Tabelog DB MCP _(DB 도구만)_\n"
            "- **@scout** — 웹검색 MCP _(검색 도구만)_\n"
            "- **@critic** — 읽기 전용 검증 게이트\n\n"
            "허용 도구 목록 = 권한 경계 (Day9 원칙)"
        )
    if st.button("🔄 대화 초기화", use_container_width=True):
        for k in ("msgs", "draft", "ready", "itinerary", "map_df", "logs"):
            ss.pop(k, None)
        st.rerun()

# ---------- 대화 표시 ----------
for m in ss.msgs:
    with st.chat_message(m["role"], avatar="🍜" if m["role"] == "assistant" else None):
        st.markdown(m["content"])

if ss.map_df is not None and len(ss.map_df):
    st.caption("📍 추천 식당 위치 (최인접 역 기준)")
    st.map(ss.map_df)
if ss.logs:
    with st.expander(f"🔍 에이전트 실행 로그 ({len(ss.logs)}건)"):
        st.code("\n".join(ss.logs), language=None)

# ---------- 일정 생성 버튼 ----------
if ss.ready and ss.itinerary is None:
    if st.button("🚀 이 계약으로 일정 생성 — 에이전트 팀 출동", type="primary", use_container_width=True):
        contract = TripContract.from_dict(ss.draft)
        logs: list[str] = []
        try:
            with st.status("🤝 에이전트 팀 작업 중… (@foodie ∥ @scout 병렬)", expanded=True) as status:
                def log(s: str):
                    logs.append(s)
                    status.write(s)
                it = asyncio.run(run_pipeline(contract, log=log))
                status.update(label="✅ 일정 완성!", state="complete")
            ss.itinerary = it
            ss.logs = logs
            ss.msgs.append({"role": "assistant", "content": itinerary_md(it)})
            pts = map_points(it)
            ss.map_df = pd.DataFrame(pts)[["lat", "lon"]] if pts else None
            st.rerun()
        except Exception:
            ss.logs = logs
            st.error("일정 생성 중 오류가 발생했어요. 아래 상세를 확인해 주세요.")
            st.code(traceback.format_exc()[-1500:])

if ss.itinerary is not None:
    if st.button("♻️ 조건을 바꿔 다시 생성 (대화로 조건 수정 후 클릭)", use_container_width=True):
        ss.itinerary = None
        ss.map_df = None
        st.rerun()

# ---------- 채팅 입력 ----------
prompt = st.chat_input("여행 계획을 말씀해 주세요…")
if prompt:
    ss.msgs.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="🍜"):
        with st.spinner("@concierge 생각 중…"):
            history = [m for m in ss.msgs if m["role"] in ("user", "assistant")]
            reply, draft, ready = asyncio.run(concierge_reply(history, ss.draft))
        st.markdown(reply)
    ss.msgs.append({"role": "assistant", "content": reply})
    ss.draft = draft
    ss.ready = ready
    st.rerun()
