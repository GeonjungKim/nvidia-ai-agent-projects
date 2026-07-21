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
- 두 키 모두 **하드코딩 금지** — `tabetabi/config.py`가 `.env`에서만 로드합니다. `.env`는 절대 커밋하지 마세요.

## 그 외 저장 파일 (가점 항목)

- **DB 저장**: `sessions.db` (SQLite, 이 폴더에 실행 시 자동 생성) — 대화·계약·생성된 일정을 세션별로 저장합니다.
  읽기 전용 타베로그 DB(`app.db`)와는 별개이며, 코드는 절대 `app.db`에 쓰지 않습니다.
- **소셜 로그인(Google)**: 선택 사항, `.streamlit/secrets.toml` 설정 필요 — 절차는 `LOGIN_SETUP.md` 참고.
  설정 안 해도 앱은 정상 동작합니다 (로그인 UI만 숨겨짐, 대화는 브라우저 탭에 묶여 저장됨).
