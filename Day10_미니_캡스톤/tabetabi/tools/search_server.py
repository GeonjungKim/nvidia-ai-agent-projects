"""웹검색 MCP 서버 — Tavily 기반, 키가 없으면 검색 링크 폴백(fail-soft).

Day9 Lab3 원칙: 검색 키는 서버(도구) 안에서만 쓴다.
"""
from __future__ import annotations

import urllib.parse

from fastmcp import FastMCP

mcp = FastMCP("WebSearch")

_client = None


def _tavily():
    global _client
    if _client is None:
        from tavily import TavilyClient

        from tabetabi.config import TAVILY_API_KEY
        _client = TavilyClient(api_key=TAVILY_API_KEY)
    return _client


def web_search_lib(query: str, max_results: int = 5) -> list[dict]:
    """web_search의 라이브러리판 — MCP 도구와 결정론 코드(resolve의 웹 조인)가 같은 로직을 쓴다."""
    from tabetabi.config import TAVILY_API_KEY
    max_results = max(1, min(int(max_results), 8))
    if not TAVILY_API_KEY:
        q = urllib.parse.quote(query)
        return [{
            "title": f"구글 검색으로 확인: {query}",
            "url": f"https://www.google.com/search?q={q}",
            "snippet": "TAVILY_API_KEY 미설정 — 링크 폴백 모드. 이 링크를 그대로 활동 항목으로 안내하라.",
        }]
    r = _tavily().search(query, max_results=max_results)
    return [
        {"title": x.get("title", ""), "url": x.get("url", ""), "snippet": (x.get("content") or "")[:300]}
        for x in r.get("results", [])
    ]


@mcp.tool
def web_search(query: str, max_results: int = 5) -> list[dict]:
    """웹에서 최신 정보를 검색한다 (관광지·이벤트·날씨 등). 결과: title/url/snippet.

    검색어는 구체적으로 쓸 것 (예: '2026년 8월 도쿄 신주쿠 주변 가볼만한 곳').
    """
    return web_search_lib(query, max_results)
