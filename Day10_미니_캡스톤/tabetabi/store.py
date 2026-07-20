"""세션 저장소 — 대화·계약·생성된 일정을 SQLite에 영속화한다 (가점: DB 저장).

읽기 전용 타베로그 DB(app.db, C-1 원칙)와는 완전히 별개의 쓰기 가능 DB다 — 이 모듈은
타베로그 DB를 절대 열지 않는다. 로그인 없이도(익명 세션 id, URL 쿼리파라미터로 유지)
동작하고, Google 로그인 시 이메일로 묶여 대화 히스토리가 계정별로 쌓인다.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone

from tabetabi.config import BASE_DIR

SESSIONS_DB_PATH = BASE_DIR / "sessions.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    user_key TEXT NOT NULL,
    user_label TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    draft_json TEXT,
    messages_json TEXT,
    itinerary_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_key, updated_at);
"""


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(SESSIONS_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    return conn


def new_session_id() -> str:
    return uuid.uuid4().hex[:16]


def save_session(session_id: str, user_key: str, user_label: str,
                 draft: dict, messages: list[dict], itinerary: dict | None) -> None:
    """현재 상태를 upsert한다 — 채팅 턴·일정 생성 등 의미 있는 변화가 있을 때마다 호출."""
    now = datetime.now(timezone.utc).isoformat()
    draft_json = json.dumps(draft or {}, ensure_ascii=False, default=str)
    messages_json = json.dumps(messages or [], ensure_ascii=False, default=str)
    itinerary_json = json.dumps(itinerary, ensure_ascii=False, default=str) if itinerary else None
    conn = _conn()
    try:
        conn.execute(
            """INSERT INTO sessions
               (session_id, user_key, user_label, created_at, updated_at, draft_json, messages_json, itinerary_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(session_id) DO UPDATE SET
                 user_key=excluded.user_key, user_label=excluded.user_label, updated_at=excluded.updated_at,
                 draft_json=excluded.draft_json, messages_json=excluded.messages_json,
                 itinerary_json=excluded.itinerary_json""",
            (session_id, user_key, user_label, now, now, draft_json, messages_json, itinerary_json),
        )
        conn.commit()
    finally:
        conn.close()


def load_session(session_id: str) -> dict | None:
    conn = _conn()
    try:
        row = conn.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
        if not row:
            return None
        return {
            "session_id": row["session_id"],
            "user_key": row["user_key"],
            "user_label": row["user_label"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "draft": json.loads(row["draft_json"]) if row["draft_json"] else {},
            "messages": json.loads(row["messages_json"]) if row["messages_json"] else [],
            "itinerary": json.loads(row["itinerary_json"]) if row["itinerary_json"] else None,
        }
    finally:
        conn.close()


def list_sessions(user_key: str, limit: int = 10) -> list[dict]:
    """이 사용자(user_key)의 대화 히스토리 — 최근 수정순. 사이드바 대화 목록용.

    제목 우선순위: 첫 사용자 메시지 요약 → 도시·기간 → "새 대화" (ChatGPT/Claude식 목록 UX).
    """
    from tabetabi.links import city_of
    conn = _conn()
    try:
        rows = conn.execute(
            "SELECT session_id, updated_at, draft_json, messages_json, itinerary_json FROM sessions "
            "WHERE user_key = ? ORDER BY updated_at DESC LIMIT ?",
            (user_key, max(1, limit)),
        ).fetchall()
        out = []
        for r in rows:
            draft = json.loads(r["draft_json"]) if r["draft_json"] else {}
            try:
                msgs = json.loads(r["messages_json"]) if r["messages_json"] else []
            except (json.JSONDecodeError, TypeError):
                msgs = []
            first_user = next((str(m.get("content", "")).strip().replace("\n", " ")
                               for m in msgs if m.get("role") == "user"), "")
            if first_user:
                label = first_user[:24] + ("…" if len(first_user) > 24 else "")
            elif draft.get("pref"):
                city_ko, _ = city_of(draft["pref"])
                dates = f" {draft.get('start_date', '')}~" if draft.get("start_date") else ""
                label = f"{city_ko}{dates}".strip()
            else:
                label = "새 대화"
            out.append({
                "session_id": r["session_id"],
                "updated_at": r["updated_at"],
                "label": label,
                "has_itinerary": bool(r["itinerary_json"]),
            })
        return out
    finally:
        conn.close()


def delete_session(session_id: str, user_key: str) -> None:
    """세션 삭제 — user_key까지 일치해야 지운다 (다른 사용자 세션 삭제 방지)."""
    conn = _conn()
    try:
        conn.execute("DELETE FROM sessions WHERE session_id = ? AND user_key = ?", (session_id, user_key))
        conn.commit()
    finally:
        conn.close()
