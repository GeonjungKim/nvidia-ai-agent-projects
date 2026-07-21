# PROMPTS.md — Claude Code (Sonnet) 세션 프롬프트 세트

운영 원칙: **한 세션 = 한 마일스톤.** 마일스톤 완료(테스트 green) 후 새 세션으로 넘어가면
컨텍스트 오염 없이 각 세션이 스펙 문서를 신선하게 읽는다.
아래 프롬프트를 순서대로 복사-붙여넣기. `[꼬리표]`는 모든 프롬프트 마지막에 항상 포함.

---

## [꼬리표] — 모든 프롬프트 공통 (복사해서 항상 끝에 붙일 것)

```
공통 규칙:
- 구현 전에 CLAUDE.md와 PHASE1_SPEC.md를 먼저 읽고, 무엇을 만들지 계획을 3~7줄로 출력한 뒤 시작해.
- 스펙에 없는 결정이 필요하면 구현하지 말고 멈춰서 질문해. 임의로 정하지 마.
- 스펙의 수치·수용 기준은 실데이터 검증값이다. 절대 수정 금지. 테스트 실패 = 코드 결함.
- 신규 설치 허용은 {streamlit, pytest}뿐(python -m pip). torch/transformers는 llmft 기존 설치분 사용 — 없으면 설치 말고 멈추고 보고.
- 완료 보고 형식: (1) pytest 전체 실행 결과 원문 (2) 스펙 대비 구현 diff 요약 (3) 스펙에서 벗어난 점 0건임을 명시적으로 확인.
```

---

## 세션 0 — 킥오프 (프로젝트 골격)

```
이 저장소의 CLAUDE.md와 PHASE1_SPEC.md를 정독해.
그 다음 아무 구현 없이 다음만 수행해:
1. CLAUDE.md의 '저장소 구조'대로 빈 패키지 골격 생성 (app/, tests/, 빈 __init__.py 포함)
2. data/tabelog_maro_merged_20260706.json 존재 확인. 없으면 멈추고 알려줘.
3. python -m pip install streamlit pytest 실행 후, python -c "import torch, transformers; print(torch.__version__, transformers.__version__, torch.cuda.is_available())" 결과 출력. CUDA False면 멈추고 보고.
4. 네가 이해한 마일스톤 M1~M4의 완료 기준을 각 1줄로 요약해서 출력해.
   내 이해와 다르면 여기서 바로잡을 거야.
[꼬리표]
```

## 세션 1 — M1: 적재

```
PHASE1_SPEC.md §3(M1)만 구현해. 범위: app/load.py + tests/test_load.py.

순서:
1. tests/test_load.py를 먼저 작성 — §3 수용 테스트 7개 항목을 그대로 pytest로 옮겨.
   기준값(14281, 48, 94, 203, 3879, C∈[3.48,3.50], m==243, budget 17종)은 스펙 §3 그대로.
2. app/load.py 구현. 진입점: python -m app.load data/tabelog_maro_merged_20260706.json app.db
3. 실행 → pytest tests/test_load.py -v 전체 통과까지.

주의(스펙에 이미 있지만 재강조):
- open(..., encoding="utf-8") 필수. C와 m은 rating 비null 집합에서 런타임 계산.
- 단일 트랜잭션, 재실행 멱등(DROP 후 재생성).
- restaurant_genres는 INSERT OR IGNORE.
M2 이후 범위(query.py, ui.py 등)는 절대 건드리지 마.
[꼬리표]
```

## 세션 2 — M2: 랭킹·필터

```
PHASE1_SPEC.md §4(M2)만 구현해. 범위: app/ranking.py, app/query.py + tests/test_ranking.py, tests/test_query.py.
전제: app.db가 M1으로 이미 생성돼 있음 (없으면 M1 커맨드로 생성부터).

순서:
1. tests 두 파일 먼저 작성 — §4 수용 테스트를 그대로:
   bayes(2106,4.07,243,3.489346)≈4.010±0.005 / bayes(1,5.0,...)<3.51 /
   tokyo×ラーメン 5634건(전체 기준, rating null 15건 포함)·1위 らぁ麺や 嶋 / nagano×ラーメン 100건 / okinawa×フレンチ [] /
   budget 필터 버킷 일치 / 계단식 위반 ValueError.
2. ranking.py: bayes(v,R,m,C) 순수 함수. m·C는 DB meta 테이블에서 읽는 헬퍼 별도 제공.
3. query.py: search(db, pref, area2, area3, genre, sort, limit) — §4 시그니처·정렬 옵션 4종 그대로.
   NULL 정렬은 포터블 형식 (bayes_score IS NULL) ASC, ... 사용.
4. pytest 전체(test_load 포함) 통과 확인.

genre 단일 선택 / budget_dinner 문자열 완전 일치 필터 / 지역 계단식 검증(위반 시 ValueError)까지 구현.
UI는 이 세션 범위 아님.
[꼬리표]
```

## 세션 3 — M3: Streamlit UI

```
PHASE1_SPEC.md §5(M3)만 구현해. 범위: app/ui.py.
전제: M1·M2 완료, pytest 전체 green.

요구:
1. streamlit run app/ui.py 로 구동. DB 경로 기본 app.db.
2. 사이드바: pref(건수 병기, 데이터에서 동적 로드) → area2 → area3 계단식,
   genre 셀렉트(선택 지역 내 건수 상위순), 예산(저녁) 셀렉트(floor 오름차순, 결측 제외 안내), 정렬 라디오(bayes 기본).
3. 결과 카드: §5 명시 필드만. review_url 등 내부 필드 노출 금지(C-2).
4. 0건 처리: 안내 문구 + 상위 지역 완화 제안.
5. "추천문 생성" 버튼은 자리만 만들고 "M4에서 활성화" 표기 (generate.py 호출 스텁).

완료 보고에 추가로: 수동 점검 체크리스트를 네가 만들어서 출력해
(예: tokyo→ラーメン 정렬 비교, okinawa→フレンチ 0건 문구, 희소 셀 nagano→ラーメン).
실제 화면 확인은 내가 한다.
[꼬리표]
```

## 세션 4 — M4: 추천문 생성 (로컬 Qwen)

```
PHASE1_SPEC.md §6(M4)만 구현해. 범위: app/generate.py + 테스트 + ui.py 버튼 연결.

요구:
1. load_model(): 경로 = os.environ.get("QWEN_MODEL_PATH", "Qwen/Qwen2.5-1.5B-Instruct").
   AutoModelForCausalLM.from_pretrained(path, torch_dtype="auto", device_map="cuda") + AutoTokenizer.
   로드 실패(OOM/CUDA 불가 포함) 시 예외를 삼키지 말고 폴백 경로로 분기 + 경고 문자열 포함.
2. generate(records, model=None, tokenizer=None) -> str
   - 프롬프트 조립은 별도 순수 함수 build_messages(records)로 분리 (system=사실 창작 금지 지시, user=사실 JSON).
   - tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True) 사용.
     특수토큰 문자열을 수동으로 조립하지 마.
   - 1차: max_new_tokens=512, do_sample=False. 출력에 입력에 없는 식당명 있으면
     1회 재시도(do_sample=True, temperature=0.7) → 재실패 시 템플릿 폴백.
   - 템플릿 폴백: f-string 사실 나열식 (모델 전무 상태에서도 데모 완주).
3. ui.py: @st.cache_resource로 load_model 1회 캐시, 버튼 연결.
   모델 미로드 상태에서도 버튼이 폴백으로 동작해야 함.
4. 테스트: 폴백(고정 3건 → 3개 식당명 포함) + build_messages 구조 단위 테스트 자동화.
   load_model·model.generate는 mock — 테스트에서 실제 모델 로드·GPU 사용·네트워크 금지.
5. pytest 전체 green + 실행 확인 커맨드 출력:
   QWEN_MODEL_PATH 미설정(기본 모델)과 설정(체크포인트 디렉토리) 두 경우의 streamlit 기동 커맨드.
[꼬리표]
```

## 부록 A — 테스트 실패 시 디버깅 프롬프트 (필요할 때만)

```
pytest 실패 로그: [로그 붙여넣기]
규칙:
1. 추측으로 고치지 마. 먼저 실패를 최소 재현하는 코드/쿼리를 실행해서 실제 원인을 특정해.
2. 원인 특정 전까지 수정 금지. 특정 후 '원인 → 최소 수정' 형식으로 보고하고 그 수정만 적용해.
3. 수용 기준값을 바꾸는 방식의 '수정'은 금지. 기준값이 틀렸다고 판단되면 근거를 제시하고 멈춰.
[꼬리표]
```

## 부록 B — 최종 점검 프롬프트 (수요일 오전, M4 후)

```
전체 최종 점검:
1. pytest -v 전체 실행 결과 원문 출력.
2. PHASE1_SPEC.md의 §3~§6 수용 기준을 표로 만들고 각 항목 옆에 통과 여부 표기.
3. CLAUDE.md 고정 지침 위반 여부 자체 감사: open() 인코딩, bare except, SQL 포매팅,
   테스트 내 네트워크 호출, 허용 외 의존성 — 각각 grep 근거와 함께 0건 확인.
4. 데모 시나리오 실행 순서 요약 (tokyo×ラーメン 정렬 비교 → 예산 필터 → okinawa×フレンチ 0건 → 추천문 생성).
[꼬리표]
```
