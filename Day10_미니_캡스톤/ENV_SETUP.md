# 환경변수 설정 (.env)

`Day10_미니_캡스톤` 폴더에 `.env` 파일을 직접 만들고 아래 내용을 넣으세요.
(guard 훅이 `.env` 자동 생성을 막으므로 — Day8에서 만든 그 훅! — 직접 생성해야 합니다)

```
TAVILY_API_KEY=tvly-여기에_발급받은_키
```

- NVIDIA 키는 `../API.txt`(NV_API_KEY)에서 **자동 로드**되므로 넣지 않아도 됩니다.
- `TAVILY_API_KEY`가 없으면 @scout이 검색 링크 폴백 모드로 동작합니다 (전체 파이프라인은 정상).
- Tavily 키 발급: https://tavily.com 무료 가입 (카드 불필요, 월 1,000회)
