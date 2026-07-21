# PHASE1_SPEC.md — 구현 명세 v2.1 (2026-07-09)

> v2.0→v2.1: M12 소패치 — 역 검색 정확/부분 일치 토글(기본 정확) + 대표역만 옵션,
> 점심 예산 필터 정식 추가(§3 DDL에 `budget_lunch_floor` 컬럼, §8 비범위 목록에서 제거).
> §14 이후의 search 시맨틱(agg 기준)은 불변.

> v1.7→v2.0: **§14 M9 다중 리뷰어(식당 단위 집계 — 시맨틱 변경)**, §15 M10(페이지네이션·지도 상호작용),
> §16 M11(Community Cloud 배포). §3~§13은 불변이되 §14가 search 시맨틱을 상위 정의로 대체.

> v1.5→v1.7: §13 M8 — 역명 라벨 + 지도. v1.6(Google 임베디드) 설계는 비용 구조 결함으로 §13에서 전면 개정(무키·무API).
> 역명 ko/en은 설계 세션 빌드타임 생성(stations_i18n.py, 1,142건: 국립국어원 대조표 결정론 변환 + 50건 수동검증) — §10의 駅データ.jp 정식 경로는 정밀화 단계로 유지.

> v1.4→v1.5: §12 M7(지역 라벨 코드 제거·지도 링크 확장) 추가, §10에 역명 현지화 정식 경로 보강.

> v1.3→v1.4: §11 M6(다국어 표시·유도형 지역 라벨·레이아웃 수정) 추가. 데이터·쿼리 시맨틱 불변.

> v1.2.1→v1.3: §9 M5(UI 개선 — pref 한국어 라벨·다중 선택·팝오버 보드·역 검색·지도 링크) 추가,
> §10 Phase 1.5 로드맵(핀 지도·지역명 — 확장 v1.4.3 보강 크롤 전제) 추가. §3~§6 기존 기준 불변.

> v1.2→v1.2.1: tokyo×ラーメン 수용값 5619→**5634** 정정 (rated 부분집합을 셀 크기로 오기재. Session 0 감사에서 발견).

> v1.1→v1.2: 입력 파일 교체(20260706, 14,281건) 및 수용 상수 전면 재계산(**m=243으로 변경**) /
> **M4를 로컬 Qwen 추론으로 재작성(C안)** / 금액대(budget) 필터 정식 추가 /
> 의존성 목록 갱신(anthropic 제거, llmft 기존 스택 사용).

요구사항분석서 v1.2의 FR-09(적재) + FR-11(필터·랭킹) + 추천문 생성(축소판 Phase 3).
모든 수치는 `tabelog_maro_merged_20260706.json` 실측값이며 수용 테스트의 기준이 된다.

---

## 1. 스택 (확정)
Python 3.11 (conda `llmft`) / sqlite3(표준 라이브러리) / Streamlit / pytest.
LLM 생성: **로컬 Qwen2.5-1.5B-Instruct** (transformers + torch — `llmft` 환경 기존 설치분 사용).
**신규 설치 허용 = {streamlit, pytest}. 그 외 pip install 금지** (torch/transformers는 이미 있음 — 없다고 판단되면 멈추고 보고).

## 2. 입력 데이터 계약 (실측 확정, 2026-07-06)
`data/tabelog_maro_merged_20260706.json` — `{meta, records[]}`.
`meta.expected`(URL 86키)·`meta.losses`는 크롤 감사용 — **앱은 records만 읽는다.**

| 필드 | 타입 | 충전율 | 비고 |
|---|---|---|---|
| reviewer_id, reviewer_display_name | str | 100% | 현재 단일값 `maro`/`maro-j` |
| restaurant_id | str | 100% | (reviewer_id, restaurant_id) 파일 내 유일 |
| name, url | str | 100% | 동일 name·다른 id 존재(이전·재오픈 추정) → 병합 금지 |
| pref / area2 / area3 | str | 100% | pref 48종(47도도부현+`taiwan`) |
| genres | str[] | 100% | 203종 |
| stations | str[] | 100% | |
| tabelog_rating | float\|null | 99.3% | **null 94건** |
| tabelog_review_count | int | 100% | |
| budget_dinner / budget_lunch | str\|null | 80.5%/– | **고정 버킷 문자열: dinner 17종, lunch 16종** (자유 텍스트 아님) |
| closed_days | str\|null | ~43% | |
| awards | obj[] | 27.2% (**3,879건**) | `{type, year, rank?, category?, label}` |
| reviewer_rating | float\|null | 34.5% | |
| visited_month / visit_count | str / int | 100% | |
| review_url, bookmark_id, source_node | str | 100% | UI 미노출 |

## 3. M1 — 적재 (`app/load.py`)

### DDL
```sql
CREATE TABLE restaurants (
  reviewer_id TEXT NOT NULL,
  restaurant_id TEXT NOT NULL,
  name TEXT NOT NULL,
  url TEXT NOT NULL,
  pref TEXT NOT NULL,
  area2 TEXT NOT NULL,
  area3 TEXT NOT NULL,
  tabelog_rating REAL,
  tabelog_review_count INTEGER NOT NULL,
  reviewer_rating REAL,
  visit_count INTEGER NOT NULL,
  visited_month TEXT NOT NULL,
  budget_dinner TEXT,
  budget_lunch TEXT,
  budget_dinner_floor INTEGER,    -- 정렬용 하한 (§3 로직 5). null 허용
  budget_lunch_floor INTEGER,     -- 정렬용 하한 (§3 로직 5, v2.1). null 허용
  closed_days TEXT,
  stations_json TEXT NOT NULL,
  awards_json TEXT NOT NULL,
  award_count INTEGER NOT NULL,
  bayes_score REAL,
  PRIMARY KEY (reviewer_id, restaurant_id)   -- 크롤러 병합 키와 동일 (다중 리뷰어 대비)
);
CREATE TABLE restaurant_genres (
  restaurant_id TEXT NOT NULL,    -- 장르는 식당 수준 사실. INSERT OR IGNORE로 적재
  genre TEXT NOT NULL,
  PRIMARY KEY (restaurant_id, genre)
);
CREATE INDEX idx_r_region ON restaurants(pref, area2, area3);
CREATE INDEX idx_r_bayes  ON restaurants(bayes_score);
CREATE INDEX idx_g_genre  ON restaurant_genres(genre);
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
-- meta: global_mean_C, prior_m, source_file, record_count, loaded_at
```

### 로직
1. JSON 로드(`encoding="utf-8"`) → 레코드 수·필드 존재 검증. 불일치 시 즉시 abort, 부분 적재 금지.
2. `C` = tabelog_rating **비null** 레코드의 rating 평균(`statistics.mean`, 런타임 계산. 실측 3.489346).
   `m` = **동일 비null 집합**의 review_count `int(statistics.median(...))` (실측 **243**).
   ⚠ 전체 레코드 기준으로 계산하면 값이 달라짐 — 반드시 rated 집합 기준.
3. `bayes_score = (v*R + m*C)/(v+m)` — rating 비null 레코드만, null이면 null.
4. 단일 트랜잭션. 재실행 시 DROP 후 재생성(멱등).
5. `budget_dinner_floor`·`budget_lunch_floor`(v2.1): 각각 budget_dinner·budget_lunch 문자열에서
   **첫 숫자 그룹**(콤마 제거)을 int로. `～￥999`처럼 상한만 있으면 0.
   null이면 null. (예: `￥3,000～￥3,999`→3000, `￥100,000～`→100000)

### 수용 테스트 (tests/test_load.py — 전부 실측 기준값)
- `restaurants` 행수 == **14281**
- `COUNT(DISTINCT pref)` == **48**
- `tabelog_rating IS NULL` == **94**, 해당 행 `bayes_score IS NULL`
- `restaurant_genres` `COUNT(DISTINCT genre)` == **203**
- `award_count > 0` == **3879**
- meta `global_mean_C` ∈ [3.48, 3.50], `prior_m` == **243**
- `COUNT(DISTINCT budget_dinner)` (null 제외) == **17**
- budget_dinner_floor 스팟체크: `￥3,000～￥3,999`→3000, `～￥999`→0, null→null
- (v2.1) `COUNT(DISTINCT budget_lunch)` (null 제외) == **16**
- (v2.1) budget_lunch_floor 스팟체크: `￥3,000～￥3,999`→3000, `～￥999`→0, null→null
- 멱등성: 2회 실행 후 행수 14281 유지

## 4. M2 — 랭킹·필터

### 랭킹 (근거: IMDb 가중 평점 공식 / E. Miller, *Ranking Items With Star Ratings*)
기본 정렬 = `ORDER BY (bayes_score IS NULL) ASC, bayes_score DESC`
(⚠ `NULLS LAST`는 SQLite 3.30+ 전용 — 버전 무가정 포터블 형식 사용. 다른 정렬도 동일 패턴.)
`score = (v·R + m·C)/(v+m)`, C·m은 §3에서 데이터 유도값(meta 테이블에서 읽음).
설계 근거(실측 검증): 티어식 대비 경계 절벽 없음 / 희소 셀에서도 자연스러운 순서 /
m을 ±2 흔들어도 tokyo×ラーメン top1 불변(강건).

`ranking.py`: `bayes(v, R, m, C) -> float` 순수 함수 + meta에서 (m, C) 읽는 헬퍼.

### 정렬 옵션 (기본=bayes)
`bayes` | `rating` | `reviews` | `reviewer` — null은 전부 포터블 형식으로 뒤로.

### 필터 (`query.py`)
```
search(db, pref=None, area2=None, area3=None, genre=None,
       budget_dinner=None, sort="bayes", limit=30) -> list[dict]
```
- 지역: pref → area2 → area3 계단식. 상위 미지정+하위 지정 → `ValueError`.
- genre: `restaurant_genres` EXISTS 서브쿼리, 단일 선택.
- budget_dinner: **문자열 완전 일치** (17종 버킷이 곧 카테고리). null 레코드는 필터 시 제외됨.
- 0건은 정상 — 빈 리스트 반환(예외 금지). 파라미터 바인딩(`?`)만 사용.

### 수용 테스트 (tests/test_ranking.py, test_query.py)
- `bayes(2106, 4.07, 243, 3.489346)` ≈ **4.010** (±0.005)
- `bayes(1, 5.0, 243, 3.489346)` < **3.51**
- tokyo×`ラーメン` search() 결과 크기 == **5634** (전체 레코드 기준 — rating null 15건 포함, 정렬 시 뒤로),
  bayes 1위 name == **らぁ麺や 嶋**
  (참고: rating 비null 부분집합은 5619 — v1.2까지 이 값을 잘못 기재했었음. search는 null도 반환한다)
- nagano×`ラーメン` == **100**
- okinawa×`フレンチ` → `[]` (실측 0건 셀)
- budget 필터: tokyo×`ラーメン`×`￥1,000～￥1,999` 결과가 전부 해당 버킷 문자열인지
- 계단식 위반(pref 없이 area2 지정) → `ValueError`

## 5. M3 — UI (`app/ui.py`, Streamlit)
- 사이드바: pref(건수 병기, 동적 로드) → area2 → area3 계단식 /
  genre 셀렉트(선택 지역 내 건수 상위순) / **예산(저녁) 셀렉트 — budget_dinner_floor 오름차순 정렬, "전체" 기본** /
  정렬 라디오(bayes 기본).
- 결과 카드(상위 30): name(→url 링크), genres, stations, tabelog_rating+review_count,
  bayes_score, budget(夜/昼), awards 뱃지(`label` 원문), "리뷰어가 N회 방문(최근 YYYY/MM)".
- 예산 필터 사용 시 안내: "예산 미기재 식당은 제외됩니다" (결측 19.5%).
- 0건: 안내 + 상위 지역/필터 완화 제안. review_url 등 내부 필드 노출 금지(C-2).
- "추천문 생성" 버튼 → M4.

## 6. M4 — 추천문 생성 (`app/generate.py`) — **로컬 Qwen (C안)**

### 모델 로드
- `load_model()`: 경로 = 환경변수 `QWEN_MODEL_PATH`, 기본값 `"Qwen/Qwen2.5-1.5B-Instruct"`.
  사용자가 직접 파인튜닝한 체크포인트(LoRA merge_and_unload 후 저장 디렉토리)를 같은 변수로 주입.
- `AutoModelForCausalLM.from_pretrained(path, torch_dtype="auto", device_map="cuda")` +
  `AutoTokenizer.from_pretrained(path)`. CUDA 불가/OOM 등 로드 실패 → **템플릿 폴백 + 경고 문자열 반환** (fail-soft — 생성은 UX 기능이지 데이터 무결성이 아님).
- VRAM 근거: 1.5B×2byte(fp16)≈3.1GB < 8GB(RTX 4070 Laptop). 여유분은 KV캐시·CUDA 컨텍스트.
- ui.py에서 `@st.cache_resource`로 프로세스당 1회만 로드.

### 생성 계약
- 입력: 검색 상위 N(기본 5)의 구조화 사실만 — name, genres, stations, rating+review_count,
  budget, awards(label), visit_count.
- 메시지: system = "아래 구조화된 사실만 근거로 한국어 추천문 작성. 사실에 없는 내용(맛·분위기 묘사 등)
  창작 금지. 각 식당 1–2문장 + 전체 요약 1문장." / user = 사실 JSON.
- 프롬프트 조립은 `tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)`
  (Qwen2.5 모델 카드 공식 방식). 수동 특수토큰 문자열 조립 금지.
- 1차 생성: `max_new_tokens=512, do_sample=False` (greedy — 결정론).
- 검증: 출력에 입력에 없는 식당명 포함 시 1회 재시도(`do_sample=True, temperature=0.7`) →
  재실패 시 템플릿 폴백.
- 템플릿 폴백: f-string으로 동일 입력 사실 나열식 추천문 (API·모델 전무 상태에서도 데모 완주).

### 수용 테스트
- 템플릿 폴백: 고정 입력 3건 → 출력에 3개 식당명 전부 포함 (자동화).
- 모델 경로: `load_model`/`generate` 호출은 **mock** — 테스트에서 실제 모델 로드·GPU 사용 금지.
- 프롬프트 조립 함수는 순수 함수로 분리해 메시지 구조(역할 2개, 사실 포함) 단위 테스트.

## 7. 일정 (수요일 완료)
- **월**: M1 + M2 / **화**: M3 + 실사용 점검 / **수 오전**: M4 + 데모 시나리오
  (tokyo×ラーメン 정렬 비교 → 예산 필터 → 0건 셀 → 추천문 생성).
- 파인튜닝(사용자 직접)은 앱과 독립 — 앱은 `QWEN_MODEL_PATH` 교체만으로 반영.

## 8. 명시적 비범위 (v1)
- 다중 리뷰어 데이터(스키마는 복합 PK로 대응 완료 — 병합 파일 교체+재적재만 필요)
- 리뷰 본문·임베딩 RAG(FR-08, OI-3 미해결), 좌표·지도(OI-9), 다중 장르 동시 필터
  (점심 예산 필터는 v2.1 M12에서 구현 완료 — 더 이상 비범위 아님)


## 9. M5 — UI·검색 개선 (v1.3 신규, 수요일 범위)

### 9.1 pref 한국어 라벨 (`app/labels.py` 신규)
- `PREF_LABELS: dict[str, str]` — 실데이터 pref 슬러그 **48종 전부**에 대한 한국어 표기
  (47 도도부현 표준 한국어 명칭 + `taiwan`→"타이완(해외)"). 48종 목록은 DB의
  `SELECT DISTINCT pref`와 일치해야 하며, 누락 슬러그는 원문 그대로 표시(KeyError 금지 — `.get(slug, slug)`).
- UI 전역에서 pref는 "한국어 라벨 (건수)" 형식으로 표시, 내부 값은 슬러그 유지.
- area2/area3는 이름 데이터가 없으므로(§10) v1.3에서는 "고급 필터" expander로 강등, 코드 그대로 표시.

### 9.2 다중 선택 (search 확장)
```
search(db, pref=None, area2=None, area3=None, genre=None, station=None,
       budget_dinner=None, sort="bayes", limit=30)
```
- `pref`, `genre`: str | list[str] | None 허용. 리스트면 IN 절(pref) / EXISTS OR(genre) —
  플레이스홀더 `?`를 리스트 길이만큼 동적 생성, 문자열 포매팅에 값 삽입 금지.
- 계단식 규칙 개정: area2/area3는 **pref가 정확히 1개일 때만** 지정 가능. 그 외 조합은 ValueError.
- `station`: str | None — stations_json에 대한 부분일치(LIKE, 파라미터 바인딩 `%...%`).

### 9.3 UI
- 지역: `st.popover("지역 선택")` 내부에 48종 한국어 라벨 체크박스 그리드(6열) — 클릭형 보드.
  (hover 트리거는 Streamlit 미지원 — 공식 위젯 한계로 클릭형 확정)
- 장르: `st.multiselect` (건수 상위순, 타이핑 검색은 위젯 내장 기능).
- 역 검색: `st.text_input("역 이름으로 찾기 (예: 銀座)")` → station 파라미터.
- 카드에 외부 링크 추가: "Google 지도에서 검색" —
  `https://www.google.com/maps/search/?api=1&query=` + URL 인코딩된 `f"{name} {첫 station}駅"`.
  (단순 링크아웃 — API·좌표 저장 아님, 기존 Google ToS 결론과 무관)

### 9.4 수용 테스트 (실측 확정값, tests/test_query.py 추가)
- search(pref=["tokyo","kanagawa"], genre="ラーメン", limit=20000) == **6008**
- search(pref="tokyo", genre=["ラーメン","つけ麺"], limit=20000) == **5724** (합집합·중복 없음)
- search(pref="kanagawa", genre="ラーメン", limit=20000) == **374**
- search(station="銀座", limit=20000) == **504** / search(station="新宿", ...) == **514**
- pref 2개 + area2 지정 → ValueError
- 기존 단일값 테스트(5634 등) 전부 하위호환으로 계속 green이어야 함 (str 입력 경로 유지)
- labels: PREF_LABELS 키 집합 == DB DISTINCT pref 48종 (테스트로 고정)

## 10. Phase 1.5 로드맵 (여행 후 — 앱 코드가 아닌 수집기 과제)
- **지역 이름**: 확장 v1.4.3 — collectChildLinks(parsers.js)가 현재 href만 수확하고
  a.textContent(지역·장르 표시명)를 버림(실측 확인). 노드 URL과 함께 라벨을 저장해
  {area_code → 표시명} 매핑 파일 산출 → labels.py에 area2/3 라벨 주입.
  이미 방문하는 페이지라 **추가 요청 0회**.
- **역명 현지화(ko/en)**: 라벨용 역명 1,142종(전체 2,771종) — 수작업 불가 규모이며 자동 음차는
  고유명사 불규칙 읽기(예: 日本橋 = 도쿄 にほんばし / 오사카 にっぽんばし) 때문에 금지.
  정식 경로: 駅データ.jp CSV(가나 읽기 포함)와 역명 매칭 → 가나→헵번 로마자(en),
  가나→한글은 국립국어원 일본어 가나 대조표(ko) — 둘 다 결정론 변환. 미매칭만 수동 검수.
- **핀 지도(임베디드)**: 데이터에 좌표·주소 필드 없음(실측 확정) → 상세페이지 보강 크롤 필요.
  착수 전 선결: 상세페이지 경로 robots 적합성 확인(신규 OI), 수집 범위(상위 N vs 전량) 결정.
  좌표 확보 후 st.map/pydeck으로 "지도 보기" 탭(상위 10~20 핀) 구현.


## 11. M6 — 다국어 표시 + 유도형 지역 라벨 (v1.4 신규)

### 11.1 원칙 (변경 금지)
- 데이터·DB·query.py의 정규 키(일본어 원문 장르, pref 슬러그, area 코드)는 **불변**.
  번역은 표시 계층(ui) 전용. 필터 파라미터로는 항상 원문 키를 전달한다.
- 번역은 런타임 생성 금지 — 사전 생성·검증된 정적 파일만 사용.

### 11.2 언어 토글
- 사이드바 최상단 `st.radio` 또는 selectbox: 한국어(기본) / 日本語 / English.
- `app/labels_i18n.py` (설계 세션에서 제공, 실데이터 203종 키 일치 검증 완료):
  `GENRE_LABELS[원문] = {"ko","en"}`. 일본어 모드는 원문 그대로.
  표시 헬퍼: `genre_label(g, lang)` — 미등록 키는 원문 폴백(KeyError 금지).
- pref: 기존 PREF_LABELS(ko)에 en 추가(도도부현 로마자 표기 — Tokyo, Osaka 등 48종),
  ja는 도도부현 일본어 표기(東京都 등). labels.py 확장.
- UI 크롬 문자열(필터/지역 선택/장르/정렬/예산/0건 안내/버튼 등)은
  `UI_TEXT[lang][key]` 사전으로 3개 언어 제공.

### 11.3 area2/3 유도형 라벨 (Phase 1.5 전까지의 잠정 표시)
- 각 area 코드의 라벨 = 해당 코드 레코드들의 **최빈 역 상위 2개**를 "코드 (역1·역2 일대)"로.
  예(실측): A1301 → "A1301 (銀座·新橋 일대)", A1307 → "A1307 (六本木·乃木坂 일대)".
- 계산은 DB에서 결정론적으로: 빈도 내림차순, 동률 시 역명 오름차순. `app/labels.py`에
  `area_label(db, pref, code, lang)` 헬퍼(집계는 st.cache_data 캐시 허용 — 입력 동일 시 출력 동일).
- "일대"의 언어별 표기: ko "일대" / ja "周辺" / en "area".

### 11.4 레이아웃 결함 수정
- 실기 확인: "고급 필터" expander가 비어 있고 area 셀렉트가 expander 밖에 렌더링됨.
  area2/area3 위젯을 expander **내부**로 이동(with 블록 스코프 확인).

### 11.5 수용 테스트
- GENRE_LABELS 키 집합 == DB DISTINCT genre (203종)
- genre_label("ラーメン","ko")=="라멘" / ("ラーメン","ja")=="ラーメン" / 미등록 키 원문 폴백
- PREF_LABELS ko/ja/en 각 48키 완전성
- area_label(real_db,"tokyo","A1301","ko")에 "銀座" 포함 (실측 최빈 역)


## 12. M7 — 지역 라벨 정리 + 지도 링크 확장 (v1.5 신규)

### 12.1 area 라벨에서 코드 제거
- 표시 형식을 "A1301 (銀座·新橋 일대)" → **"銀座·新橋 일대"**로 (ja "…周辺", en "… area").
- 코드는 내부 값으로만 유지(필터 파라미터·key). 역명 고유명사는 모든 언어에서 원문 유지
  (§10 현지화 경로 확보 전까지 — 오표기 방지 원칙).

### 12.2 카드 지도 링크 2종
- 기존 Google 링크 유지 + **Apple 지도 링크** 추가:
  `https://maps.apple.com/?q=` + quote(f"{name} {첫 station}駅") (Apple Map Links URL 스킴).

### 12.3 "상위 N곳 경로 보기" (Google Maps URLs API, 키 불필요)
- 결과 상단 버튼 + N 슬라이더(2~10, 기본 5). 상위 N의 (name + 첫 station + "駅")을
  경유지로: `https://www.google.com/maps/dir/?api=1&destination=<N번째>&waypoints=<1..N-1 파이프 구분>`
  &travelmode=walking. 전체 URL은 urllib.parse 인코딩(파이프 포함), 2,048자 초과 시 N 축소.
- 문서화된 제한을 UI 캡션에 명시: "모바일 브라우저에서는 경유지 3곳까지 표시될 수 있음".
- 이름 기반 매칭이므로 오매칭 가능 — 캡션에 "위치는 이름 검색 기반 근사" 문구.

### 12.4 수용 테스트
- URL 조립 함수는 순수 함수로 분리: N=5 고정 입력 → api=1 포함, waypoints 파이프 인코딩(%7C) 확인,
  총 길이 ≤2048 검증. 2048 초과 케이스(긴 이름 인위 입력) → N 자동 축소 동작.
- area_label 출력에 "A13" 등 코드 문자열 미포함 확인.


## 13. M8 — 역명 라벨 적용 + 역 좌표 핀 지도 (v1.7 전면 개정)

> v1.6의 Google 임베디드+클라이언트 지오코딩 설계는 **폐기** — Streamlit이 위젯 조작마다
> 스크립트를 재실행하므로 렌더당 지오코딩 반복 과금 구조가 됨(검토에서 확인).
> 개정판: 국토수치정보(N02) 좌표를 오프라인 1회 매칭 → API 호출·키 완전 제거.

### 13.1 역명 라벨 (`app/stations_i18n.py` — 설계 세션 제공, 내용 수정 금지)
- `STATION_LABELS[원문] = {"ko","en"}` 1,142건. `station_label(name, lang)`:
  ja→원문 / ko·en→매핑 / **미등록 키 원문 폴백**.
- 적용: area_label의 역 이름부, 카드 "역:" 목록. 내부 값·역 검색 파라미터는 원문 유지.

### 13.2 역 좌표 준비 (오프라인 1회, `scripts/prep_station_coords.py`)
- 입력: 국토수치정보 철도 데이터(N02) 최신판의 `N02-xx_Station.geojson`(UTF-8)
  — 사용자가 국토교통성 다운로드 서비스에서 수동 취득해 `data/geo/`에 배치.
- 처리: feature별 역명(N02_005)·지오메트리(플랫폼 LineString) → **중심점을 대표 좌표**로.
  그룹코드(N02_005g)로 동일역 병합(멀티 플랫폼 평균).
- 우리 역명 2,771종과 매칭:
  ① 전국 유일명 → 즉시 확정. ② 동명 복수 후보 → 2-패스: 해당 pref에서 ①로 확정된
  역들의 무게중심에 **최근접 후보** 선택(결정론: 거리 동률 시 좌표 사전순).
  ③ 미매칭 → 좌표 없음(핀 생략 대상)으로 기록.
- 출력: `data/station_coords.json` — {역명: {lat, lng, matched: exact|disambiguated}} + 매칭률 리포트.
- 출처 표기 상수 포함: "「国土数値情報（鉄道データ）」（国土交通省）を加工して作成" — 지도 캡션에 노출.

### 13.3 지도 렌더링 (키·API 호출 없음)
- 검색 결과 상위 N(슬라이더 5~30)을 `st.pydeck_chart`(Streamlit 내장 pydeck)로:
  각 식당 핀 = **첫 번째 역의 좌표**(동일 역 다수 식당은 지터 소량 부여), 툴팁 = 식당명·평점·역.
  기본 베이스맵(토큰 불요 스타일) 사용 — 토큰 요구 스타일 금지. pydeck 불가 시 st.map 폴백.
- 캡션 고정 문구(3개 언어): "핀은 최인접 역 기준 근사 위치" + N02 출처 표기 +
  "좌표 미확보 역의 식당 K곳 제외" 카운트.
- `data/station_coords.json` 부재 시 지도 섹션 미노출(fail-soft) — 기존 외부 링크는 항상 유지.

### 13.4 수용 테스트
- station_label: 1142키 / ko·en 정상 / 미등록 원문 폴백
- prep 스크립트: 매칭률 리포트 생성, "新宿" 좌표가 (35.6~35.8, 139.6~139.8) 범위(스팟체크),
  disambiguation 결정론(동일 입력 2회 실행 → 동일 출력 파일)
- 지도용 데이터 조립 함수 순수 함수화: 좌표 없는 역 제외 카운트 정확성, N 상한 강제
- pydeck 렌더 자체는 수동 확인. 테스트에서 네트워크 금지


## 14. M9 — 다중 리뷰어: 식당 단위 집계 (v2.0, 시맨틱 변경)

### 14.1 입력·적재 확장
- 입력: `data/reviewers/` 내 모든 `.json` (기존 maro merged 포함, 사용자가 배치). 파일별로
  `{meta, records[]}` 및 **22필드 스키마 완전 일치를 검증 — 불일치 파일 발견 시 즉시 정지·보고**
  (필드 추가/누락/타입 상이 모두 정지 사유. 새 리뷰어 파일이 다른 내보내기 형식일 가능성 있음).
- 전 파일 union 후 (reviewer_id, restaurant_id) 유일성 검증. restaurants 테이블은 기존 그대로(레코드 단위).

### 14.2 식당 단위 집계 테이블 `restaurants_agg` (적재 시 생성)
- 키: restaurant_id (1행 = 1식당).
- 식당 속성(name, url, pref/area2/area3, tabelog_rating, review_count, budget*, stations, awards):
  리뷰어 간 상이할 수 있음 → **visited_month 최신 레코드 값 채택**(동률 시 reviewer_id 오름차순). 
  상이 발생 건수를 적재 리포트에 출력(이상 감지용).
- 집계 컬럼: reviewer_count, reviewers_json(표시용), visit_count_total(합),
  reviewer_rating_mean(비null 평균, 전부 null이면 null), last_visited(max).
- **bayes_score, C, m: restaurants_agg(중복 제거된 식당 집합) 기준으로 재계산** — 레코드 기준 금지.
- search()는 이제 restaurants_agg를 읽는다(카드 1장 = 식당 1곳). 정렬 `reviewer` = reviewer_rating_mean.

### 14.3 수용 상수 재확정 프로토콜 (측정 먼저)
- `scripts/measure_constants.py`: 적재 후 다음을 산출·출력 —
  총 레코드/총 식당/리뷰어 목록·파일별 건수/중복 식당 수/pref·genre distinct/C·m(신규 기준)/
  tokyo×ラーメン 식당 수·bayes top1/nagano·okinawa 셀/budget 17종 유지 여부/속성 상이 건수.
- 측정값을 **완료 보고에 표로 제시한 뒤** 그 값으로 §3·§4 계열 테스트 기준을 갱신·고정.
  기존 단일 리뷰어 상수(14281 등)는 "records 테이블 검증"으로 유지, 셀·top1 계열은 agg 기준으로 이관.
- 이상 징후(스키마 불일치·중복 식당의 속성 상이 폭증·top1 급변) 시 정지·보고.

### 14.4 표시·생성
- 카드: "리뷰어 K명 · 총 N회 방문 (최근 YYYY/MM)" + reviewer_rating_mean(존재 시).
- 추천문 생성 입력에 리뷰어별 (표시명, reviewer_rating, visit_count) 목록 포함 —
  프롬프트 지시에 "복수 리뷰어의 평가를 종합하되 사실 외 창작 금지" 추가.

## 15. M10 — 페이지네이션 + 지도 상호작용 (v2.0)

### 15.1 페이지네이션
- search(..., offset=0) 추가 + count 전용 쿼리. UI: 페이지당 30, "더 보기" 또는 페이지 선택.
  총 건수 표기("전체 5,634곳 중 1–30").

### 15.2 지도 상호작용 (공식 지원 기능만 사용)
- 핀 클릭: `st.pydeck_chart(..., on_select="rerun", selection_mode="single-object")`,
  레이어에 `id` 필수(문서 요구). 선택 객체를 지도 하단 패널에 표시 — 식당명·평점·
  타베로그 링크·Google/Apple 링크 (툴팁 내 클릭 링크는 미지원이므로 패널 방식 확정).
- 카드→지도 포커스: 카드에 "지도에서 보기" 버튼 → st.session_state["map_focus"]=(lat,lng) →
  ViewState(zoom≈15)로 재렌더 + 해당 핀 강조색. (선택 상태의 프로그래밍 설정은 불가 — 문서 확인)
- 동적 뷰포트: map_focus 없으면 **현재 결과 핀들의 평균 좌표·적정 zoom으로 항상 재계산** —
  지역/필터 변경 시 지도가 자동 추종.

## 16. M11 — 배포 (Streamlit Community Cloud, 여행용)

### 16.1 구성 (근거: Streamlit 공식 문서 — 프라이빗 저장소 앱은 기본 비공개, viewer 이메일 초대)
- GitHub **프라이빗** 저장소 push(데이터 포함 — C-1 유지). Community Cloud에서 배포,
  공유 설정은 비공개 유지 + 본인(및 동행자) 이메일만 viewer 초대.
- `requirements.txt`: streamlit, pydeck **만**. torch/transformers 절대 포함 금지
  (클라우드 메모리 상한 ~1GB 문서화 — Qwen 3.1GB 불가. generate.py 지연 임포트 덕에
  클라우드에서는 자동으로 템플릿 폴백 동작 = fail-soft 검증 지점).
- app.db·station_coords.json은 빌드 시 생성 대신 저장소에 포함(단순성 우선. 12MB급 — Git 허용 범위).
- 시작 명령·경로: 클라우드는 저장소 루트에서 실행 — ui.py의 sys.path 부트스트랩과
  DB 상대경로가 루트 기준으로 동작함을 로컬에서 `python -m streamlit run app/ui.py`로 재확인.
- 모바일: Streamlit 기본 반응형(사이드바는 햄버거 메뉴). set_page_config(initial_sidebar_state="expanded" 유지).
- 앱스토어 등록은 범위 밖(네이티브 래퍼 별개 과제). 폰 브라우저 "홈 화면에 추가" 안내로 갈음.
