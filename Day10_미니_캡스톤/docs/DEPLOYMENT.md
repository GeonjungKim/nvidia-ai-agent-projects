# TabeTabi 배포 가이드

## TL;DR — 추천 배포 전략

현재 코드는 **Streamlit(Python) + 인메모리 FastMCP + 읽기 전용 SQLite(41MB)** 구성이다.
따라서:

| 단계 | 스택 | 이유 |
|---|---|---|
| **1단계 (지금 바로, 추천)** | **Streamlit Community Cloud** 단일 배포 | 코드 수정 0줄. MCP 서버는 인프로세스로 돌고, DB는 리포에 포함(41MB < GitHub 100MB 제한). Vercel·Neon·Horizon **전부 불필요** |
| 2단계 (포트폴리오 고도화) | v0 → Vercel(Next.js) + FastAPI 백엔드 + Neon(Postgres) + Prefect Horizon(MCP) | UI를 Next.js로 재작성할 때만 의미가 있다. 현 Streamlit UI는 Vercel에 올릴 수 없다 |

> ⚠️ 흔한 오해: Vercel은 Next.js/프런트엔드 플랫폼이라 **Streamlit 앱을 호스팅할 수 없다.**
> Neon은 Postgres라 SQLite를 그대로 못 쓴다(스키마 이전 필요). Prefect Horizon은 MCP 서버 호스팅용이라
> 에이전트 루프(오케스트레이터) 자체는 별도 Python 백엔드가 필요하다. 지금 코드엔 셋 다 과투자다.

---

## 1단계 — Streamlit Community Cloud (권장, ~15분)

### 1. GitHub 리포 준비

```bash
git init
git add .
git commit -m "TabeTabi v1"
# GitHub에서 새 리포 생성 후:
git remote add origin https://github.com/<계정>/<리포>.git
git push -u origin main
```

체크리스트:
- [ ] `.gitignore`에 `.env` / `API.txt` / `sessions.db`가 있는지 확인 (루트에 준비돼 있음)
- [ ] `Tabelog_Recommendation/app.db`(41MB)는 **커밋한다** — 배포에 필요
- [ ] 커밋 전 `git status`로 API 키 파일이 안 올라가는지 재확인

### 2. Streamlit Cloud 앱 생성

1. https://share.streamlit.io → GitHub 계정으로 로그인
2. **New app** → 리포 선택
3. 설정:
   - **Main file path**: `Day10_미니_캡스톤/ui.py`
   - **Python version**: 3.13 (Advanced settings)
4. **Advanced settings → Secrets**에 입력 (Streamlit Cloud는 secrets를 환경변수로도 주입한다):

```toml
NVIDIA_API_KEY = "nvapi-..."
TAVILY_API_KEY = "tvly-..."
GOOGLE_MAPS_API_KEY = "..."       # 선택 — DB 미등록 장소 지도 핀 검증 (없으면 링크 폴백)
TABELOG_DIR = "Tabelog_Recommendation"
```

> `TABELOG_DIR`은 리포 루트 기준 상대경로. `config.py`가 `os.getenv("TABELOG_DIR")`를 읽으므로 그대로 동작한다.
> requirements는 `Day10_미니_캡스톤/requirements.txt`를 자동 감지한다 (main file 기준 탐색).

5. **Deploy** → 2~3분 뒤 `https://<앱이름>.streamlit.app` 공개 URL 완성

### 3. 배포 후 확인

- 채팅에 예시 문장 입력 → 계약 추출 스트리밍 확인
- [일정 생성] → 에이전트 로그에 `@foodie ∥ @scout` 병렬 실행과 `@critic` 판정이 찍히는지 확인
- Tavily 키를 안 넣었으면 활동 항목이 "구글 검색 링크 폴백"으로 나오는 게 정상 (fail-soft)

---

## 2단계 — 목표 아키텍처 (Next.js + Vercel + Neon + Horizon)

UI를 Next.js로 재작성하기로 결정했을 때의 로드맵. **작업량: UI 전면 재작성 + 백엔드 API화 + DB 이전.**

### 아키텍처

```
브라우저 ── Vercel (Next.js, v0로 디자인)
              │  /api/chat, /api/itinerary (스트리밍 프록시)
              ▼
        FastAPI 백엔드 (Render/Railway/Fly.io — Python 에이전트 루프 호스팅)
              │                         │
              ▼                         ▼
   Prefect Horizon (FastMCP 서버 2개)   NVIDIA NIM (LLM)
              │
              ▼
        Neon (Postgres — restaurants_agg 이전)
```

### Step 1 — DB: SQLite → Neon Postgres

1. https://neon.com → 프로젝트 생성 → 연결 문자열 복사 (`postgresql://...`)
2. 스키마·데이터 이전 (택1):
   ```bash
   # pgloader (가장 간단)
   pgloader sqlite://Tabelog_Recommendation/app.db postgresql://<neon-연결문자열>
   ```
   또는 Python 스크립트로 `restaurants_agg`·`restaurant_genres` 두 테이블만 복사
3. `tabetabi/tools/tabelog_server.py`의 `sqlite3` 연결부를 `psycopg`로 교체
   (쿼리는 표준 SQL이라 `group_concat → string_agg` 정도만 수정)

### Step 2 — MCP 서버: Prefect Horizon

FastMCP는 Prefect 팀이 만든 프레임워크라 Horizon과 궁합이 좋다. 루프 코드는 서버 객체 대신 URL을 넘기면 끝 (`Client(server)` → `Client("https://...")` — 코드 구조 무변경).

1. https://horizon.prefect.io → GitHub 로그인 → 리포 연결
2. 서버 엔트리포인트 지정: `tabetabi/tools/tabelog_server.py`의 `mcp`, `search_server.py`의 `mcp`
   (로컬 검증: `fastmcp run tabetabi/tools/tabelog_server.py:mcp --transport http`)
3. 환경변수 등록: `TAVILY_API_KEY`, Neon `DATABASE_URL`
4. 발급된 URL을 백엔드 환경변수 `TABELOG_MCP_URL` / `SEARCH_MCP_URL`로 주입

### Step 3 — 백엔드: FastAPI (Render 또는 Railway)

Vercel은 Python 장기 실행(1분짜리 파이프라인)에 부적합 → 별도 Python 호스트 필요.

1. `api/main.py` 작성 — 기존 함수를 그대로 감싼다:
   - `POST /chat` → `concierge_reply()` (SSE 스트리밍은 `stream_chat` 활용)
   - `POST /itinerary` → `run_pipeline()` (StreamingResponse로 로그 이벤트 전송)
2. Render/Railway에 GitHub 연결 → 환경변수(NVIDIA·Tavily·MCP URL·DATABASE_URL) 설정 → 배포

### Step 4 — 프런트엔드: v0 → Vercel

1. https://v0.app 에서 디자인 생성 — 프롬프트 예:
   > "여행 일정 플래너 채팅 앱. 왼쪽 채팅(스트리밍), 오른쪽 일정표 카드(날짜별 점심/카페/저녁 + 평점·링크·지도). 다크모드."
2. 만족스러우면 **"Add to Codebase" / GitHub 리포로 내보내기** (v0와 Vercel은 동일 계정)
3. Next.js API Route(`app/api/*/route.ts`)에서 FastAPI 백엔드로 프록시 (백엔드 URL은 서버 환경변수로 — 브라우저에 직접 노출 금지)
4. https://vercel.com → 리포 import → 환경변수 `BACKEND_URL` 설정 → Deploy

### Step 5 — 마무리

- CORS: FastAPI에 Vercel 도메인 허용
- Vercel 도메인 연결, Neon은 무료 티어 autosuspend 주의 (첫 쿼리 콜드스타트 ~1초)
- Streamlit 버전은 데모/백업용으로 유지 가능

---

## 환경변수 총정리

| 변수 | 용도 | 1단계 | 2단계 |
|---|---|---|---|
| `NVIDIA_API_KEY` | NIM LLM 호출 | Streamlit secrets | FastAPI 호스트 |
| `TAVILY_API_KEY` | 웹검색 (선택) | Streamlit secrets | Horizon |
| `TABELOG_DIR` | DB·좌표 데이터 경로 | `Tabelog_Recommendation` | — (Neon으로 대체) |
| `LLM_MODEL` | 모델 교체 (선택) | 선택 | 선택 |
| `DATABASE_URL` | Neon Postgres | — | Horizon·FastAPI |
