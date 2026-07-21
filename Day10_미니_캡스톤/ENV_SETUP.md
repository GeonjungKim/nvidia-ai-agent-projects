# 환경변수 설정 (.env)

`Day10_미니_캡스톤` 폴더에 `.env` 파일을 직접 만들고 아래 내용을 넣으세요.
(guard 훅이 `.env` 자동 생성을 막으므로 — Day8에서 만든 그 훅! — 직접 생성해야 합니다)

```
NVIDIA_API_KEY=nvapi-여기에_발급받은_키
TAVILY_API_KEY=tvly-여기에_발급받은_키
```

- `NVIDIA_API_KEY`가 없으면 `../API.txt`(NV_API_KEY)에서 폴백 로드를 시도합니다 (둘 다 없으면 실행 시 즉시 에러).
- `TAVILY_API_KEY`가 없으면 @scout이 검색 링크 폴백 모드로 동작하고, 고정 식당의 웹검색 매칭(resolve 2단)도 건너뜁니다 (전체 파이프라인은 정상).
- Tavily 키 발급: https://tavily.com 무료 가입 (카드 불필요, 월 1,000회)
- (선택) `GOOGLE_MAPS_API_KEY=...` — 설정 시 DB 미등록 고정 장소를 Google Places로 확인해
  정식 명칭·주소·**정확한 지도 핀 링크**를 제공합니다. 없으면 기존 지도 검색 링크로 폴백.
  발급: https://console.cloud.google.com → "Places API (New)" 활성화 (월 무료 쿼터 내 소규모 사용 가능, 결과는 메모리 캐시로 반복 과금 방지)

## 보조 LLM 제공자 (선택 — NIM 장애 대비 이원화)

NVIDIA NIM 무료 티어는 간헐적으로 502/타임아웃이 발생합니다. OpenAI 호환 엔드포인트를
보조로 등록하면, 기본 모델이 장애일 때 **자동으로 폴백**합니다 (코드 무변경, `.env`만):

```
FALLBACK_BASE_URL=https://<openai호환 엔드포인트>/v1
FALLBACK_API_KEY=<키>
FALLBACK_MODEL=openai/gpt-5-mini      # 미지정 시 base_url 있으면 이 값이 기본
```

- 폴백 순서: 기본 모델(NIM qwen) → `FALLBACK_MODEL` → NIM llama-3.3-70b.
- **gpt-5 계열 자동 처리**: `temperature` 제거·`max_completion_tokens` 변환·`reasoning_effort=minimal`을
  코드가 알아서 적용합니다. OpenAI 계열이라 **병렬 tool call도 지원**(NIM llama 폴백이 막혔던 지점 해결).
- 실측: gpt-5-mini는 tool 루프·병합 모두 ~5초로, 과부하 시 NIM qwen(수십 초)보다 오히려 빠름.
- `LLM_FALLBACK_MODELS`(콤마 구분)로 폴백 체인을 직접 지정할 수도 있습니다.
- 두 키 모두 **하드코딩 금지** — `tabetabi/config.py`가 `.env`에서만 로드합니다. `.env`는 절대 커밋하지 마세요.

## 그 외 저장 파일 (가점 항목)

- **DB 저장**: `sessions.db` (SQLite, 이 폴더에 실행 시 자동 생성) — 대화·계약·생성된 일정을 세션별로 저장합니다.
  읽기 전용 타베로그 DB(`app.db`)와는 별개이며, 코드는 절대 `app.db`에 쓰지 않습니다.
- **소셜 로그인(Google)**: 선택 사항, `.streamlit/secrets.toml` 설정 필요 — 절차는 `LOGIN_SETUP.md` 참고.
  설정 안 해도 앱은 정상 동작합니다 (로그인 UI만 숨겨짐, 대화는 브라우저 탭에 묶여 저장됨).
