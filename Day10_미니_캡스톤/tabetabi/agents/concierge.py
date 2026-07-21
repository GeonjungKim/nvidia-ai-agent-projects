"""@concierge — 대화로 SHARED CONTRACT를 완성하고 에이전트 팀을 지휘한다.

파이프라인 (Day9 Lab3의 배치 구조를 런타임에 적용):
  계약 고정
  → 배치1: @foodie ∥ @scout 병렬 (asyncio.gather)
  → 병합: 도구 없는 LLM이 슬롯별 최종 선정 — 후보 밖 선택은 '코드'가 교정
  → 게이트: @critic 읽기 전용 검증 — 불합격 시 병합 1회 재시도 (self-correction)
  → 로지스틱스: 동선 NN 정렬·지도 경로·항공/숙소 딥링크 (결정론 — 계산은 코드로)
"""
from __future__ import annotations

import asyncio
import json
import re
from dataclasses import asdict
from datetime import date

from tabetabi import timemodel
from tabetabi.agents.critic import run_critic
from tabetabi.agents.foodie import run_foodie
from tabetabi.agents.loop import plain_chat, stream_chat
from tabetabi.agents.scout import run_scout
from tabetabi.anchors import deviation_km, off_anchor_label, resolve_anchor
from tabetabi.contract import MAX_TRIP_DAYS, TripContract, extract_json
from tabetabi.geo import order_day_route
from tabetabi.links import (city_of, external_place_link, external_web_search_link,
                            flight_links, google_search_url, hotel_links)
from tabetabi.places import places_resolve
from tabetabi.resolve import resolve_place
from tabetabi.tools.tabelog_server import fetch_by_ids, pref_codes, search_lib

_SLOT_ORDER = ("lunch", "cafe", "dinner")

# 품질 하한 게이트 (D5, 실측 기반: ≥50/≥3.4 → 재고 11,484곳). 희소 지역은 라벨 달고 완화.
QUALITY_MIN_REVIEWS, QUALITY_MIN_BAYES = 50, 3.4
QUALITY_RELAX_REVIEWS, QUALITY_RELAX_BAYES = 20, 3.3
# 저녁 슬롯 배제 대상 테이크아웃/반찬 업태 (실측 빈도: 弁当1632·惣菜1258·コロッケ232)
_TAKEOUT_GENRES = {"弁当", "惣菜", "デリカテッセン", "コロッケ", "からあげ", "お持ち帰り"}

_pref_hint_cache: str | None = None


def _pref_hint() -> str:
    global _pref_hint_cache
    if _pref_hint_cache is None:
        _pref_hint_cache = ", ".join(f"{p}({n:,})" for p, n in pref_codes()[:20])
    return _pref_hint_cache


CONCIERGE_SYSTEM = """너는 'TabeTabi' 미식 여행 컨시어지다. 사용자와 한국어로 대화하며 여행 계약(contract)을 완성한다.
- 필수: pref(지역 코드), start_date/end_date(YYYY-MM-DD). 선택: areas(세부지역, 일본어 지명), stay_area(숙소역), day_anchors, theme_park, origin(출발 도시), party(인원), max_dinner_budget(저녁 1인 예산, 엔 숫자), max_lunch_budget(점심 1인 예산, 엔 숫자), genres_pref(일본어 장르), arrival_time/departure_time(HH:MM), locked, notes.
- **예산**: "점심 2000엔"은 max_lunch_budget:2000, "저녁 4000엔 이하"는 max_dinner_budget:4000 처럼 각각 넣는다. 코드가 이 상한을 강제하니 반드시 숫자로 채운다.
- **항공 시간**: 첫날 현지 도착 시각은 arrival_time, 마지막날 귀국편 출발 시각은 departure_time에 HH:MM으로 넣는다. "아침 비행기로 도착"→"10:00", "밤 9시 출발 귀국편"→"21:00"처럼 대략값도 좋다. 언급이 없으면 비워둔다 (일정은 기본 가정으로 만들어진다 — 굳이 캐묻지 마라).
- 사용자가 언급한 '고정' 식당·장소·일정은 반드시 locked 배열에 넣는다: {"day": 1부터(미정 0), "slot": "lunch|dinner|activity|stay", "name": "...", "note": "..."}. 이건 절대 바꾸면 안 되는 약속이다.
- **숙소**: "○○역 쪽에서 묵을 예정"·"○○에 숙소" 같은 말은 stay_area(일본어 역/지명)에 넣는다. notes에만 남기지 마라. 예: "고마고메역 쪽" → stay_area:"駒込". (locked의 stay 슬롯으로 들어와도 stay_area로 승격된다.)
- **일자별 앵커(day_anchors)**: {"1":"表参道","2":"駒込"}처럼 각 날의 중심 지역. 고정 식당·장소가 있는 날은 그 지역, 마지막 날은 stay_area 인접, 나머지는 areas 순환으로 제안한다. 사용자가 대화로 수정하면 반영한다. 지정 안 하면 비워둬도 코드가 자동 채운다.
- **중요 — 앵커는 pref(지역) 안의 지명만 쓴다**: 이 앱의 식당 DB는 pref 하나만 검색한다. 사용자가 pref 밖(다른 都道府県)의 근교 나들이를 말하면(예: 도쿄 여행 중 요코하마=가나가와, 가와구치코=야마나시, 가와고에=사이타마), 그날 식당 앵커로 pref 밖 지명을 넣지 마라. 대신 그날은 stay_area나 pref 안 지역을 앵커로 두고, 근교 나들이 계획은 notes에만 적는다. (pref 밖 지명을 앵커로 넣으면 엉뚱한 지역 식당이 추천된다 — 지금은 pref 교차 여행을 지원하지 않는다고 reply에서 정직하게 안내한다.)
- **theme_park**: 디즈니랜드/USJ 등 종일형 테마파크를 하루 통째로 원하면 true.
- 사용 가능한 pref 코드(식당 수): «PREFS»
- genres_pref는 타베로그 장르 표기(일본어)로 변환한다: 라멘→ラーメン, 스시→寿司, 야키니쿠→焼肉, 이자카야→居酒屋, 카페→カフェ.
- areas·stay_area·day_anchors는 일본어 지명으로 쓴다. 한국어 지명은 일본어 표기로 변환한다 (신주쿠→新宿, 긴자→銀座, 오모테산도→表参道, 고마고메→駒込).
- 오늘은 «TODAY»다. 상대 날짜는 이 기준으로 해석한다.
- pref와 날짜가 갖춰지면 즉시 ready=true. 선택 정보(예산·취향 등)를 더 캐묻지 말고, reply에 계약 요약(숙소 앵커·일자별 앵커 포함)과 "일정 생성 버튼을 눌러주세요" 안내를 담는다. 빠진 선택 정보는 알아서 기본값으로 진행한다고 말한다.
- 필수 정보가 빠졌을 때만 1~2개를 자연어로 묻는다 (예시는 자연스러운 문장으로).
- **출력 형식(중요, 화면 실시간 스트리밍용)**: 코드펜스·JSON 없이 사용자에게 보일 한국어 답변을 '순수 텍스트'로 먼저 쓴다.
  그 다음 줄에 구분자 `<<<CONTRACT>>>` 만 단독으로 쓰고, 그 다음 줄부터 계약 JSON 하나만 쓴다: {"contract": {전체 갱신본}, "ready": true/false}.
  구분자 앞의 텍스트에는 JSON·중괄호를 절대 섞지 마라 — 그 부분만 화면에 실시간으로 노출된다.
  예:
  안녕하세요! 도쿄 여행이시군요. 날짜만 알려주시면 바로 준비할게요.
  <<<CONTRACT>>>
  {"contract": {...}, "ready": false}"""

_CONTRACT_MARKER = "<<<CONTRACT>>>"


def _finalize_reply(raw: str, draft: dict) -> tuple[str, dict, bool]:
    """모델 원문(마커 이전 순수 텍스트 + 마커 이후 JSON)을 (답변, 갱신된 계약, ready)로 정리한다.

    스트리밍·비스트리밍 양쪽에서 공유하는 후처리 — 코드가 최종 판단(ready·D6 확인 필요)을 내린다.
    """
    if _CONTRACT_MARKER in raw:
        reply_part, _, rest = raw.partition(_CONTRACT_MARKER)
    else:
        reply_part, rest = raw, ""
    reply = reply_part.strip() \
        or "죄송해요, 한 번만 다시 말씀해 주시겠어요? (어느 지역으로 언제 가시는지가 필요해요)"
    data = extract_json(rest) or {}
    new_draft = data.get("contract") if isinstance(data.get("contract"), dict) else draft
    # ready 판정은 코드가 한다 — 필수(pref·날짜)가 갖춰지면 생성 버튼을 연다 (모델의 과잉 질문 방지)
    c = TripContract.from_dict(new_draft)
    ready = c.is_ready()
    if not ready and c.pref and c.num_days_raw > MAX_TRIP_DAYS:
        # 조용한 실패 금지: 기간 초과로 버튼이 안 열리는 이유를 반드시 사용자에게 알린다
        # (실사례: 15일 여행이 구 상한 14일에 걸려 안내 없이 버튼만 사라짐)
        reply += (f"\n\n⚠️ 한 번에 만들 수 있는 일정은 최대 **{MAX_TRIP_DAYS}일**이에요. "
                  f"지금 기간은 {c.num_days_raw}일이라 생성 버튼이 열리지 않아요 — "
                  "기간을 나눠서 (예: \"전반부 8/19~8/25로 먼저 짜줘\") 요청해 주시면 차례로 만들어 드릴게요.")
    if ready:
        pend = pending_lock_confirmations(new_draft)
        if pend:   # D6: 고정 장소 매칭이 불확실(4단계)하면 생성 전에 반드시 확인받는다
            ready = False
            reply = reply + "\n\n" + _confirm_question(pend[0])
    return reply, new_draft, ready


def _pending_confirm_shortcut(history: list[dict], draft: dict) -> tuple[str, dict, bool] | None:
    """D6: 고정 장소 확인 대기 중이면 LLM을 거치지 않고 코드가 사용자 답변을 직접 해석한다
    (자유 서술 재해석은 오탐 위험 — 번호/그대로만 받는 좁은 질문이라 결정론이 더 정확하다).
    해당 없으면 None (호출부가 평소대로 LLM을 호출하게 한다)."""
    if not history or history[-1]["role"] != "user":
        return None
    pend_before = pending_lock_confirmations(draft)
    if not pend_before:
        return None
    draft = _apply_lock_confirm_reply(draft, str(history[-1]["content"]), pend_before)
    pend_after = pending_lock_confirmations(draft)
    if pend_after:
        return _confirm_question(pend_after[0]), draft, False
    reply = "확인 감사합니다! 계약에 반영했어요.\n\n" + TripContract.from_dict(draft).summary_md()
    ready = TripContract.from_dict(draft).is_ready()
    return reply, draft, ready


def _concierge_prompt(history: list[dict], draft: dict) -> tuple[str, str]:
    system = (CONCIERGE_SYSTEM
              .replace("«PREFS»", _pref_hint())
              .replace("«TODAY»", date.today().isoformat()))
    convo = "\n".join(f"{m['role']}: {str(m['content'])[:500]}" for m in history[-12:])
    user = (
        f"현재 계약 초안 JSON:\n{json.dumps(draft, ensure_ascii=False)}\n\n"
        f"지금까지 대화:\n{convo}\n\n위 형식(텍스트 답변 → {_CONTRACT_MARKER} → JSON)으로 출력:"
    )
    return system, user


async def concierge_reply(history: list[dict], draft: dict) -> tuple[str, dict, bool]:
    """대화 1턴 처리 (비스트리밍) — (답변, 갱신된 계약 초안, ready 여부). 테스트·비UI 호출용."""
    shortcut = _pending_confirm_shortcut(history, draft)
    if shortcut:
        return shortcut
    system, user = _concierge_prompt(history, draft)
    out = await plain_chat(system, user, max_tokens=2000)
    return _finalize_reply(out, draft)


class ConciergeTurn:
    """스트리밍 대화 1턴 — 화면에는 답변 텍스트만 실시간으로, 계약 JSON은 뒤에서 조용히 파싱한다.

    사용법(ui.py):
        turn = ConciergeTurn(history, draft)
        if turn.shortcut:                       # D6 확인 응답 등 — LLM 호출 없이 즉답
            st.markdown(turn.shortcut[0])
        else:
            st.write_stream(turn.stream())       # 실시간 토큰 스트리밍
        reply, new_draft, ready = turn.result()
    """

    def __init__(self, history: list[dict], draft: dict):
        self.history = history
        self.draft = draft
        self.shortcut = _pending_confirm_shortcut(history, draft)
        self._raw = ""
        self._result: tuple[str, dict, bool] | None = self.shortcut

    async def stream(self):
        if self.shortcut:   # 이미 결정론으로 답이 나왔으면 스트리밍할 게 없다
            return
        system, user = _concierge_prompt(self.history, self.draft)
        shown = 0
        hold_back = len(_CONTRACT_MARKER) - 1   # 마커가 델타 경계에서 쪼개져 도착할 수 있어 꼬리를 보류
        async for delta in stream_chat(system, user, max_tokens=2000):
            self._raw += delta
            idx = self._raw.find(_CONTRACT_MARKER)
            if idx != -1:
                if idx > shown:
                    yield self._raw[shown:idx]
                    shown = idx
                continue   # 마커 확정 이후는 전부 JSON — 더 이상 아무것도 보여주지 않는다
            safe_len = max(0, len(self._raw) - hold_back)
            if safe_len > shown:
                yield self._raw[shown:safe_len]
                shown = safe_len
        self._result = _finalize_reply(self._raw, self.draft)

    def result(self) -> tuple[str, dict, bool]:
        if self._result is None:
            raise RuntimeError("stream()을 먼저 완전히 소비해야 result()를 부를 수 있다")
        return self._result


MERGE_SYSTEM = """너는 컨시어지의 병합 담당이다. @foodie 후보와 @scout 정보를 보고 '열린 슬롯'별 최종 식당 1곳을 고른다.
규칙:
- 고정 슬롯은 이미 코드가 확정했다. days에는 열린 슬롯만 담아라.
- 반드시 해당 슬롯의 candidates 안에서만 고르고, 값은 restaurant_id 문자열만 쓴다 (식당 이름 금지). 후보 밖 식당·창작·EXTERNAL 금지.
- 같은 식당을 두 번 쓰지 않는다 (고정 슬롯의 식당 포함). 하루 안에서는 '고정 슬롯의 장르 포함' 장르가 겹치지 않게 다양성을 준다 (예: 고정 점심이 라멘이면 저녁은 라멘 금지).
- 출력은 JSON 하나만:
{"days": [{"day": 1, "lunch": "restaurant_id", "cafe": "restaurant_id", "dinner": "restaurant_id"}],
 "hotel_area": "숙소 추천 세부지역(일본어, 계약 areas 우선)"}
- comment(선정 이유) 필드는 출력하지 마라 — 그건 코드가 결정론으로 생성한다 (자유 서술 금지, D4)."""


async def _merge(contract: TripContract, foodie_data: dict, scout_data: dict,
                 fixed_view: list[dict], extra_note: str = "") -> dict:
    user = (
        f"계약:\n{contract.to_json()}\n\n"
        f"이미 확정된 고정 슬롯(재출력 금지, 중복 금지): {json.dumps(fixed_view, ensure_ascii=False) if fixed_view else '없음'}\n\n"
        f"@foodie 후보:\n{json.dumps(foodie_data, ensure_ascii=False)}\n\n"
        f"@scout 요약:\n{json.dumps(scout_data, ensure_ascii=False)[:2000]}\n"
    )
    if extra_note:
        user += f"\n필수 반영 지적사항: {extra_note}\n"
    out = await plain_chat(MERGE_SYSTEM, user, max_tokens=2000)
    return extract_json(out) or {}


def _resolve_locked(contract: TripContract, anchor_keys: dict[int, dict], log) -> dict:
    """고정 식사 슬롯을 '코드'가 DB 조회로 확정한다 — LLM에게 맡기지 않는다 (계약 강제).

    D6 v2: 4단계 매칭(resolve_place) — 1)원문 2)토큰분해 3)앵커+유사도. 4단계(유사도만)는
    자동 확정하지 않는다. 채팅 단계에서 사용자가 이미 확인했다면 locked.name이 DB 정식
    표기로 치환돼 있어 1단계에서 바로 확정된다 (_apply_lock_confirm_reply 참고).
    """
    resolved: dict = {}
    for lk in contract.locked:
        if not lk.name or lk.slot not in _SLOT_ORDER or not (1 <= lk.day <= contract.num_days):
            continue   # stay/activity/미지정 day는 식사 슬롯 대상 아님 — 계약 notes로만 전달
        note = f" · {lk.note}" if lk.note and lk.note != "사용자 고정" else ""
        anchor_kw = (anchor_keys.get(lk.day, {}) or {}).get("search_kwargs", {})
        r = resolve_place(contract.pref, lk.name, anchor_kwargs=anchor_kw)
        if r["hit"]:
            hit = r["hit"]
            resolved[(lk.day, lk.slot)] = {"restaurant_id": hit["restaurant_id"], "name": hit["name"],
                                           "genres": hit.get("genres") or "",
                                           "reason": "사용자 고정" + note}
            log(f"[계약] 🔒 {lk.day}일차 {lk.slot} '{lk.name}' → DB 확정 (id {hit['restaurant_id']}, {r['stage']}단계)")
        elif r["stage"] == 4 and r["candidates"]:
            cand_desc = ", ".join(f"{c['name']}({c['restaurant_id']})" for c in r["candidates"])
            # 근접 후보를 버리지 않고 들고 간다 — 일정 카드에서 "혹시 이 곳?" 제안으로 노출 (UX)
            resolved[(lk.day, lk.slot)] = {"external": True, "name": lk.name,
                                           "candidates": [c["restaurant_id"] for c in r["candidates"][:2]]}
            log(f"[계약] 🔒 {lk.day}일차 {lk.slot} '{lk.name}' → 자동 매칭 불확실(4단계·미확인) "
                f"→ 사용자 지정 이름 그대로 반영. 근접 후보: {cand_desc}")
        else:
            resolved[(lk.day, lk.slot)] = {"external": True, "name": lk.name}
            log(f"[계약] 🔒 {lk.day}일차 {lk.slot} '{lk.name}' → DB에 없음, 사용자 지정 그대로 반영")
    return resolved


def pending_lock_confirmations(draft: dict) -> list[dict]:
    """계약 확정 전, 4단계(유사도만) 매칭이라 자동 확정할 수 없는 고정 항목을 찾는다 (D6).

    사용자가 이미 확인한 항목(note에 확인 마커가 있음)은 다시 묻지 않는다.
    """
    contract = TripContract.from_dict(draft)
    if not contract.pref or contract.num_days <= 0:
        return []
    anchors = contract.effective_day_anchors()
    pend: list[dict] = []
    for lk in contract.locked:
        if not lk.name or lk.slot not in _SLOT_ORDER or not (1 <= lk.day <= contract.num_days):
            continue
        if "[사용자 확인" in (lk.note or ""):
            continue
        anchor_label = anchors.get(lk.day, "")
        anchor_kw = resolve_anchor(contract.pref, anchor_label).get("search_kwargs", {})
        r = resolve_place(contract.pref, lk.name, anchor_kwargs=anchor_kw)
        if r["stage"] == 4 and r["candidates"]:
            # 증거 카드용: 앵커에서의 직선거리를 결정론으로 붙인다 (유저가 "내가 아는 그 가게"인지 판단할 근거)
            for c in r["candidates"]:
                st0 = c["stations"][0] if c.get("stations") else ""
                c["_dist_km"] = deviation_km(contract.pref, anchor_label, st0) if (anchor_label and st0) else None
            pend.append({"day": lk.day, "slot": lk.slot, "name": lk.name,
                         "anchor": anchor_label, "candidates": r["candidates"]})
    return pend


def _confirm_question(p: dict) -> str:
    """후보 제시 질문 — 코드 템플릿(LLM 창작 아님, D6).

    증거 카드: 이름만으로는 유저가 '내가 아는 그 가게'인지 알 수 없다 (실사례: とんかつ七井戸를
    이름·역만 보고 거절). 평점·리뷰수·지역·앵커 거리·타베로그/지도 링크를 함께 보여준다.
    """
    lines = [f"'{p['name']}' 이름과 정확히 일치하는 곳을 DB에서 못 찾았어요 ({p['day']}일차 {p['slot']}). "
             "비슷한 곳을 찾았는데, 혹시 이 중 하나인가요?"]
    for i, c in enumerate(p["candidates"], 1):
        station = c["stations"][0] if c.get("stations") else ""
        bits = []
        if c.get("genres"):
            bits.append(c["genres"])
        if c.get("tabelog_rating"):
            rv = f"(리뷰 {c['tabelog_review_count']:,})" if c.get("tabelog_review_count") else ""
            bits.append(f"★{c['tabelog_rating']}{rv}")
        if station:
            bits.append(f"{station}역")
        if c.get("_dist_km") is not None and p.get("anchor"):
            bits.append(f"{p['anchor']}에서 직선 ~{c['_dist_km']}km")
        links = " · ".join(x for x in (
            f"[타베로그]({c['tabelog_url']})" if c.get("tabelog_url") else "",
            f"[📍 지도]({c['gmap']})" if c.get("gmap") else "") if x)
        lines.append(f"**{i}) {c['name']}** — " + " · ".join(bits) + (f"\n   {links}" if links else ""))
    lines.append("번호로 답해 주시거나, 없으면 '그대로'라고 답해 주세요 — 지정하신 이름 그대로(DB 외) 반영할게요.")
    return "\n\n".join(lines)


def _apply_lock_confirm_reply(draft: dict, user_text: str, pend: list[dict]) -> dict:
    """사용자의 확인 답변(번호 | 그대로)을 코드로 파싱해 locked 항목에 반영한다 (LLM 비경유 — 오해석 방지)."""
    if not pend:
        return draft
    p = pend[0]
    m = re.match(r"^\s*([1-9])", user_text.strip())
    new_locked = []
    for it in draft.get("locked") or []:
        if isinstance(it, dict) and it.get("name") == p["name"] and int(it.get("day") or 0) == p["day"]:
            it = dict(it)
            if m and 1 <= int(m.group(1)) <= len(p["candidates"]):
                chosen = p["candidates"][int(m.group(1)) - 1]
                it["name"] = chosen["name"]   # DB 정식 표기로 치환 → 파이프라인에서 1단계 즉시 확정
                it["note"] = (it.get("note") or "").strip() + f" [사용자 확인: {chosen['name']}]"
            else:
                it["note"] = (it.get("note") or "").strip() + " [사용자 확인: DB 외 지정 이름 그대로]"
        new_locked.append(it)
    return {**draft, "locked": new_locked}


# 식사(lunch/dinner) 슬롯에 오면 안 되는 카페 계열 장르 — DB 장르 기준 코드 게이트
_CAFE_GENRES = {"カフェ", "パン", "スイーツ", "ケーキ", "チョコレート", "喫茶店", "甘味処",
                "コーヒー専門店", "紅茶専門店", "タピオカ", "かき氷", "ドーナツ", "クレープ",
                "パンケーキ", "サンドイッチ", "ベーカリー"}


def _is_cafe_only(row: dict) -> bool:
    genres = {g.strip() for g in (row.get("genres") or "").split(",") if g.strip()}
    return bool(genres) and genres <= _CAFE_GENRES


def _has_cafe_genre(row: dict) -> bool:
    """카페 계열 장르를 하나라도 포함하는가 — 카페 슬롯 배치 자격 판정."""
    genres = {g.strip() for g in (row.get("genres") or "").split(",") if g.strip()}
    return bool(genres & _CAFE_GENRES)


# LLM이 추천 이유 자리에 흘리는 사과문·메타 지시문 (실사례: "죄송합니다, 카페 슬롯에는…")
_REASON_META_MARKERS = ("죄송", "sorry", "슬롯에는", "배치해야", "배치되어야", "규칙상", "죄송합니다",
                        "출력해야", "지침", "안내드립", "cannot", "unable to", "as an ai")


def _clean_reason(reason: str) -> str:
    """추천 이유 정제 — LLM 사과/자기지시 텍스트가 새어나오면 버린다 (코드 코멘트로 대체됨)."""
    r = (reason or "").strip()
    if not r:
        return ""
    low = r.lower()
    if any(m in r or m in low for m in _REASON_META_MARKERS):
        return ""
    return r


def _gset(text) -> set:
    return {g.strip() for g in (text or "").split(",") if g.strip()}


def _below_floor(row: dict, relax: bool = False) -> bool:
    """품질 하한 미달 여부 (D5). relax=True면 완화 하한(≥20/≥3.3) 적용."""
    rv = row.get("tabelog_review_count") or 0
    bs = row.get("bayes_score")
    min_rv = QUALITY_RELAX_REVIEWS if relax else QUALITY_MIN_REVIEWS
    min_bs = QUALITY_RELAX_BAYES if relax else QUALITY_MIN_BAYES
    return rv < min_rv or bs is None or bs < min_bs


def _is_takeout_dinner(row: dict) -> bool:
    """저녁 슬롯 배제 대상: 테이크아웃/반찬 단독 업태 또는 초저가+좌석형 식사장르 부재 (D5, S7)."""
    genres = _gset(row.get("genres"))
    if genres and genres <= _TAKEOUT_GENRES:
        return True
    floor = row.get("budget_dinner_floor")
    seated = genres - _TAKEOUT_GENRES - _CAFE_GENRES
    if (floor is None or floor < 1000) and not seated and genres:
        return True
    return False


def _budget_cap(contract: TripContract, slot: str) -> int | None:
    """슬롯별 예산 상한 (엔). cafe는 점심 예산에 준한다."""
    if slot == "dinner":
        return contract.max_dinner_budget
    return contract.max_lunch_budget   # lunch·cafe


def _over_budget(row: dict, slot: str, contract: TripContract) -> int | None:
    """예산 초과면 그 하한가(엔)를 반환, 아니면 None. 코드가 강제하는 결정론 게이트 —
    LLM(@foodie)이 예산 인자를 빠뜨려도 초과 식당이 최종 일정에 남지 않게 한다 (실사례: 4,000엔
    저녁 설정인데 40,000엔 스시가 추천됨). 가격 정보가 없는(floor=None) 곳은 판정 보류(통과)."""
    cap = _budget_cap(contract, slot)
    if not cap:
        return None
    floor = row.get("budget_dinner_floor") if slot == "dinner" else row.get("budget_lunch_floor")
    if floor is not None and floor > cap:
        return floor
    return None


def _sanitize_foodie(foodie_data: dict, contract: TripContract, log) -> dict:
    """후보에 DB 장르를 붙이고, 카페 오배치·품질 하한 미달·저녁 테이크아웃·예산 초과 후보를 코드로 걸러낸다 (D5)."""
    ids = [str(c.get("restaurant_id")) for s in foodie_data.get("slots", [])
           for c in (s.get("candidates") or []) if c.get("restaurant_id")]
    rows = fetch_by_ids(ids)
    for s in foodie_data.get("slots", []):
        slot = str(s.get("slot") or "")
        kept = []
        for c in s.get("candidates") or []:
            c["reason"] = _clean_reason(c.get("reason", ""))   # LLM 사과문·메타 텍스트 제거 (#3)
            r = rows.get(str(c.get("restaurant_id")))
            if r:
                c["genres"] = r.get("genres") or ""
                if slot in ("lunch", "dinner") and _is_cafe_only(r):
                    log(f"[정제] {s.get('day')}일차 {slot}: 카페 계열 후보 제외 ({r['name']})")
                    continue
                if slot == "cafe" and not _has_cafe_genre(r):
                    log(f"[정제] {s.get('day')}일차 카페: 비카페 업태 제외 ({r['name']} · {r.get('genres')})")
                    continue
                if _below_floor(r):
                    log(f"[정제] {s.get('day')}일차 {slot}: 품질 하한 미달 제외 "
                        f"({r['name']} · 리뷰 {r.get('tabelog_review_count') or 0}·신뢰 {r.get('bayes_score')})")
                    continue
                if slot == "dinner" and _is_takeout_dinner(r):
                    log(f"[정제] {s.get('day')}일차 저녁: 테이크아웃/반찬 업태 제외 ({r['name']})")
                    continue
                over = _over_budget(r, slot, contract)
                if over:
                    log(f"[정제] {s.get('day')}일차 {slot}: 예산 초과 제외 ({r['name']} · 하한 ¥{over:,} > 상한 ¥{_budget_cap(contract, slot):,})")
                    continue
            kept.append(c)
        s["candidates"] = kept
    return foodie_data


def _slot_candidates(foodie_data: dict) -> dict:
    table: dict = {}
    for s in foodie_data.get("slots", []):
        try:
            table[(int(s.get("day", 0)), str(s.get("slot", "")))] = s
        except (ValueError, TypeError):
            continue
    return table


def _picks_from(merged: dict, foodie_data: dict, contract: TripContract, locked_map: dict, log) -> list[dict]:
    """병합 결과를 후보 목록에 대해 검증·교정한다 — 계약 강제는 프롬프트가 아니라 코드가 한다."""
    slots = _slot_candidates(foodie_data)
    by_day = {}
    for d in merged.get("days") or []:
        if isinstance(d, dict):
            try:
                by_day[int(d.get("day", 0))] = d
            except (ValueError, TypeError):
                continue

    # 1) 고정 슬롯을 먼저 심는다 — 병합 LLM의 출력과 무관하게 계약이 이긴다
    picks: list[dict] = []
    used: set[str] = set()
    day_genres: dict[int, set] = {}          # 같은 날 장르 중복 회피용 (코드 게이트)
    for (day, slot), info in sorted(locked_map.items()):
        if info.get("restaurant_id"):
            used.add(info["restaurant_id"])
        day_genres.setdefault(day, set()).update(_gset(info.get("genres")))
        picks.append({"day": day, "slot": slot, "locked": True, **info})

    # 2) 열린 슬롯만 병합 결과에서 채운다 (후보 밖/중복/EXTERNAL은 교정)
    for day in range(1, contract.num_days + 1):
        d = by_day.get(day, {})
        for slot in _SLOT_ORDER:
            if (day, slot) in locked_map:
                continue
            clist = (slots.get((day, slot)) or {}).get("candidates") or []
            chosen = str(d.get(slot) or "")
            if chosen.startswith("EXTERNAL:"):
                log(f"[병합] ⚠️ {day}일차 {slot}: EXTERNAL 출력 무효 (고정 슬롯은 코드가 관리)")
                chosen = ""
            pick = None
            legal = {str(c.get("restaurant_id")): c for c in clist if c.get("restaurant_id")}
            by_name = {str(c.get("name")): c for c in clist if c.get("restaurant_id") and c.get("name")}
            cand = None
            if chosen in legal and chosen not in used:
                cand = legal[chosen]
            elif chosen in by_name and by_name[chosen]["restaurant_id"] not in used:
                cand = by_name[chosen]           # 병합이 id 대신 이름을 출력한 경우 구제
                log(f"[병합] {day}일차 {slot}: 이름 출력 → id 매칭 구제 ({chosen[:20]})")
            taken = day_genres.get(day, set())
            if cand and _gset(cand.get("genres")) & taken:
                alt = next((c for c in clist if c.get("restaurant_id") and c["restaurant_id"] not in used
                            and c is not cand and not (_gset(c.get("genres")) & taken)), None)
                if alt:
                    log(f"[병합] {day}일차 {slot}: 같은 날 장르 중복 회피 → {alt.get('name', '')[:24]}")
                    cand = alt
            if cand:
                pick = {"restaurant_id": cand["restaurant_id"], "name": cand.get("name", ""),
                        "genres": cand.get("genres", ""), "reason": cand.get("reason", "")}
            else:
                fbs = [c for c in clist if c.get("restaurant_id") and c["restaurant_id"] not in used]
                fb = next((c for c in fbs if not (_gset(c.get("genres")) & taken)), fbs[0] if fbs else None)
                if fb:
                    pick = {"restaurant_id": fb["restaurant_id"], "name": fb.get("name", ""),
                            "genres": fb.get("genres", ""), "reason": fb.get("reason", ""),
                            "corrected": bool(chosen)}
                    if chosen:
                        log(f"[병합] ⚠️ {day}일차 {slot}: 후보 밖/중복 선택 → 후보로 교정")
            if pick:
                if pick.get("restaurant_id"):
                    used.add(pick["restaurant_id"])
                day_genres.setdefault(day, set()).update(_gset(pick.get("genres")))
                # D8: 선택되지 않은 나머지 후보를 대안으로 남긴다 ("다른 후보 보기" 카드용)
                alt_ids = [c["restaurant_id"] for c in clist
                           if c.get("restaurant_id") and c["restaurant_id"] != pick.get("restaurant_id")][:3]
                picks.append({"day": day, "slot": slot, "locked": False, "alt_ids": alt_ids, **pick})
    return picks


def _backfill(picks: list[dict], contract: TripContract, anchor_keys: dict[int, dict], log,
              meal_times: dict[int, dict] | None = None) -> list[dict]:
    """비어 있는 day×slot을 결정론 검색으로 채운다 — 앵커 검색키 + 품질 하한(≥50/≥3.4), 희소 시 라벨 완화 (D2·D5).

    meal_times가 주어지면 시간창 밖 슬롯(항공 시간과 겹침)은 백필하지 않는다.
    """
    have = {(p["day"], p["slot"]) for p in picks}
    used = {p["restaurant_id"] for p in picks if p.get("restaurant_id")}
    day_genres: dict[int, set] = {}
    trip_genre_count: dict[str, int] = {}          # 여행 전체 장르 사용 횟수 (다양도 균형용, #1)
    for p in picks:
        day_genres.setdefault(p["day"], set()).update(_gset(p.get("genres")))
        for g in _gset(p.get("genres")):
            trip_genre_count[g] = trip_genre_count.get(g, 0) + 1
    genres = contract.genres_pref or [None]
    day_anchors = contract.effective_day_anchors()

    for day in range(1, contract.num_days + 1):
        anchor = day_anchors.get(day)
        anchor_kw = (anchor_keys.get(day, {}) or {}).get("search_kwargs", {})   # {station:..} | {area2:..} | {}
        for i, slot in enumerate(_SLOT_ORDER):
            if (day, slot) in have:
                continue
            if meal_times is not None and slot not in meal_times.get(day, {}):
                continue   # 시간창 밖 슬롯 — 백필 금지 (항공 시간 반영)
            budget_kw = ({"max_dinner_budget": contract.max_dinner_budget} if slot == "dinner"
                         else {"max_lunch_budget": contract.max_lunch_budget})  # cafe도 점심 예산 준용
            # 장르: 여행 전체에서 가장 적게 쓴 선호 장르를 우선한다 (모듈로 순환 → 최소사용 우선, #1 다양도)
            if slot == "cafe":
                genre = "カフェ"
            elif genres and genres[0] is not None:
                genre = min(genres, key=lambda g: (trip_genre_count.get(g, 0), genres.index(g)))
            else:
                genre = None
            taken = day_genres.get(day, set())
            cand, relaxed = None, False
            # 품질 하한 우선(strict → relaxed), 각 단계에서 앵커키 → 장르만 → 전지역 순으로 완화
            for relax in (False, True):
                min_rv = QUALITY_RELAX_REVIEWS if relax else QUALITY_MIN_REVIEWS
                min_bs = QUALITY_RELAX_BAYES if relax else QUALITY_MIN_BAYES
                for kw in ({**anchor_kw, "genre": genre}, {**anchor_kw}, {"genre": genre}, {}):
                    rows = search_lib(pref=contract.pref, **budget_kw,
                                      min_reviews=min_rv, min_bayes=min_bs, sort="bayes", limit=12,
                                      **{k: v for k, v in kw.items() if v})
                    ok = [r for r in rows if r["restaurant_id"] not in used
                          and not (slot != "cafe" and _is_cafe_only(r))
                          and not (slot == "cafe" and not _has_cafe_genre(r))   # 카페 슬롯엔 카페 장르만 (#3)
                          and not (slot == "dinner" and _is_takeout_dinner(r))]
                    # 같은 날 장르 중복을 피하되, 동률이면 여행 전체에서 덜 쓴 장르를 우선 (다양도, #1)
                    fresh = [r for r in ok if not (_gset(r.get("genres")) & taken)]
                    pool = fresh or ok
                    cand = min(pool, key=lambda r: sum(trip_genre_count.get(g, 0) for g in _gset(r.get("genres")))) \
                        if pool else None
                    if cand:
                        relaxed = relax
                        break
                if cand:
                    break
            if cand:
                used.add(cand["restaurant_id"])
                day_genres.setdefault(day, set()).update(_gset(cand.get("genres")))
                for g in _gset(cand.get("genres")):
                    trip_genre_count[g] = trip_genre_count.get(g, 0) + 1
                reason = "자동 보충 — 베이지안 랭킹 상위"
                if relaxed:
                    reason += " · ⚠️ 데이터 희소 지역 — 기준 완화(리뷰≥20)"
                alt_ids = [r["restaurant_id"] for r in ok if r["restaurant_id"] != cand["restaurant_id"]][:3]
                picks.append({"day": day, "slot": slot, "locked": False, "backfill": True, "alt_ids": alt_ids,
                              "restaurant_id": cand["restaurant_id"], "name": cand["name"],
                              "genres": cand.get("genres", ""), "relaxed": relaxed, "reason": reason})
                tag = " (희소 완화)" if relaxed else ""
                log(f"[보충] {day}일차 {slot}: 후보 누락 → 결정론 백필{tag} ({cand['name']})")
    return picks


def _sanitize_flight(flight: dict) -> dict:
    """항공 시세를 코드가 정제한다 (D7): low/high가 둘 다 없으면 '부터' 단일가로 새지 않게 아예 비운다.

    @scout이 하한만 찾았거나(예: '25만원부터'만 확인) 창작을 피해 0을 남긴 경우, 화면에 어설픈
    단일가를 내보내는 대신 조용히 범위 없음으로 처리한다 (fail-soft, 거짓 정밀도보다 정직 우선).
    """
    try:
        low, high = int(flight.get("low") or 0), int(flight.get("high") or 0)
    except (TypeError, ValueError):
        low, high = 0, 0
    if low and high and low > high:
        low, high = high, low
    if not (low and high):
        return {"low": None, "high": None, "range_krw": "", "baseline": "", "note": str(flight.get("note") or "")}
    return {
        "low": low, "high": high, "range_krw": f"약 {low:,}~{high:,}원",
        "baseline": str(flight.get("baseline") or "").strip(),
        "note": str(flight.get("note") or "").strip(),
    }


_SLOT_KO_P = {"lunch": "점심", "cafe": "카페", "dinner": "저녁"}


def _emit_partial(on_partial, stage: str, md: str) -> None:
    """부분 결과 콜백 — UI 콜백 오류가 파이프라인을 죽이지 않게 감싼다 (fail-soft)."""
    if on_partial:
        try:
            on_partial(stage, md)
        except Exception:
            pass


def _partial_md(contract: TripContract, picks: list[dict], day_anchors: dict[int, str],
                acts_by_day: dict[int, list[dict]] | None = None, stage_note: str = "") -> str:
    """잠정 라인업 마크다운 — 식당이 확정되는 즉시 사용자에게 먼저 보여준다 (progressive UX).

    최종 카드(검증·휴무·동선·팁)와 달리 한 줄 요약만 — '기다림의 체감'을 줄이는 게 목적이다.
    """
    rows = fetch_by_ids([p["restaurant_id"] for p in picks if p.get("restaurant_id")])
    L = [f"#### ⚡ 식당 라인업 (잠정) — {stage_note}"]
    for day in range(1, contract.num_days + 1):
        parts = []
        for slot in _SLOT_ORDER:
            p = next((x for x in picks if x["day"] == day and x["slot"] == slot), None)
            if not p:
                continue
            lock = "🔒 " if p.get("locked") else ""
            r = rows.get(p.get("restaurant_id"))
            star = f" ★{r['tabelog_rating']}" if r and r.get("tabelog_rating") else ""
            parts.append(f"{_SLOT_KO_P[slot]} {lock}{(r or p).get('name', '')}{star}")
        anchor = day_anchors.get(day, "")
        head = f"**Day{day}**" + (f" ({anchor})" if anchor else "")
        L.append(f"- {head}: " + (" · ".join(parts) if parts else "_항공 시간과 겹쳐 식사 슬롯 없음_"))
    if acts_by_day:
        act_lines = []
        for day in range(1, contract.num_days + 1):
            titles = [a.get("title", "") for a in acts_by_day.get(day, []) if a.get("title")]
            if titles:
                act_lines.append(f"- **Day{day} 활동**: " + " · ".join(titles))
        if act_lines:
            L.append("#### 🔭 주변 활동 (잠정)")
            L.extend(act_lines)
    L.append(f"_{'⚖️ @critic 검증·동선 계산 중… 최종 일정이 곧 표시됩니다' if acts_by_day else '🔭 @scout이 활동·날씨·호텔·항공을 조사 중…'}_")
    return "\n\n".join(L)


def _build_comment(contract: TripContract, picks: list[dict], day_anchors: dict[int, str]) -> str:
    """선정 이유 코멘트 — 코드 템플릿 (D4). LLM 자유 서술 금지: '표참도에서 교통 편리' 같은
    검색 근거 없는 창작이나 '시스템 내 식당으로 정정' 같은 허위 정정 서술의 재발을 구조로 차단한다.
    """
    n_locked = sum(1 for p in picks if p.get("locked"))
    n_relaxed = sum(1 for p in picks if p.get("relaxed"))
    genres = sorted({g for p in picks for g in _gset(p.get("genres"))})
    genre_txt = "·".join(genres[:4]) + ("…" if len(genres) > 4 else "") if genres else "다양한 장르"
    anchor_txt = " / ".join(f"Day{d} {a}" for d, a in sorted(day_anchors.items())) if day_anchors else ""
    parts = []
    if n_locked:
        parts.append(f"고정 {n_locked}곳")
    parts.append(f"장르 {genre_txt} 순환")
    if anchor_txt:
        parts.append(f"{anchor_txt} 중심")
    if n_relaxed:
        parts.append(f"희소 지역 {n_relaxed}곳은 품질 기준 완화")
    return " · ".join(parts) + "으로 구성했어요."


async def run_pipeline(contract: TripContract, log=None, on_partial=None) -> dict:
    """일정 생성 파이프라인.

    on_partial(stage, md): 부분 결과 콜백 (선택) — 식당 라인업이 확정되는 즉시("meals"),
    활동 조사가 끝나는 즉시("activities") 잠정 마크다운을 UI에 먼저 흘린다.
    최종 반환값은 기존과 동일한 완성 일정 dict.
    """
    log = log or (lambda s: None)
    log("[계약] SHARED CONTRACT 고정 — locked 항목은 어떤 에이전트도 변경 불가")

    # 앵커 해석 (D2): 일자별 앵커 → 검증된 DB 검색 키 (area2 vs station을 코드가 결정)
    # 고정 장소 매칭(D6)도 이 검색 키를 4단계 매칭의 앵커 후보 조회에 쓰므로 먼저 계산한다.
    day_anchors = contract.effective_day_anchors()
    anchor_keys: dict[int, dict] = {}
    for day, anchor in day_anchors.items():
        info = resolve_anchor(contract.pref, anchor)
        anchor_keys[day] = info
        log(info["log"])

    locked_map = _resolve_locked(contract, anchor_keys, log)

    # Day Window (항공 시간 반영, 결정론): 창 밖 식사 슬롯은 처음부터 열지 않는다 —
    # 고정(locked) 슬롯은 계약이 이기므로 창과 무관하게 유지된다.
    windows = {d: timemodel.day_window(d, contract.num_days, contract.arrival_time, contract.departure_time)
               for d in range(1, contract.num_days + 1)}
    meal_times = {d: timemodel.plan_meal_slots(w["start"], w["end"]) for d, w in windows.items()}
    for d, w in windows.items():
        if w["banner"]:
            log(f"[시간창] {d}일차 {timemodel.min_to_hhmm(w['start'])}~{timemodel.min_to_hhmm(w['end'])} — {w['banner']}")
        for s in _SLOT_ORDER:
            if s not in meal_times[d] and (d, s) not in locked_map:
                log(f"[시간창] {d}일차 {s}: 항공·이동 시간과 겹쳐 슬롯 제외")

    open_slots = [(d, s) for d in range(1, contract.num_days + 1) for s in _SLOT_ORDER
                  if (d, s) not in locked_map and s in meal_times[d]]
    fixed_view = [{"day": d, "slot": s,
                   **{k: v for k, v in info.items() if k in ("restaurant_id", "name", "external")}}
                  for (d, s), info in sorted(locked_map.items())]

    # 배치1: @scout은 태스크로 띄워 두고(느린 웹검색), @foodie → 병합을 먼저 끝내
    # 식당 라인업을 즉시 사용자에게 보여준다 (progressive). 병합이 scout 완료를 기다리지
    # 않으므로 전체 시간도 단축된다. scout 결과는 병합 판단에 필수가 아니다 (후보는 foodie 전용).
    log("[배치1] @foodie ∥ @scout 병렬 리서치 시작 (scout은 백그라운드 태스크)")
    scout_task = asyncio.create_task(run_scout(contract, log=log))
    try:
        if open_slots:
            foodie_data = await run_foodie(contract, open_slots, fixed_view, anchor_keys=anchor_keys, log=log)
        else:                               # 모든 식사가 고정된 극단 케이스
            foodie_data = {"slots": []}
        log(f"[배치1] @foodie 완료 — 식당 후보 슬롯 {len(foodie_data.get('slots', []))}개")
        foodie_data = _sanitize_foodie(foodie_data, contract, log)

        log("[병합] @concierge 슬롯별 최종 선정 (후보 밖 선택은 코드가 교정)")
        merged = await _merge(contract, foodie_data,
                              {"note": "(@scout 조사 진행 중 — 슬롯 선정은 후보 내에서만 한다)"},
                              fixed_view)
        picks = _picks_from(merged, foodie_data, contract, locked_map, log)
        picks = _backfill(picks, contract, anchor_keys, log, meal_times=meal_times)
        _emit_partial(on_partial, "meals",
                      _partial_md(contract, picks, day_anchors, stage_note="검증 전 초안"))

        scout_data = await scout_task
    except BaseException:
        scout_task.cancel()                 # foodie/병합 실패 시 scout 고아 태스크 방지
        raise
    n_items = sum(len(x.get("items") or []) for x in scout_data.get("days", []))
    log(f"[배치1] @scout 완료 — 활동 {n_items}건")

    scout_by_day = {}
    for d in scout_data.get("days", []):
        if isinstance(d, dict):
            try:
                scout_by_day[int(d.get("day", 0))] = d.get("items") or []
            except (ValueError, TypeError):
                continue

    # 활동: 종일형 차단 + 슬롯 규칙 배치 + 전 일정 dedup (D3 + D4 코드 게이트) — critic 검증보다 먼저 확정한다
    seen_titles: set[str] = set()
    scheduled_acts: dict[int, list[dict]] = {}
    allday_options: list[dict] = []
    for day in range(1, contract.num_days + 1):
        w = windows[day]
        acts, allday = timemodel.schedule_day(
            scout_by_day.get(day, []), seen_titles, log=log, day=day,
            allowed=timemodel.allowed_activity_slots(w["start"], w["end"]))
        scheduled_acts[day] = acts
        allday_options.extend(allday)
    flat_acts = [{"day": d, **{k: a[k] for k in ("title", "why", "area", "open_hours", "last_entry", "slot") if k in a}}
                 for d, acts in scheduled_acts.items() for a in acts]
    evidence = str(scout_data.get("_evidence") or "")[:6000]
    _emit_partial(on_partial, "activities",
                  _partial_md(contract, picks, day_anchors, acts_by_day=scheduled_acts,
                              stage_note="검증 전 초안"))

    log("[게이트] @critic 읽기 전용 검증 시작 — 식당 + 활동")
    def _critic_view(ps):
        return [{k: p[k] for k in ("day", "slot", "locked", "restaurant_id", "name", "external") if k in p}
                for p in ps]
    verdict = await run_critic(contract, _critic_view(picks), activities=flat_acts, evidence=evidence,
                               day_anchors=day_anchors, flight=scout_data.get("flight"), log=log)
    if not verdict.get("pass", True) and verdict.get("issues"):
        log("[게이트] ❌ 불합격 → 지적사항 반영해 병합 재시도 (self-correction)")
        merged = await _merge(contract, foodie_data, scout_data, fixed_view,
                              extra_note="; ".join(map(str, verdict["issues"])))
        picks = _picks_from(merged, foodie_data, contract, locked_map, log)
        picks = _backfill(picks, contract, anchor_keys, log, meal_times=meal_times)
        verdict = await run_critic(contract, _critic_view(picks), activities=flat_acts, evidence=evidence,
                                   day_anchors=day_anchors, flight=scout_data.get("flight"), log=log)
    # 판정 건수는 코드가 확정한다 (D4 수용 기준: "식당 N곳 + 활동 M건 판정"을 항상 포함)
    verdict.setdefault("issues", [])
    verdict["restaurants_checked"] = len(_critic_view(picks))
    verdict["activities_checked"] = len(flat_acts)

    # 예산 검증은 코드가 확정한다 (#4) — critic(LLM)의 관대함에 의존하지 않는다.
    # 후보 정제·백필이 이미 예산을 강제하므로 위반은 0이어야 한다. locked(사용자 고정)는
    # 사용자 선택이라 검증 대상에서 뺀다. 위반이 발견되면 픽에서 제거하고 issues에 기록한다.
    if contract.max_dinner_budget or contract.max_lunch_budget:
        pick_rows = fetch_by_ids([p["restaurant_id"] for p in picks if p.get("restaurant_id")])
        kept_picks, budget_issues = [], []
        for p in picks:
            r = pick_rows.get(p.get("restaurant_id"))
            if r and not p.get("locked") and not p.get("external"):
                over = _over_budget(r, p["slot"], contract)
                if over:
                    budget_issues.append(f"{p['day']}일차 {p['slot']} {r['name']}: 하한 ¥{over:,} > 상한 ¥{_budget_cap(contract, p['slot']):,}")
                    log(f"[예산감사] ⛔ {budget_issues[-1]} → 최종 제거")
                    continue
            kept_picks.append(p)
        if budget_issues:
            picks = kept_picks
            verdict["issues"].append("예산 초과 식당을 코드가 최종 제거: " + "; ".join(budget_issues))
        verdict["budget_checked"] = True
        log(f"[예산감사] 예산 준수 확인 — 위반 {len(budget_issues)}건 처리")

    log("[로지스틱스] 앵커 이탈 검증·동선·딥링크 (결정론 도구)")
    alt_pool_ids = [aid for p in picks for aid in (p.get("alt_ids") or [])]
    ext_cand_ids = [cid for p in picks if p.get("external") for cid in (p.get("candidates") or [])]
    rows = fetch_by_ids([p["restaurant_id"] for p in picks if p.get("restaurant_id")]
                        + alt_pool_ids + ext_cand_ids)

    days_out = []
    for day in range(1, contract.num_days + 1):
        anchor = day_anchors.get(day, "")
        anchor_station = anchor  # 앵커 문자열 자체가 역명 (표参道 등) — external·이탈 판정 기준
        date_str = contract.date_of(day)
        # 방문일의 일본식 요일 문자 — 식당 정기휴무(closed_days)와 대조해 경고를 띄운다 (결정론 팁)
        jp_wd = "月火水木金土日"[date.fromisoformat(date_str).weekday()] if date_str else ""
        meals, route_places = [], []
        for p in [x for x in picks if x["day"] == day]:
            # 시간창 기반 슬롯 시각 (창 밖 고정 슬롯은 명목 시각으로 렌더 폴백)
            t_min = meal_times.get(day, {}).get(p["slot"])
            t_str = timemodel.min_to_hhmm(t_min) if t_min else ""
            if p.get("external"):
                # external 고정 장소: 앵커 역 좌표로 근사해 동선·지도에 포함한다 (D2)
                # 지도 링크에 앵커 역을 넣어 검색 반경을 좁히고(도시 전역 오검색 방지),
                # 지도가 핀을 못 잡을 경우를 대비해 웹 검색 링크와 DB 근접 후보 제안을 함께 준다.
                sugg = [
                    {"restaurant_id": cid, "name": cr["name"],
                     "tabelog_url": cr.get("tabelog_url"), "gmap": cr.get("gmap"),
                     "rating": cr.get("tabelog_rating"), "reviews": cr.get("tabelog_review_count"),
                     "station": cr["stations"][0] if cr.get("stations") else ""}
                    for cid in (p.get("candidates") or []) if (cr := rows.get(cid))
                ]
                gmap = (google_search_url(p["name"], anchor_station) if anchor_station
                        else external_place_link(p["name"], contract.pref))
                # Places API(키 설정 시): 정식 명칭·주소·핀 확정 링크로 업그레이드 (실패 시 위 폴백 유지)
                place = places_resolve(p["name"], anchor_station, city_of(contract.pref)[1])
                address = canonical = ""
                if place:
                    gmap = place["maps_url"] or gmap
                    address = place["address"]
                    if place["name"] and place["name"] != p["name"]:
                        canonical = place["name"]
                    log(f"[지도] {day}일차 {p['slot']}: Places 확인 — {place['name'] or p['name']}")
                meals.append({"slot": p["slot"], "locked": True, "external": True, "name": p["name"],
                              "time": t_str,
                              "station": anchor_station, "note": "DB 미등록 — 지정 이름 그대로 반영",
                              "gmap": gmap, "address": address, "canonical": canonical,
                              "pin_verified": bool(place),
                              "web": external_web_search_link(p["name"], anchor_station, contract.pref),
                              "suggestions": sugg})
                if anchor_station:
                    route_places.append({"name": p["name"], "station": anchor_station})
                continue
            r = rows.get(p.get("restaurant_id"))
            if not r:      # critic이 못 거른 유령 id 최종 방어선
                log(f"[방어] {day}일차 {p['slot']}: DB에 없는 id 제거")
                continue
            st0 = r["stations"][0] if r.get("stations") else ""
            # 앵커 이탈 게이트 (D2): 최기역이 앵커 역에서 4km 초과면 라벨 강제 (조용한 이탈 금지)
            off_label = ""
            if not p.get("locked") and anchor_station and st0:
                dev = deviation_km(contract.pref, anchor_station, st0)
                off_label = off_anchor_label(dev)
                if off_label:
                    log(f"[이탈] {day}일차 {p['slot']}: {r['name']} — {off_label}")
            # D8: 선택되지 않은 후보 최대 3곳 — 슬롯 카드의 "다른 후보 보기"용 (LLM 재호출 없이 즉시 표시)
            alternatives = [
                {"restaurant_id": aid, "name": ar["name"],
                 "tabelog_url": ar.get("tabelog_url"), "gmap": ar.get("gmap"),
                 "rating": ar.get("tabelog_rating"), "reviews": ar.get("tabelog_review_count"),
                 "station": ar["stations"][0] if ar.get("stations") else ""}
                for aid in (p.get("alt_ids") or []) if (ar := rows.get(aid))
            ]
            closed = (r.get("closed_days") or "").strip()
            # '祝日(공휴일)'의 日이 일요일(日)과 오검출되지 않게 제거 후 요일 문자를 대조한다
            closed_warn = bool(jp_wd and closed
                               and jp_wd in closed.replace("祝日", "").replace("祭日", ""))
            if closed_warn:
                log(f"[휴무] ⚠️ {day}일차 {p['slot']}: {r['name']} — 정기휴무({closed})가 방문일({date_str})과 겹칠 수 있음")
            meals.append({
                "slot": p["slot"], "locked": p.get("locked", False), "external": False,
                "restaurant_id": p.get("restaurant_id", ""), "time": t_str,
                "name": r["name"], "genres": r.get("genres") or "",
                "rating": r.get("tabelog_rating"), "reviews": r.get("tabelog_review_count"),
                "bayes": r.get("bayes_score"),
                "budget": r.get("budget_dinner") if p["slot"] == "dinner" else r.get("budget_lunch"),
                "station": st0, "tabelog_url": r.get("tabelog_url"), "gmap": r.get("gmap"),
                "reason": p.get("reason", ""), "off_anchor": off_label, "relaxed": p.get("relaxed", False),
                "closed": closed, "closed_warn": closed_warn,
                "alternatives": alternatives,
            })
            if st0:
                route_places.append({"name": r["name"], "station": st0})
        meals.sort(key=lambda m: _SLOT_ORDER.index(m["slot"]) if m["slot"] in _SLOT_ORDER else 9)
        # 식사는 시간순(점심→카페→저녁)이 고정이므로 NN 재정렬 없이 순서 유지
        route = order_day_route(route_places, keep_order=True) if route_places else {"order": [], "route_url": "", "legs": [], "points": []}
        days_out.append({"day": day, "date": contract.date_of(day), "anchor": anchor,
                         "banner": windows[day]["banner"],
                         "window": {"start": timemodel.min_to_hhmm(windows[day]["start"]),
                                    "end": timemodel.min_to_hhmm(windows[day]["end"])},
                         "meals": meals, "activities": scheduled_acts.get(day, []), "route": route})

    hotel_area = contract.hotel_anchor() or str(merged.get("hotel_area") or "")   # 숙소 앵커 우선 (D1)
    stats = {
        "foodie_candidates": sum(len(s.get("candidates") or []) for s in foodie_data.get("slots", [])),
        "meals": sum(len(d["meals"]) for d in days_out),
        "activities": sum(len(d["activities"]) for d in days_out),
        "hotel_picks": len(scout_data.get("hotels") or []),
        "verified": len([p for p in picks if p.get("restaurant_id")]),
        "critic_pass": bool(verdict.get("pass")),
    }
    itinerary = {
        "contract": asdict(contract),
        "day_anchors": {str(d): a for d, a in day_anchors.items()},
        "days": days_out,
        "allday_options": allday_options[:4],
        "flights": {**flight_links(contract.origin, contract.pref, contract.start_date, contract.end_date, contract.party),
                    **_sanitize_flight(scout_data.get("flight") or {})},
        "hotels": {**hotel_links(hotel_area, contract.pref, contract.start_date, contract.end_date, contract.party),
                   "picks": (scout_data.get("hotels") or [])[:3]},
        "weather": str(scout_data.get("weather") or ""),
        "critic": verdict,
        "comment": _build_comment(contract, picks, day_anchors),
        "stats": stats,
    }
    log("[완료] 일정표 생성 ✅")
    return itinerary


def swap_meal(itinerary: dict, day: int, slot: str, new_id: str) -> dict | None:
    """일정의 한 슬롯을 사전 계산된 대안/제안으로 교체한다 — LLM 재호출 없는 결정론 연산 (D8 확장).

    교체 전 픽은 대안 목록 맨 앞에 남겨 '되돌리기'가 가능하고, 그날 동선(route)도 재계산한다.
    유령 id·없는 슬롯이면 None (호출부가 무시).
    """
    new_id = str(new_id)
    row = fetch_by_ids([new_id]).get(new_id)
    if not row:
        return None
    d = next((x for x in itinerary.get("days", []) if x.get("day") == day), None)
    if not d:
        return None
    idx = next((i for i, m in enumerate(d.get("meals", [])) if m.get("slot") == slot), None)
    if idx is None:
        return None
    old = d["meals"][idx]
    pref = str((itinerary.get("contract") or {}).get("pref") or "")
    anchor = str(d.get("anchor") or "")
    st0 = row["stations"][0] if row.get("stations") else ""

    # 요일-휴무 대조 (파이프라인과 동일 규칙)
    try:
        jp_wd = "月火水木金土日"[date.fromisoformat(d.get("date") or "").weekday()]
    except (ValueError, TypeError):
        jp_wd = ""
    closed = (row.get("closed_days") or "").strip()
    closed_warn = bool(jp_wd and closed and jp_wd in closed.replace("祝日", "").replace("祭日", ""))
    off_label = off_anchor_label(deviation_km(pref, anchor, st0)) if (anchor and st0) else ""

    # 대안 목록 재구성: 이전 픽(되돌리기용, DB 픽일 때만) + 기존 대안·제안 중 새 픽 제외
    pool = (old.get("alternatives") or []) + (old.get("suggestions") or [])
    alts = [a for a in pool if str(a.get("restaurant_id") or "") not in ("", new_id)]
    if not old.get("external") and old.get("restaurant_id"):
        alts = [{"restaurant_id": old["restaurant_id"], "name": old.get("name", ""),
                 "tabelog_url": old.get("tabelog_url"), "gmap": old.get("gmap"),
                 "rating": old.get("rating"), "reviews": old.get("reviews"),
                 "station": old.get("station", "")}] + alts

    d["meals"][idx] = {
        "slot": slot, "locked": bool(old.get("locked")), "external": False,
        "restaurant_id": new_id, "time": old.get("time", ""),
        "name": row["name"], "genres": row.get("genres") or "",
        "rating": row.get("tabelog_rating"), "reviews": row.get("tabelog_review_count"),
        "bayes": row.get("bayes_score"),
        "budget": row.get("budget_dinner") if slot == "dinner" else row.get("budget_lunch"),
        "station": st0, "tabelog_url": row.get("tabelog_url"), "gmap": row.get("gmap"),
        "reason": "사용자 고정 — 제안에서 채택" if old.get("external") else "사용자 선택 — 대안에서 교체",
        "off_anchor": off_label, "closed": closed, "closed_warn": closed_warn,
        "alternatives": alts[:3],
    }

    # 그날 동선 재계산 (식사 시간순 유지, external은 앵커 역 근사 — 파이프라인과 동일)
    route_places = []
    for m in sorted(d["meals"], key=lambda m: _SLOT_ORDER.index(m["slot"]) if m["slot"] in _SLOT_ORDER else 9):
        if m.get("external"):
            if anchor:
                route_places.append({"name": m["name"], "station": anchor})
        elif m.get("station"):
            route_places.append({"name": m["name"], "station": m["station"]})
    d["route"] = order_day_route(route_places, keep_order=True) if route_places \
        else {"order": [], "route_url": "", "legs": [], "points": []}
    return itinerary
