"""에이전트 루프 — Day7 실습 루프의 일반화판.

① LLM 판단 → ② MCP 도구 실행 → ③ 결과 되먹임 → 반복.
- 도구 백엔드 = FastMCP 서버 (인메모리 ↔ URL 교체 가능, Day7 Lab5)
- allow 인자로 도구를 골라 주는 것이 곧 권한 경계 (Day9)
- 오류는 관찰로 되먹여 self-correction (Day7 Lab4)
- 계획·병합 단계는 tools 없이 plain_chat 사용 (Day7 Lab2.5: 계획 단계엔 tools 금지)
"""
from __future__ import annotations

import asyncio
import json

from fastmcp import Client
from openai import APIConnectionError, APIStatusError, RateLimitError

from tabetabi.config import DEFAULT_MODEL, NO_THINK, get_llm

_model_cache: dict = {"id": None}


async def resolve_model() -> str:
    """모델 가용성 확인 후 확정 (Day7 Lab0 방식). 실패 시 기본값 유지."""
    if _model_cache["id"]:
        return _model_cache["id"]
    model = DEFAULT_MODEL
    try:
        page = await get_llm().models.list()
        av = [m.id for m in page.data]
        if model not in av:
            q = [m for m in av if m.startswith("qwen/")
                 and not any(x in m for x in ("vl", "embed", "rerank", "thinking"))]
            model = q[0] if q else (av[0] if av else DEFAULT_MODEL)
    except Exception:
        pass
    _model_cache["id"] = model
    return model


def _transient_status(e: APIStatusError) -> bool:
    """재시도해도 되는 상태 오류인가. 5xx 외에, NIM이 일시적 서버 장애(서빙 function의
    DEGRADED 상태)를 400으로 반환하는 특이 케이스도 포함한다 — 클라이언트 잘못이 아니다."""
    if e.status_code and e.status_code >= 500:
        return True
    return e.status_code == 400 and "DEGRADED" in str(e)


# 기본 모델이 장애(502/DEGRADED/행)로 재시도까지 소진되면 갈아탈 폴백 모델 체인.
# NIM 무료 티어에서 tool calling을 지원하는 대형 모델을 기본값으로 둔다.
import os as _os

FALLBACK_MODELS = [m.strip() for m in
                   _os.getenv("LLM_FALLBACK_MODELS", "meta/llama-3.3-70b-instruct").split(",") if m.strip()]
_failed_models: set[str] = set()


def _next_fallback(model: str | None) -> str | None:
    """장애 모델을 기록하고 아직 실패하지 않은 다음 후보를 돌려준다 (없으면 None)."""
    if model:
        _failed_models.add(model)
    for m in [DEFAULT_MODEL] + FALLBACK_MODELS:
        if m not in _failed_models:
            return m
    return None


def _model_kwargs(kw: dict) -> dict:
    """모델별 인자 정리 — NO_THINK(chat_template_kwargs)는 qwen 전용이라 타 모델에선 뺀다 (400 방지)."""
    if not str(kw.get("model", "")).startswith("qwen"):
        return {k: v for k, v in kw.items() if k != "extra_body"}
    return kw


def _should_fallback(e: Exception) -> bool:
    """다른 모델로 갈아탈 상황인가 — 일시 장애(429/5xx/DEGRADED/타임아웃/연결) 또는
    404(모델·엔드포인트 없음: 설정 모델이 NIM에서 내려간 경우)."""
    if isinstance(e, (RateLimitError, APIConnectionError)):
        return True
    if isinstance(e, APIStatusError):
        return _transient_status(e) or e.status_code == 404
    return False


async def _try_seq(kw, delays):
    """한 모델에 대한 재시도 시퀀스 — 재시도 가능한 오류만 백오프, 아니면 즉시 raise."""
    last: Exception | None = None
    for i, delay in enumerate(delays):
        if delay:
            await asyncio.sleep(delay)
        try:
            return await get_llm().chat.completions.create(**_model_kwargs(kw))
        except (RateLimitError, APIStatusError, APIConnectionError) as e:
            # 404는 같은 모델을 재시도해도 소용없다 — 즉시 빠져나가 폴백에 맡긴다
            if isinstance(e, APIStatusError) and e.status_code == 404:
                raise
            if isinstance(e, APIStatusError) and not isinstance(e, RateLimitError) and not _transient_status(e):
                raise
            last = e
    raise last


async def _create(**kw):
    """재시도 + 모델 폴백. 폴백 성공 시 _model_cache를 갱신해 같은 파이프라인의 남은 단계도
    폴백 모델을 쓰게 한다 (단계마다 죽은 모델의 타임아웃 비용을 다시 내지 않는다).

    tool 호출 여부로 전략을 나눈다:
    - tool 호출(병렬 tool_call 사용): 폴백 모델이 병렬 tool을 못 하는 경우가 많아(예: llama-3.3),
      기본 모델(qwen)을 여러 번 재시도한다 — qwen은 과부하 시 간헐적으로 복구된다.
    - 비-tool 호출(대화·병합·검증 마무리): 폴백 모델도 문제없이 처리하므로 빠르게 폴백한다.
    """
    is_tool_call = bool(kw.get("tools"))
    primary_delays = (0, 6, 15) if is_tool_call else (0,)
    try:
        return await _try_seq(kw, delays=primary_delays)
    except (RateLimitError, APIStatusError, APIConnectionError) as e:
        if not _should_fallback(e):
            raise
        fb = _next_fallback(kw.get("model"))
        if not fb:
            raise
        # tool 호출에서 폴백 모델로 전환하면 성공해도 캐시에 고정하지 않는다 — 병렬 tool
        # 비호환으로 다음 tool 단계가 깨질 수 있으니, 각 단계가 기본 모델을 다시 시도하게 둔다.
        if not is_tool_call:
            _model_cache["id"] = fb
        return await _try_seq({**kw, "model": fb}, delays=(0, 4, 12))


def to_openai_tools(mcp_tools) -> list[dict]:
    """MCP 도구(name·description·inputSchema) → OpenAI function 스펙 (Day7 그대로)."""
    return [{"type": "function", "function": {
        "name": t.name, "description": t.description or "", "parameters": t.inputSchema}} for t in mcp_tools]


def _short(args: dict, n: int = 90) -> str:
    s = json.dumps(args, ensure_ascii=False, default=str)
    return s if len(s) <= n else s[:n] + "…"


async def plain_chat(system: str, user: str, *, temperature: float = 0.2, max_tokens: int = 1200) -> str:
    """도구 없는 순수 호출 — 계약 추출·병합 등 '판단만' 하는 단계용."""
    model = await resolve_model()
    r = await _create(
        model=model, temperature=temperature, max_tokens=max_tokens,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        extra_body=NO_THINK,
    )
    return r.choices[0].message.content or ""


async def stream_chat(system: str, user: str, *, temperature: float = 0.2, max_tokens: int = 1200):
    """도구 없는 순수 호출의 스트리밍판 — 토큰 델타를 실시간으로 yield한다 (채팅 UI 스트리밍 표시용).

    재시도(429·5xx·연결 오류)는 스트림 생성 시점까지만 적용한다 — 이미 델타를 화면에 내보낸
    뒤에는 되돌릴 수 없으므로, 스트림이 한 번 시작되면 중간 오류는 호출부로 그대로 전파해
    ui.py가 '일부만 표시됨' 에러 상태로 처리하게 한다.
    """
    model = await resolve_model()
    last: Exception | None = None
    stream = None
    # 스트림 생성 시점까지만 재시도·모델 폴백 (델타를 이미 내보낸 뒤에는 되돌릴 수 없음)
    for attempt_model in [model] + [m for m in ([DEFAULT_MODEL] + FALLBACK_MODELS) if m != model]:
        for delay in (0, 3, 8, 20):
            if delay:
                await asyncio.sleep(delay)
            try:
                stream = await get_llm().chat.completions.create(**_model_kwargs(dict(
                    model=attempt_model, temperature=temperature, max_tokens=max_tokens,
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                    extra_body=NO_THINK, stream=True,
                )))
                break
            except RateLimitError as e:
                last = e
            except APIStatusError as e:
                if _transient_status(e):
                    last = e
                else:
                    raise
            except APIConnectionError as e:
                last = e
        if stream is not None:
            if attempt_model != model:
                _model_cache["id"] = attempt_model   # 폴백 성공 → 이후 호출도 이 모델 사용
            break
        _failed_models.add(attempt_model)
    if stream is None:
        raise last
    try:
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    finally:
        await stream.close()   # 호출부가 소비를 중도 포기해도(예외·조기 종료) 커넥션을 확실히 반납


async def run_tool_agent(
    *,
    name: str,
    server,
    system: str,
    task: str,
    allow: set[str] | None = None,
    max_steps: int = 8,
    log=None,
    temperature: float = 0.2,
    max_tokens: int = 1600,
) -> tuple[str, list[str]]:
    """이름 있는 역할 에이전트 하나를 도구 루프로 실행한다.

    반환: (최종 텍스트, evidence) — evidence는 실제 도구 호출 결과 원문 목록이다.
    @critic이 활동의 why·open_hours가 창작인지 판정할 근거로 쓴다 (D4, evidence 기반 검증).
    """
    model = await resolve_model()
    log = log or (lambda s: None)
    evidence: list[str] = []
    async with Client(server) as client:
        tools = await client.list_tools()
        if allow is not None:                      # 도구를 골라 주는 것 = 권한 경계
            tools = [t for t in tools if t.name in allow]
        specs = to_openai_tools(tools)
        messages = [{"role": "system", "content": system}, {"role": "user", "content": task}]
        for _ in range(max_steps):
            m = (await _create(
                model=model, messages=messages, tools=specs,
                temperature=temperature, max_tokens=max_tokens, extra_body=NO_THINK,
            )).choices[0].message
            if not m.tool_calls:                   # 도구를 더 안 부르면 정상 종료
                log(f"[{name}] ✅ 완료")
                return m.content or "", evidence
            messages.append({"role": "assistant", "content": m.content or "",
                             "tool_calls": [tc.model_dump() for tc in m.tool_calls]})
            for tc in m.tool_calls:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                log(f"[{name}] 🔧 {tc.function.name}({_short(args)})")
                try:
                    res = await client.call_tool(tc.function.name, args)
                    content = json.dumps(res.data, ensure_ascii=False, default=str)
                    evidence.append(f"[{tc.function.name}({_short(args)})] {content[:2000]}")
                except Exception as e:             # 오류도 관찰로 되먹인다 → self-correction
                    content = "오류: " + (str(e).splitlines()[-1] if str(e) else type(e).__name__)
                    log(f"[{name}] ⚠️ {content[:120]}")
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": content[:20000]})

        # 한도 도달 → 도구 없이 마무리 호출 (계획 단계에 tools를 안 주는 것과 같은 원리로,
        # tools를 빼면 모델은 반드시 텍스트를 낸다) — 에이전트가 빈손으로 끝나는 일을 막는다.
        log(f"[{name}] ⏳ 도구 한도({max_steps}) 도달 — 지금까지의 결과로 마무리")
        messages.append({"role": "user", "content":
                         "도구 호출은 여기까지다. 지금까지 확보한 도구 결과만 사용해서, "
                         "요구된 최종 JSON을 필수 항목(모든 날짜·슬롯)을 빠뜨리지 말고 지금 바로 출력하라."})
        m = (await _create(
            model=model, messages=messages,
            temperature=temperature, max_tokens=max_tokens, extra_body=NO_THINK,
        )).choices[0].message
        log(f"[{name}] ✅ 완료 (마무리 모드)")
        return m.content or "", evidence
