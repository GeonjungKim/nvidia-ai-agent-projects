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

from tabetabi import store
from tabetabi.agents.concierge import ConciergeTurn, run_pipeline, swap_meal
from tabetabi.anchors import resolve_anchor
from tabetabi.config import DEFAULT_MODEL, TAVILY_API_KEY
from tabetabi.contract import MAX_TRIP_DAYS, TripContract
from tabetabi.i18n import DEFAULT_LANG, LANGS, t_area, t_genre, t_genres, t_station
from tabetabi.render import itinerary_md, map_points
from tabetabi.tools.tabelog_server import db_stats, list_areas, list_genres, pref_codes, search_lib

st.set_page_config(page_title="TabeTabi — 미식 여행 컨시어지", page_icon="🍜", layout="wide")


def _sync_stream(agen):
    """비동기 제너레이터(ConciergeTurn.stream())를 st.write_stream이 소비할 동기 제너레이터로 브릿지한다.

    각 토큰이 도착할 때마다 하나씩 꺼내 yield하므로 화면에 실시간으로 반영된다. 중간에 API 오류가
    나면 여기서 그대로 raise되어 호출부의 try/except가 잡는다 (이미 표시된 부분 텍스트는 남는다).
    """
    loop = asyncio.new_event_loop()
    try:
        while True:
            try:
                yield loop.run_until_complete(agen.__anext__())
            except StopAsyncIteration:
                break
    finally:
        loop.close()

GREETING = """안녕하세요! 🍜 **TabeTabi 미식 여행 컨시어지**입니다.

타베로그 고신뢰 리뷰어 데이터(유니크 식당 **45,725곳**)를 기반으로, 맛집을 중심에 둔 여행 일정을 만들어 드려요.

이렇게 말씀해 보세요:

> 8월 22일부터 23일까지 도쿄 1박 2일, 성인 2명이야. 라멘·스시·야키니쿠 좋아하고 저녁 예산은 1인 8,000엔 이하. 1일차 점심은 'らぁ麺や 嶋'로 고정해줘. 신주쿠 쪽에서 묵을 예정이고 서울에서 출발해!

가고 싶은 식당·장소·일정을 **고정**하시면 그대로 반영하고, 나머지만 추천해 드립니다."""

# ---------- 로그인 상태 (선택적 Google OAuth — .streamlit/secrets.toml에 [auth] 설정 시에만 활성화) ----------
try:
    AUTH_CONFIGURED = bool(st.secrets.get("auth", {}).get("client_id"))
except Exception:
    AUTH_CONFIGURED = False
LOGGED_IN = bool(AUTH_CONFIGURED and st.user.is_logged_in)
USER_KEY = st.user.email if LOGGED_IN else None       # None → 비로그인(익명) 모드
USER_LABEL = (st.user.name or st.user.email) if LOGGED_IN else "게스트"

ss = st.session_state

# ---------- 세션 식별 + DB에서 이어보기 (가점: DB 저장) ----------
if "session_id" not in ss:
    if LOGGED_IN:
        recent = store.list_sessions(USER_KEY, limit=1)
        ss.session_id = recent[0]["session_id"] if recent else store.new_session_id()
    else:
        if "sid" not in st.query_params:
            st.query_params["sid"] = store.new_session_id()
        ss.session_id = st.query_params["sid"]

if "msgs" not in ss:
    loaded = None
    try:
        loaded = store.load_session(ss.session_id)
    except Exception:
        loaded = None   # DB 조회 실패해도 빈 화면 대신 새 대화로 시작 (fail-soft)
    if loaded and loaded.get("messages"):
        ss.msgs = loaded["messages"]
        ss.draft = loaded.get("draft") or {}
        ss.itinerary = loaded.get("itinerary")
        ss.ready = TripContract.from_dict(ss.draft).is_ready() if ss.draft else False
    else:
        ss.msgs = [{"role": "assistant", "content": GREETING}]
        ss.draft = {}
        ss.ready = False
        ss.itinerary = None
    ss.map_df = None
    if ss.itinerary:
        pts = map_points(ss.itinerary)
        ss.map_df = pd.DataFrame(pts)[["lat", "lon"]] if pts else None
    ss.logs = []


def _persist_session() -> None:
    """현재 대화·계약·일정을 DB에 저장한다 — 채팅 턴·일정 생성 직후 호출."""
    try:
        store.save_session(ss.session_id, USER_KEY or ("anon:" + ss.session_id), USER_LABEL,
                           ss.draft, ss.msgs, ss.itinerary)
    except Exception:
        pass   # 저장 실패해도 현재 세션 동작에는 영향 없음 (fail-soft)

def _reset_view_state() -> None:
    """세션 전환·삭제 시 화면 상태를 비운다 — 다음 rerun에서 DB 기준으로 다시 로드된다."""
    for k in ("msgs", "draft", "ready", "itinerary", "map_df", "logs"):
        ss.pop(k, None)


if "lang" not in ss:
    ss.lang = DEFAULT_LANG

# ---------- 사이드바 (대화 목록을 최상단에 — ChatGPT/Claude식 내비게이션) ----------
with st.sidebar:
    st.title("🍜 TabeTabi")
    st.caption("멀티에이전트 미식 여행 컨시어지")

    # 표시 언어 — 장르·역·정기휴무 등 일본어 메타데이터를 선택 언어로 번역해 표시 (LLM 미사용)
    _lang_labels = list(LANGS.keys())
    _cur = next((lbl for lbl, code in LANGS.items() if code == ss.lang), _lang_labels[0])
    _pick = st.radio("🌐 표시 언어 / Language", _lang_labels,
                     index=_lang_labels.index(_cur), horizontal=True, key="lang_pick")
    if LANGS[_pick] != ss.lang:
        ss.lang = LANGS[_pick]
        # 이미 생성된 일정 메시지를 새 언어로 다시 렌더 (파이프라인 재실행 없이 — 결정론 사전 조회)
        if ss.get("itinerary"):
            for i in range(len(ss.msgs) - 1, -1, -1):
                if ss.msgs[i]["role"] == "assistant" and str(ss.msgs[i]["content"]).startswith("## 🗾"):
                    ss.msgs[i]["content"] = itinerary_md(ss.itinerary, ss.lang)
                    break
        st.rerun()

    if st.button("➕ 새 대화", type="primary", use_container_width=True):
        ss.session_id = store.new_session_id()
        if not LOGGED_IN:
            st.query_params["sid"] = ss.session_id
        _reset_view_state()
        st.rerun()

    # 대화 목록 — 항상 보이게, 클릭 한 번으로 전환·삭제 (expander에 숨기지 않는다)
    if LOGGED_IN:
        try:
            past = store.list_sessions(USER_KEY, limit=15)
        except Exception:
            past = []
        if past:
            st.subheader("💬 대화 목록")
            for s in past:
                current = s["session_id"] == ss.session_id
                icon = "📋 " if s["has_itinerary"] else ""
                col_open, col_del = st.columns([6, 1])
                if col_open.button(("▶ " if current else "") + icon + s["label"],
                                   key=f"sess_{s['session_id']}", disabled=current,
                                   use_container_width=True,
                                   help=f"마지막 수정 {s['updated_at'][:16].replace('T', ' ')} UTC"):
                    ss.session_id = s["session_id"]
                    _reset_view_state()
                    st.rerun()
                if col_del.button("🗑️", key=f"del_{s['session_id']}", help="이 대화 삭제"):
                    try:
                        store.delete_session(s["session_id"], USER_KEY)
                    except Exception:
                        pass
                    if current:
                        ss.session_id = store.new_session_id()
                        _reset_view_state()
                    st.rerun()
    else:
        st.caption("🔐 로그인하면 대화 목록이 계정에 보관되고, 여기서 바로 전환할 수 있어요.")

    st.divider()
    st.subheader("📋 SHARED CONTRACT")
    if ss.draft:
        st.markdown(TripContract.from_dict(ss.draft).summary_md(ss.lang))
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
    with st.expander("ℹ️ 데이터·모델 상태"):
        try:
            stats = db_stats()
            c1, c2 = st.columns(2)
            c1.metric("식당 데이터", f"{stats['restaurants']:,}곳")
            c2.metric("지역(pref)", f"{stats['prefs']}개")
        except Exception:
            st.error("타베로그 DB에 연결하지 못했어요 (TABELOG_DB 경로를 확인하세요).", icon="🛑")
        st.caption(f"LLM: `{DEFAULT_MODEL}` · NVIDIA NIM")
        if TAVILY_API_KEY:
            st.success("웹검색: Tavily 활성", icon="🔎")
        else:
            st.warning("웹검색: 폴백 모드 — .env에 TAVILY_API_KEY 추가", icon="🔗")

    st.divider()
    st.subheader("👤 계정")
    if not AUTH_CONFIGURED:
        st.caption("로그인 비활성 — 설정법: `LOGIN_SETUP.md`")
    elif LOGGED_IN:
        st.success(f"{USER_LABEL}", icon="✅")
        if st.button("로그아웃", use_container_width=True):
            st.logout()
    else:
        st.caption("로그인하면 대화 히스토리가 계정에 저장돼요.")
        if st.button("🔐 Google로 로그인", use_container_width=True):
            st.login()

# ---------- 탭: 대화 / 지역 랭킹 탐색 (D8) ----------
tab_chat, tab_rank = st.tabs(["💬 여행 계획", "📃 지역 랭킹 탐색"])

with tab_chat:
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
            # 부분 결과 우선 표시: 식당 라인업이 확정되는 즉시 이 자리에 잠정 표시된다
            # (최종 일정이 채팅에 붙으면 rerun으로 사라짐 — 실패 시엔 잠정 결과가 남는다, fail-soft)
            partial_box = st.empty()
            try:
                with st.status("🤝 에이전트 팀 작업 중… (@foodie ∥ @scout 병렬)", expanded=True) as status:
                    def log(s: str):
                        logs.append(s)
                        status.write(s)
                    it = asyncio.run(run_pipeline(
                        contract, log=log,
                        on_partial=lambda stage, md: partial_box.markdown(md)))
                    status.update(label="✅ 일정 완성!", state="complete")
                ss.itinerary = it
                ss.logs = logs
                ss.msgs.append({"role": "assistant", "content": itinerary_md(it, ss.lang)})
                pts = map_points(it)
                ss.map_df = pd.DataFrame(pts)[["lat", "lon"]] if pts else None
                _persist_session()
                st.rerun()
            except Exception:
                ss.logs = logs
                st.error("일정 생성 중 오류가 발생했어요. 아래 상세를 확인해 주세요. "
                         "(위에 잠정 라인업이 보인다면 거기까지는 확정된 결과예요)")
                st.code(traceback.format_exc()[-1500:])

    if ss.itinerary is not None:
        if st.button("♻️ 조건을 바꿔 다시 생성 (대화로 조건 수정 후 클릭)", use_container_width=True):
            ss.itinerary = None
            ss.map_df = None
            st.rerun()

        # 슬롯 즉시 교체 — 파이프라인이 계산해 둔 대안/제안으로 LLM 재호출 없이 바로 바꾼다
        _SLOT_KO = {"lunch": "점심", "cafe": "카페", "dinner": "저녁"}
        swap_rows = []
        for d in ss.itinerary.get("days", []):
            for m in d.get("meals", []):
                if m.get("locked") and not m.get("external"):
                    continue   # DB 고정 슬롯은 계약 — 교체 대상 제외
                pool = (m.get("alternatives") or []) + (m.get("suggestions") or [])
                alts = [a for a in pool if a.get("restaurant_id")]
                if alts:
                    swap_rows.append((d, m, alts))
        if swap_rows:
            with st.expander("🔀 슬롯 즉시 교체 — 대안으로 바로 바꾸기 (LLM 재호출 없음)"):
                for d, m, alts in swap_rows:
                    label = _SLOT_KO.get(m["slot"], m["slot"])
                    tag = " (DB 미등록 — 제안 채택 시 정식 확정)" if m.get("external") else ""
                    c1, c2, c3 = st.columns([4, 5, 1])
                    c1.markdown(f"**Day{d['day']} {label}**{tag}\n\n{m['name']}")
                    opts = [f"{a['name']}" + (f" ★{a['rating']}" if a.get("rating") else "")
                            + (f" · {a['station']}역" if a.get("station") else "") for a in alts]
                    sel = c2.selectbox("대안 선택", opts, key=f"swapsel_{d['day']}_{m['slot']}",
                                       label_visibility="collapsed")
                    if c3.button("교체", key=f"swapbtn_{d['day']}_{m['slot']}"):
                        a = alts[opts.index(sel)]
                        new_it = swap_meal(ss.itinerary, d["day"], m["slot"], a["restaurant_id"])
                        if new_it:
                            if m.get("external"):
                                # 제안 채택 → 계약의 고정 이름도 DB 정식 표기로 승격 (재생성 시 1단계 즉시 확정)
                                _alias = {"점심": "lunch", "런치": "lunch", "브런치": "lunch",
                                          "저녁": "dinner", "디너": "dinner", "카페": "cafe", "디저트": "cafe"}
                                locked = []
                                for lk in ss.draft.get("locked") or []:
                                    lk_slot = str(lk.get("slot") or "").strip().lower() if isinstance(lk, dict) else ""
                                    lk_slot = _alias.get(lk_slot, lk_slot)
                                    try:
                                        lk_day = int(lk.get("day") or 0) if isinstance(lk, dict) else 0
                                    except (ValueError, TypeError):
                                        lk_day = 0
                                    if isinstance(lk, dict) and lk_day == d["day"] and lk_slot == m["slot"]:
                                        lk = {**lk, "name": a["name"],
                                              "note": (str(lk.get("note") or "") + f" [사용자 확인: {a['name']}]").strip()}
                                    locked.append(lk)
                                ss.draft = {**ss.draft, "locked": locked}
                            ss.itinerary = new_it
                            for i in range(len(ss.msgs) - 1, -1, -1):   # 채팅의 일정 메시지도 갱신
                                if ss.msgs[i]["role"] == "assistant" and str(ss.msgs[i]["content"]).startswith("## 🗾"):
                                    ss.msgs[i]["content"] = itinerary_md(new_it, ss.lang)
                                    break
                            pts = map_points(new_it)
                            ss.map_df = pd.DataFrame(pts)[["lat", "lon"]] if pts else None
                            _persist_session()
                            st.rerun()
                st.caption("🔒 고정 슬롯은 계약이라 제외됩니다. 여기 없는 식당은 '📃 지역 랭킹 탐색' 탭에서 📌로 고정한 뒤 재생성하세요.")

    # ---------- 채팅 입력 (LLM 응답 실시간 스트리밍 + 오류 상태 처리) ----------
    prompt = st.chat_input("여행 계획을 말씀해 주세요…")
    if prompt:
        ss.msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant", avatar="🍜"):
            thinking = st.empty()
            thinking.markdown("🍜 *@concierge 생각 중…*")
            reply = draft = ready = None
            try:
                history = [m for m in ss.msgs if m["role"] in ("user", "assistant")]
                turn = ConciergeTurn(history, ss.draft)
                thinking.empty()
                if turn.shortcut:                     # D6 확인 응답 등 — 결정론 즉답, 스트리밍할 게 없음
                    st.markdown(turn.shortcut[0])
                else:
                    st.write_stream(_sync_stream(turn.stream()))
                reply, draft, ready = turn.result()
            except Exception:
                thinking.empty()
                st.error("응답을 생성하는 중 오류가 발생했어요 (네트워크 또는 API 문제일 수 있어요). 잠시 후 다시 시도해 주세요.")
                with st.expander("오류 상세"):
                    st.code(traceback.format_exc()[-1500:])
        if reply is not None:
            ss.msgs.append({"role": "assistant", "content": reply})
            ss.draft = draft
            ss.ready = ready
        else:
            ss.msgs.append({"role": "assistant", "content": "⚠️ 응답 생성에 실패했어요. 같은 메시지를 다시 보내 주세요."})
        _persist_session()
        st.rerun()

with tab_rank:
    # ---------- D8: 지역 랭킹 탐색 — 일정 생성과 무관하게 즉시 열람 (LLM 호출 0회) ----------
    st.subheader("📃 지역 랭킹 탐색")
    st.caption("타베로그 베이지안 랭킹을 그대로 노출합니다 — 일정 생성 없이도 즉시 응답 (LLM 미사용). "
               "계약이 있으면 **기본값만** 미리 채워질 뿐, 지역·앵커·장르 모두 자유롭게 바꿀 수 있어요.")

    try:
        contract_draft = TripContract.from_dict(ss.draft) if ss.draft else TripContract()
        pref_options = [p for p, _ in pref_codes()]
    except Exception:
        st.error("타베로그 DB 조회에 실패했어요. 잠시 후 탭을 다시 열어 주세요.", icon="🛑")
        pref_options = []

    if not pref_options:
        st.info("표시할 지역 데이터가 없어요.")
    else:
        default_pref = contract_draft.pref if contract_draft.pref in pref_options else pref_options[0]
        pref_sel = st.selectbox("지역", pref_options, index=pref_options.index(default_pref) if default_pref in pref_options else 0,
                                key="rank_pref")

        # 앵커 선택지 = 계약 앵커(기본값 편의) + 해당 pref의 DB 세부지역 상위 30 + 직접 입력.
        # 계약이 있어도 선택지가 계약 지역에 갇히지 않는다 — 탐색 탭은 자유 열람이 목적.
        contract_anchors = []
        if contract_draft.pref == pref_sel:
            contract_anchors = [a for a in contract_draft.effective_day_anchors().values() if a] \
                + contract_draft.areas \
                + ([contract_draft.stay_area] if contract_draft.stay_area else [])
        try:
            db_areas = [a["area2"] for a in list_areas(pref_sel)]
        except Exception:
            db_areas = []
        anchor_pool = list(dict.fromkeys(contract_anchors + db_areas))
        # 값은 코드/역명(검색 키), 표시만 선택 언어로 번역 (A1301 → '긴자·유라쿠초 일대')
        anchor_choice = st.selectbox(
            "앵커(역/세부지역)", ["(전체)"] + anchor_pool, key="rank_anchor",
            format_func=lambda v: "(전체)" if v == "(전체)" else t_area(v, ss.lang, pref=pref_sel))
        custom_anchor = st.text_input("목록에 없는 역/지명 직접 입력 (일본어 표기 — 예: 中野, 吉祥寺, 恵比寿)",
                                      key="rank_anchor_custom",
                                      help="입력하면 위 선택보다 우선 적용됩니다. 비우면 위 선택을 따라요.")
        chosen_anchor = custom_anchor.strip() or ("" if anchor_choice == "(전체)" else anchor_choice)
        anchor_kwargs: dict = {}
        try:
            if chosen_anchor:
                info = resolve_anchor(pref_sel, chosen_anchor)
                anchor_kwargs = info.get("search_kwargs") or {}
                # 로그의 원시 코드 대신 번역 지명으로 안내 (UX)
                st.caption(f"📍 {t_area(chosen_anchor, ss.lang, pref=pref_sel)} · 매칭 {info.get('count', 0):,}곳")

            genre_rows = list_genres(pref_sel, anchor_kwargs.get("area2"))
        except Exception:
            st.error("장르 목록을 불러오지 못했어요.", icon="🛑")
            genre_rows = []
        genre_options = [g["genre"] for g in genre_rows]
        default_genres = [g for g in contract_draft.genres_pref if g in genre_options]
        # 값은 일본어 원문(검색 키), 표시만 선택 언어로 번역 (format_func)
        genre_sel = st.multiselect("장르 (복수 선택 가능 — 계약의 선호 장르가 미리 선택돼 있어요)",
                                   genre_options, default=default_genres, key="rank_genres",
                                   format_func=lambda g: t_genre(g, ss.lang))

        c1, c2, c3 = st.columns(3)
        budget = c1.number_input("저녁 예산 상한(엔, 0=제한 없음)", min_value=0, step=500,
                                 value=contract_draft.max_dinner_budget or 0, key="rank_budget")
        sort_sel = c2.selectbox("정렬", ["bayes", "rating", "reviews"], key="rank_sort")
        n_show = c3.selectbox("표시 개수", [10, 20, 30, 50], index=2, key="rank_limit")

        with st.spinner("검색 중…"):
            try:
                if genre_sel:
                    seen_ids: set = set()
                    results = []
                    for g in genre_sel:
                        for r in search_lib(pref=pref_sel, genre=g, max_dinner_budget=budget or None,
                                            sort=sort_sel, limit=n_show, **anchor_kwargs):
                            if r["restaurant_id"] not in seen_ids:
                                seen_ids.add(r["restaurant_id"])
                                results.append(r)
                    results.sort(key=lambda r: (r.get("bayes_score") is None, -(r.get("bayes_score") or 0)))
                    results = results[:n_show]
                else:
                    results = search_lib(pref=pref_sel, max_dinner_budget=budget or None, sort=sort_sel,
                                         limit=n_show, **anchor_kwargs)
            except Exception:
                st.error("랭킹 조회 중 오류가 발생했어요. 필터를 바꿔 다시 시도해 주세요.", icon="🛑")
                results = []

        if not results:
            st.info("조건에 맞는 식당이 없어요 — 필터를 완화해 보세요.")
        else:
            # 📌 고정: 자유 텍스트 이름 매칭의 근본 대체 — DB 정식 표기가 계약에 직접 들어가
            # 매칭 불확실성이 0이 된다 (external 문제 원천 차단)
            st.caption(f"상위 {len(results)}곳 — 각 행의 📌 버튼으로 일정 계약에 바로 고정할 수 있어요")
            _SLOT_KO_RANK = {"lunch": "점심", "cafe": "카페", "dinner": "저녁"}
            nd = contract_draft.num_days or 0
            pc1, pc2 = st.columns(2)
            pin_day = pc1.number_input("고정할 일차 (Day)", min_value=1, max_value=nd if nd else MAX_TRIP_DAYS,
                                       value=1, key="pin_day")
            pin_slot = pc2.selectbox("고정할 슬롯", ["lunch", "cafe", "dinner"],
                                     format_func=lambda s: _SLOT_KO_RANK[s], key="pin_slot")
            if ss.get("pin_done"):
                st.success(ss.pop("pin_done"))
            for r in results:
                rating = f"★{r['tabelog_rating']}" if r.get("tabelog_rating") else "★-"
                reviews = f"{r['tabelog_review_count']:,}" if r.get("tabelog_review_count") else "0"
                bayes = f" · 신뢰점수 {r['bayes_score']}" if r.get("bayes_score") else ""
                budget_txt = f" · 저녁 {r['budget_dinner']}" if r.get("budget_dinner") else ""
                station = f" · {t_station(r['stations'][0], ss.lang)}" if r.get("stations") else ""
                rc1, rc2 = st.columns([12, 1])
                rc1.markdown(
                    f"- [{r['name']}]({r['tabelog_url']}) — {t_genres(r.get('genres', ''), ss.lang)} · {rating}({reviews}){bayes}{budget_txt}{station}"
                    f" · [📍 지도]({r['gmap']})"
                )
                if rc2.button("📌", key=f"pin_{r['restaurant_id']}",
                              help=f"Day{pin_day} {_SLOT_KO_RANK[pin_slot]}에 이 식당을 고정"):
                    draft = dict(ss.draft or {})
                    if not draft.get("pref"):
                        draft["pref"] = pref_sel   # 계약이 비어 있으면 탐색 중인 지역으로 시작
                    locked = [l for l in (draft.get("locked") or [])
                              if not (isinstance(l, dict) and str(l.get("slot") or "") == pin_slot
                                      and str(l.get("day") or "") in (str(pin_day), str(int(pin_day))))]
                    locked.append({"day": int(pin_day), "slot": pin_slot, "name": r["name"],
                                   "note": "[사용자 확인: 랭킹 탐색에서 직접 지정]"})
                    draft["locked"] = locked
                    ss.draft = draft
                    ss.ready = TripContract.from_dict(draft).is_ready()
                    ss.pin_done = (f"📌 Day{pin_day} {_SLOT_KO_RANK[pin_slot]} 고정: {r['name']} — "
                                   "'💬 여행 계획' 탭에서 일정을 (재)생성하면 반영돼요."
                                   + ("" if ss.ready else " (지역·날짜를 채팅으로 알려주시면 생성 버튼이 열려요)"))
                    _persist_session()
                    st.rerun()
