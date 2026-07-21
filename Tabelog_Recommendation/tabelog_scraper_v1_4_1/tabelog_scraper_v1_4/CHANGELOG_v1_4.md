# CHANGELOG v1.4 (2026-07-03)

근거 자료: 사용자 제공 실측 ①~⑤ (`tabelog_claude_요청.txt`, pal=tokyo 페이지 전체 HTML 포함).
모든 변경은 이 실측을 픽스처로 한 테스트로 검증됨 (**로직 34 + DOM 33 = 67/67 통과**).

## 0. v1.3 재검증 (변경의 출발점)

배포 v1.3 파서를 실측 전체 페이지에 직접 실행 → **24/25 통과, 유일 실패 = awards**.

| 항목 | v1.3 결과 |
|---|---|
| 총 건수 9399 / 오류페이지 아님 / rel=next→PG=2 | ✅ |
| 카드 20건(mode card), 종합점·개인점 전수·범위, rvwdtl 링크 | ✅ |
| 자식 30개(LstPrf A1301~A1330), pal 보존, 오염 0 | ✅ |
| ① 단독 카드 전 필드 (4.06/5.0, 예산, 방문, B490866169 등) | ✅ |
| **awards: 파서 35 vs 실측 36** | ❌ |

## 1. 신발견 — 수상 뱃지 마크업 확정 (이전 세션 주장 정정)

이전 세션의 "이 페이지엔 수상 뱃지 없음" 주장은 **오류**였음. 실측 페이지의 카드 내
`.simple-rvw__rst-name` 안에 뱃지 div가 실재:

```html
<div class="simple-rvw__award-badge rvwr-award-badge">
  <span class="c-badge-award c-badge-award--square c-badge-award--2026gold"><i>2026年Gold受賞店</i></span>
  <div class="rvwr-award-badge__tooltip-wrap">…<p>The Tabelog Award 2026 Gold 受賞店</p>…</div>
</div>
```

실측 3종 (20카드 중 18카드, 뱃지 총 36개, 최대 3개/카드 = よろにく):

| 종류 | 수식어 클래스 | 실측 수 | 라벨 예 |
|---|---|---|---|
| The Tabelog Award | `c-badge-award--{YYYY}{gold\|silver\|bronze}` | 18 (gold7·silver5·bronze6) | 2026年Gold受賞店 |
| 百名店 | `c-badge-hyakumeiten--{YYYY}{category}` | 17 (sushi4·japanese3·creative_innovative3·french2·sukiyaki_shabushabu2·yakitori1·yakiniku1·spanish1) | 寿司 TOKYO 百名店 2025 選出店 |
| ホットレストラン | `c-badge-hot-restaurant--{YYYY}` | 1 | 食べログ ホットレストラン 2026 受賞店 |

v1.3 텍스트 정규식의 결함(실측으로 확인):
- `hot-restaurant` 유형 **전량 누락** (35 vs 36의 원인)
- 메달은 가시 텍스트 `2026年Gold受賞店`에 불일치, **툴팁 문구에 우연히 매칭**되어 살아있었음
- 百名店의 **카테고리 정보 소실** (`"百名店2025"`만 저장)

## 2. parsers.js

- **`parseAwards(card)` 신설** — 구조 셀렉터(`.simple-rvw__award-badge [class*='c-badge']`)로
  수식어 클래스에서 연도·등급/카테고리를 기계판독. 미지 뱃지는 `type:"unknown"`으로 보존(스키마 방어).
  구조 뱃지 0개일 때만 v1.3 텍스트 정규식을 안전망으로 실행(`type:"text_fallback"`, 이중계상 방지).
- **awards 스키마 변경: `string[]` → `object[]`** (Phase 1 DB 적재 착수 전이 변경 적기)
  ```json
  { "type": "tabelog_award", "year": 2026, "rank": "gold",  "label": "2026年Gold受賞店" }
  { "type": "hyakumeiten",  "year": 2025, "category": "sushi", "label": "寿司 TOKYO 百名店 2025 選出店" }
  { "type": "hot_restaurant", "year": 2026, "label": "食べログ ホットレストラン 2026 受賞店" }
  ```
  주: 百名店 라벨의 지역 수식(TOKYO/EAST 등)은 클래스에 없어 label에만 보존됨.
- **`collectChildLinksDetailed` / `harvestChildFilterLinksDetailed` 신설** — `{url, text, value}` 반환
  (감사 리포트의 지역명 라벨용). 판정 규칙은 기존과 동일하며 문자열 API는 상세 버전의 사상(map)으로
  재구성되어 **단일 정의** 유지. 기존 호출부(content.js) 무변경.

## 3. content.js

- **버그 수정: 백오프 한계 경로의 리뷰어 큐 건너뜀** — 마지막 노드에서 반복 실패 시
  `reviewerQueue`를 확인하지 않고 종료하던 결함. 다음 목적지 선택을 `popNext(store)`로 추출해
  정상 경로와 실패 경로가 동일 로직을 공유.
- **커버리지 감사 모듈 신설(파일럿 도구)** — 팝업에서 `{cmd:"tblg_audit"}` 수신 시
  `runCoverageAudit()` 실행:
  - 현재 DOM에서 부모 건수 + 자식 한 단계(상세) 수확 → 자식 최대 40개를 **same-origin fetch +
    DOMParser**로 순차 처리. 파싱은 배포 `TBLG_P` 그대로(테스트=배포 원칙).
  - 레이트리밋은 크롤과 동일: 매 요청 전 `randDelay()`(5~8초), 오류 시 30초 1회 재시도.
  - 산출: 자식별 `{label, value, count, cards, mode, badges, hasNext, nulls, http, error}`,
    `sums.{child_sum, delta, delta_pct}`, 셀렉터 건강 플래그, **뱃지 변형 클래스 인벤토리**
    → JSON 자동 다운로드(`tabelog_audit_{slug}_{key}_{ts}.json`) + console.table.
  - **읽기 전용**: 크롤 상태(storage)를 일절 변경하지 않음. 크롤 중 실행 차단, 중복 실행 가드,
    우하단 HUD로 진행 표시.

## 4. popup.js / popup.html / manifest.json

- **시작 노드 URL(선택)** — 입력 시 해당 URL을 `normalizeUrl`로 정규화해 그 노드를 루트로
  **서브트리만 순회**(파일럿·부분 재수집). 엄격 자식 규칙이 현재 노드의 의미 파라미터를 전부
  보존하므로 서브트리 격리는 규칙의 따름정리(로직 테스트 L6에서 합성 패널로 검증).
- **커버리지 감사 버튼** — 현재 탭 content script에 메시지 전송.
- 시작 시 기존 레코드가 있으면 **confirm** 경고(무단 초기화 방지).
- `rootUrlFor` 중복 제거 → `TBLG_P.buildRootUrl` 단일 정의 사용(popup.html이 parsers.js 로드).
- export meta·헤더 버전을 `chrome.runtime.getManifest().version`으로 동적화. manifest **1.4.0**.

## 5. 테스트 (재구축)

v1.3의 테스트 파일이 프로젝트 지식에 없어 실측 픽스처 기반으로 재구축:

| 파일 | 수 | 내용 |
|---|---|---|
| `test_logic_v14.mjs` | 34 | URL 유틸 멱등성·캡, depth, **엄격 자식 규칙 합성 패널 10케이스**, parseAwards 단위·폴백·이중계상 방지 |
| `test_dom_v14.mjs` | 33 | 실측 페이지: v1.3 회귀 전 항목 + **뱃지 36개 전수 대조**(유형·연도·등급·카테고리 분포), 상세 자식 30개 라벨, 장르 1단계 Cat 6종 |

실행: `npm install jsdom` 후 `node test_logic_v14.mjs && node test_dom_v14.mjs`

## v1.4.1 (2026-07-04) — 감사 fetch 경로 가드 (첫 실전 구동 피드백 반영)

실전 첫 구동(사용자 콘솔 실측)에서 감사의 모든 자식 fetch가 실패:
`tabelog.com/rvwr/…` 요청이 **`s.tabelog.com/smartphone/reviewer/…`로 302** →
교차 출처 리다이렉트에 ACAO 헤더 부재 → CORS 차단(`Failed to fetch`).
같은 세션에서 문서 내비게이션은 데스크톱 페이지를 정상 수신(자식 30개 수확·건수 9399 파싱 성공).
리다이렉트 대상에 `my_site_uri`가 부가된 점에서 SP 라우팅은 Tabelog 앱 로직으로 판단(확정).
**원인은 미확정** — 유력 가설: 탭의 모바일 UA(DevTools 기기 에뮬레이션)로 인한 기기 라우팅.

가드(원인 무관하게 동작):
1. **모바일 UA 사전 차단** — `navigator.userAgent`/`userAgentData.mobile` 검사, 감지 시 시작 전 중단·안내
2. **프로브 fetch** — 자식 루프 전에 '방금 내비게이션으로 성공한 부모 URL'을 fetch로 재요청해
   경로 동등성 확인. 실패 시 30회 낭비 없이 즉시 중단 + 원인 후보 안내(TypeError=차단 분류)
3. **fetchDoc 강화** — `redirect:"follow"` 명시, 최종 URL 호스트 검증(동일 출처 이탈 시 명시 오류
   `오프사이트 리다이렉트`), `Accept: text/html` 부여, `redirected/finalUrl` 반환
4. **자식 루프** — 예외도 30초 1회 재시도(단, 오프사이트는 구조적 실패로 즉시 기록),
   리포트 행에 `redirected`/`final_url` 보존

## v1.4.2 (2026-07-04) — 부모 3중 측정 (파일럿 단계 A 결과 반영)

단계 A(도쿄 커버리지 감사) 실측에서 서로 다른 부모 건수 3개 관측:
라이브 DOM(베어 URL 내비게이션) **9399** / 정규화 URL fetch **9465** / Σ자식(정규화) **9431**.
⑤(07-02)에선 베어=장식풀세트=9399로 일치했으므로, 오늘의 +66이 파라미터 효과인지
DOM(캐시) 스테일인지 미확정. v1.4.1 리포트는 Δ를 DOM 기준으로 계산해 교차 우주 비교(-32)가
됐음 → 수정:

- **parent 3중 측정**: `count_dom`(라이브 DOM) / `count_fetch`(정규화 프로브, 자식과 동일 조건) /
  `count_fetch_bare`(베어 프로브 +1요청) + `param_delta` 자동 기록
- **sums.delta를 count_fetch 기준으로 재정의**(동일 우주 비교), `delta_vs_dom`은 참고용으로 보존
- **`parent.unlinked_children`**: 패널의 링크 없는(nolink) 항목 텍스트 수집 —
  링크 수확으로 도달 불가한 영역(예: 伊豆諸島・小笠原)의 존재를 리포트가 증거로 남김
- 완료 alert에 3중 측정치·nolink 항목 표기

### v1.4.2b 추가 (2026-07-04, 전국 크롤 14,062건 실측 반영)

- **pal=atw 후순위화**: atw는 root와 동일 건수(14,389)인 전집합 노드로 실측 확정.
  단 패널 미노출 지층 구조 실증(kochi 1·saga 4건이 pal 링크 부재에도 atw 상위 1200에서 수집)
  → 제외 대신 스택 바닥으로 강등(리프 우선 방문). atw발 신규 레코드 수 = 미도달 지층 측정치.
- **증분 병합 재크롤 모드**(popup 체크박스): records/losses/expected/failures 보존,
  seen/stack만 초기화. mergeRecords(reviewer_id::restaurant_id)가 중복을 병합하므로
  부족 리프만 골라 재수집해 기존 14,062건에 보강 가능. (동기: 대형 리프들에서 기대 대비
  레코드 부족 관측 — 도쿄 -229 등, 수집 중 라이브 변동 의심)
