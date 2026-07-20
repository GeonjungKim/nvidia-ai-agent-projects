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


async def _create(**kw):
    """429·5xx·연결 오류 재시도 (백오프 3/8/20초)."""
    last: Exception | None = None
    for delay in (0, 3, 8, 20):
        if delay:
            await asyncio.sleep(delay)
        try:
            return await get_llm().chat.completions.create(**kw)
        except RateLimitError as e:
            last = e
        except APIStatusError as e:
            if e.status_code and e.status_code >= 500:
                last = e
            else:
                raise
        except APIConnectionError as e:
            last = e
    raise last


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
) -> str:
    """이름 있는 역할 에이전트 하나를 도구 루프로 실행한다."""
    model = await resolve_model()
    log = log or (lambda s: None)
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
                return m.content or ""
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
        return m.content or ""
