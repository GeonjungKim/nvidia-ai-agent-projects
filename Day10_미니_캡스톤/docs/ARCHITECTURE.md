# TabeTabi — 아키텍처

> 이 문서의 다이어그램은 **실제 코드 기준**으로 작성되었다 (GitHub에서 mermaid가 바로 렌더링된다).
> 핵심 설계 원칙: **판단은 LLM이, 계산·검증·확정은 코드가** 한다.

## 1. 컴포넌트 다이어그램

```mermaid
flowchart TD
    U(["사용자"]) <--> UI["Streamlit 채팅 UI<br/>(ui.py)"]
    UI <-->|"대화 스트리밍 · 계약(Contract) 추출"| C["🎩 @concierge<br/>대화·계약·병합 지휘<br/>(도구 없는 순수 LLM + 결정론 파이프라인 코드)"]

    subgraph PIPE["run_pipeline() — concierge.py"]
        direction TB
        LOCK["계약 고정<br/>locked 식당은 코드가 DB 조회로 확정<br/>(LLM 불개입)"]
        MERGE["병합 (도구 없는 LLM)<br/>후보 밖 선택·중복은 코드가 교정<br/>누락 슬롯은 결정론 백필"]
        LOGI["로지스틱스 (결정론 코드)<br/>동선 NN 정렬 · 경유지 지도 URL<br/>항공/숙소 딥링크"]
    end

    C --> LOCK
    LOCK -->|"배치1: asyncio.gather 병렬"| F["🍜 @foodie<br/>열린 슬롯 식당 후보<br/>(슬롯당 2곳)"]
    LOCK -->|"배치1: asyncio.gather 병렬"| S["🔭 @scout<br/>활동·날씨·호텔·항공 시세"]
    F --> MERGE
    S --> MERGE
    MERGE --> CR["⚖️ @critic<br/>읽기 전용 검증 게이트<br/>불합격 시 병합 1회 재시도"]
    CR --> LOGI
    LOGI --> UI

    F <-->|"search_restaurants<br/>list_areas · list_genres"| DB[("Tabelog DB MCP 서버<br/>SQLite · 유니크 식당 45,725곳<br/>읽기 전용 URI")]
    CR <-->|"get_restaurant (단 1개)"| DB
    S <-->|"web_search"| WS["웹검색 MCP 서버<br/>(Tavily · 키 없으면 링크 폴백)"]
```

**도구 허용 목록 = 권한 경계**

| 에이전트 | 구현 | 허용 도구 | 이유 |
|---|---|---|---|
| @concierge | `agents/concierge.py` | 없음 (순수 LLM) | 판단만 한다 — 계획 단계에 tools를 주면 실행해버린다 |
| @foodie | `agents/foodie.py` | `search_restaurants` `list_areas` `list_genres` | DB 결과 밖 식당을 "말할 수 없다" → 환각 구조 차단 |
| @scout | `agents/scout.py` | `web_search` | DB 접근 불가 — 식당 추천에 관여 불가 |
| @critic | `agents/critic.py` | `get_restaurant` 1개 | 읽기 전용 — 수정 능력 자체가 없다 |

## 2. 시퀀스 다이어그램

```mermaid
sequenceDiagram
    actor U as 사용자
    participant UI as Streamlit UI<br/>(ui.py)
    participant C as @concierge<br/>(concierge.py)
    participant F as @foodie
    participant S as @scout
    participant CR as @critic
    participant DB as Tabelog DB MCP
    participant WS as 웹검색 MCP

    U->>UI: "오모테산도 근처 맛집 포함된 여행 일정 짜줘"
    UI->>C: ConciergeTurn (대화 이력 + 계약 초안)
    C-->>UI: 답변 토큰 스트리밍 + 계약 JSON 갱신 (마커 분리)
    Note over U,C: 필수 정보(지역·날짜)가 모일 때까지 멀티턴 반복 → ready=true

    U->>UI: [일정 생성] 버튼
    UI->>C: run_pipeline(contract)
    C->>DB: 고정(locked) 식당 코드 확정 (4단계 매칭)

    par 배치1 — asyncio.gather 병렬
        C->>F: 열린 슬롯 후보 요청
        F->>DB: search_restaurants (병렬 tool call)
        DB-->>F: 후보 (id·평점·예산·역·링크)
        F-->>C: 슬롯별 후보 2곳 JSON
    and
        C->>S: 활동·날씨·호텔·항공 리서치
        S->>WS: web_search (≤9회)
        WS-->>S: 스니펫 + URL
        S-->>C: 활동/날씨/호텔/항공 JSON + evidence
    end

    C->>C: 병합 (도구 없는 LLM) → 코드 교정·백필
    C->>CR: 식당 + 활동 + 항공 기준선 검증 요청 (evidence 첨부)
    CR->>DB: get_restaurant (유령 id·계약 위반 검사)
    CR-->>C: {"pass": bool, "issues": [...]}

    opt 불합격 시 (self-correction, 1회)
        C->>C: 지적사항 반영해 병합 재시도
        C->>CR: 재검증
    end

    C->>C: 로지스틱스 (결정론): 동선 정렬·지도 경로·딥링크
    C-->>UI: 완성 일정 JSON
    UI-->>U: 일정표 카드 + st.map + 에이전트 실행 로그
    Note over U,UI: 대화 계속 가능 — 계약 수정 후 재생성 (Multi-turn)
```

## 3. 모듈 다이어그램

> 에이전트는 클래스 상속 계층이 아니라 **공용 도구 루프(`run_tool_agent`)를 공유하는 함수들**이다.
> 상태를 가진 클래스는 `TripContract`(계약)와 `ConciergeTurn`(스트리밍 1턴) 둘뿐.

```mermaid
classDiagram
    class ui_py["ui.py (Streamlit)"] {
        +채팅 스트리밍 표시
        +일정 카드 · st.map
        +세션 저장 (store.py)
    }
    class ConciergeTurn {
        +stream() 토큰 스트리밍
        +result() (reply, draft, ready)
    }
    class TripContract {
        +pref / start_date / end_date
        +areas · stay_area · day_anchors
        +locked[] · genres_pref · budget
        +is_ready() bool
        +effective_day_anchors()
    }
    class concierge_py["agents/concierge.py"] {
        +concierge_reply()
        +run_pipeline(contract) itinerary
        -_resolve_locked() 코드 확정
        -_merge() 도구 없는 LLM
        -_picks_from() 코드 교정
        -_backfill() 결정론 백필
    }
    class loop_py["agents/loop.py"] {
        +run_tool_agent(server, allow, ...)
        +plain_chat() / stream_chat()
        +resolve_model() · 재시도 백오프
    }
    class foodie_py["agents/foodie.py"] { +run_foodie() }
    class scout_py["agents/scout.py"] { +run_scout() }
    class critic_py["agents/critic.py"] { +run_critic() }
    class tabelog_server["tools/tabelog_server.py (FastMCP)"] {
        +search_restaurants()
        +get_restaurant()
        +list_areas() · list_genres() · list_prefs()
        +fetch_by_ids() 라이브러리 겸용
    }
    class search_server["tools/search_server.py (FastMCP)"] {
        +web_search() Tavily · 링크 폴백
    }
    class detlib["결정론 라이브러리<br/>anchors · geo · links<br/>timemodel · resolve · render"] {
        +앵커 해석 · NN 동선 정렬
        +지도/항공/숙소 딥링크
        +활동 시간표 배치 · 렌더링
    }

    ui_py --> ConciergeTurn
    ui_py --> concierge_py : run_pipeline
    ConciergeTurn --> loop_py : stream_chat
    concierge_py --> TripContract
    concierge_py --> foodie_py : 배치1 병렬
    concierge_py --> scout_py : 배치1 병렬
    concierge_py --> critic_py : 게이트
    concierge_py --> detlib
    foodie_py --> loop_py : run_tool_agent
    scout_py --> loop_py : run_tool_agent
    critic_py --> loop_py : run_tool_agent
    foodie_py ..> tabelog_server : allow 3개
    critic_py ..> tabelog_server : get_restaurant만
    scout_py ..> search_server : web_search
```

## 환각 3중 방어

1. **권한 경계** — @foodie는 DB 도구 결과에서만 후보를 뽑는다.
2. **코드 재조인** — 화면의 이름·평점·링크는 전부 `restaurant_id`로 DB에서 재조회. LLM이 전사한 텍스트를 신뢰하지 않는다.
3. **@critic 게이트 + 코드 교정** — 유령 id·계약 위반·창작 근거(evidence 대조)를 검증하고, 후보 밖 선택은 코드가 교정, 누락 슬롯은 베이지안 랭킹 상위로 결정론 백필.
