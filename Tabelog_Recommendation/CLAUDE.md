# CLAUDE.md — Tabelog 추천 앱 (Phase 1)

## 프로젝트 개요
Tabelog 고신뢰 리뷰어의 방문 식당 데이터(사전 수집 완료, JSON 1개)를
지역×장르로 필터·랭킹하고, 구조화 사실만으로 LLM 추천문을 생성하는 앱.
수업 내 비공개 프로젝트. 크롤링은 이 저장소의 범위 밖(이미 완료됨).

## 절대 규칙
1. **추측 금지.** 스펙(`PHASE1_SPEC.md`)에 없는 결정이 필요하면 임의로 정하지 말고 질문할 것.
   스펙의 수치(레코드 수, 상수, 수용 기준)는 실데이터에서 검증된 값이므로 변경 금지.
2. **C-1**: 수집 데이터·산출물은 비공개 분석용. 외부 전송/업로드 코드 작성 금지.
3. **C-2**: 리뷰 원문을 UI에 노출하지 않는다. (현 데이터에 리뷰 본문 자체가 없음 — 추가하지도 말 것.)
4. **Tabelog에 대한 어떤 네트워크 요청도 금지.** 이 앱은 로컬 JSON만 읽는다.
5. 각 마일스톤은 수용 테스트(pytest)가 전부 통과해야 완료로 간주.
6. **(FT)** 학습 입력 포맷 = `app/generate.py`의 `build_messages()` 출력과 바이트 단위 동일. 별도 포맷 창조 금지 — 반드시 import해서 재사용.
7. **(FT)** 타베로그 리뷰 원문을 어떤 형태로도 학습 데이터에 넣지 않는다 (구조화 사실만).
8. **(FT)** 교사 출력은 충실성 필터 통과분만 채택. 필터 기준 완화 금지.
9. **(FT)** 파인튜닝 산출물(데이터셋·체크포인트) 전부 비공개(C-1 연장 적용).

## 입력 데이터 (읽기 전용)
- `data/tabelog_maro_merged_20260706.json` — `{meta, records[]}` 구조, 14,281 레코드.
- 레코드 스키마와 필드 충전율은 `PHASE1_SPEC.md` §2 참조. 이 파일을 수정하지 말 것.

## 환경·컨벤션
- Windows / conda env `llmft` (Python 3.11). 패키지 설치는 반드시 `python -m pip install ...`.
- 셸은 Git Bash(MINGW64): Windows식 슬래시 플래그가 깨짐 (`/F` → `//F`).
- DB는 SQLite 단일 파일 `app.db` (표준 라이브러리 `sqlite3` 사용, ORM 불필요).
- UI는 Streamlit. 웹 프레임워크(FastAPI 등) 추가 금지 — 이번 범위 아님.
- 테스트는 pytest. 배포 코드와 테스트가 동일 모듈을 import (드리프트 금지).

## 오류 처리·코드 고정 지침 (전 마일스톤 공통)
- **모든 `open()`에 `encoding="utf-8"` 명시.** Windows 기본 인코딩(cp949)에서 일본어 JSON이 깨진다. 예외 없음.
- 경로는 전부 `pathlib.Path`. 문자열 연결로 경로 조립 금지.
- **fail-fast**: 입력 검증 실패 시 명확한 메시지로 즉시 중단. 부분 산출물(반쯤 적재된 DB 등)을 남기지 않는다 — 적재는 단일 트랜잭션.
- `except:`/`except Exception:` 포괄 캐치 금지. 구체 예외만 잡고, 잡을 이유가 없으면 전파.
- SQL은 파라미터 바인딩(`?`)만. f-string/`%` 포매팅으로 쿼리 조립 금지.
- 네트워크 호출 전면 금지. 유일한 예외: transformers의 HF Hub 모델 최초 다운로드(기본 모델 사용 시 1회). 테스트에서는 모델 로드·네트워크 모두 mock.
- 결정론 유지: 랜덤·현재시각 의존 로직 금지(LLM 생성 출력 제외). 같은 입력 → 같은 출력.
- 스펙의 수치·수용 기준을 코드에 맞추지 말 것. 테스트가 실패하면 **코드가 틀린 것**이다. 기준값 수정이 필요해 보이면 중단하고 사용자에게 보고.

## 저장소 구조 (생성할 것)
```
app/
  load.py        # M1: JSON → SQLite 적재 + 검증
  ranking.py     # M2: 랭킹 함수 (순수 함수, DB 비의존 부분 분리)
  query.py       # M2: 필터·정렬 쿼리
  generate.py    # M4: LLM 추천문 생성 (구조화 사실 → 텍스트)
  ui.py          # M3: Streamlit 앱
data/            # 입력 JSON (사용자가 배치)
tests/
  test_load.py
  test_ranking.py
  test_query.py
```

## 마일스톤 (순서 고정, 각각 테스트 통과 후 다음으로)
- **M1** 적재: `python -m app.load data/tabelog_maro_merged_20260706.json app.db`
- **M2** 랭킹·필터: 순수 함수 + SQL
- **M3** UI: Streamlit (`streamlit run app/ui.py`)
- **M4** 추천문 생성: 로컬 Qwen2.5-1.5B-Instruct (QWEN_MODEL_PATH로 파인튜닝 체크포인트 교체 가능) / 로드 실패 시 템플릿 폴백

상세 스펙·DDL·수용 기준은 전부 `PHASE1_SPEC.md`에 있음. 거기 적힌 대로만 구현할 것.
