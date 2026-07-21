# v1.3 변경 요약 (실측 HTML 기반 파서 확정)

v1.2(트리 구조·요구사항 확정) 이후, 사용자가 **실제 페이지 HTML**(카드 1개 + pal=tokyo 전체 페이지 + 패널 덤프)을 제공하여 파서를 추측이 아닌 실측 셀렉터로 확정함.

## 코드 구조 변경
- **`parsers.js` 신설**: 모든 DOM 파싱·URL 로직을 chrome API 비의존 모듈로 분리. 브라우저(content script)와 Node(jsdom 테스트)가 **동일 코드**를 실행 → 테스트-배포 드리프트 제거.
- **`content.js`는 오케스트레이터로 축소**: 상태기계(수집→seen→push→pop→단일저장→이동)만 담당.

## 실측으로 확정된 셀렉터 (2026-07-02 사용자 HTML)
| 필드 | 셀렉터 | 실측 예 |
|---|---|---|
| 카드 컨테이너 | `div.simple-rvw--rstdata` | 페이지당 20개 |
| 식당명/URL | `a.simple-rvw__rst-name-target` | たかむら別邸やまじん |
| 역/장르 | `p.simple-rvw__area-catg` ('/' 분리) | 神谷町、…/日本料理 |
| **타베로그 종합점** | `b.simple-rvw__score-total-val` | 4.06 |
| **리뷰어 개인점** | `.p-preview-visit .c-rating-v2__val` (복수 시 max) | 5.0 |
| 리뷰 수 | `.simple-rvw__rvw-count em` | 49 |
| 예산 夜/昼 | `.simple-rvw__budget` + `.c-rating__time--dinner/lunch` | ￥40,000～￥49,999 / '-'→null |
| 정휴일 | `.simple-rvw__holiday-text` | '-'→null |
| 방문월/횟수 | `.p-preview-visit__visited-date` / `__visit-count-num` | 2024/08 / 1回 |
| 리뷰 상세 | `.p-preview-visit[data-detail-url]` | /rvwr/maro/rvwdtl/B490866169/ |
| 표시명 | `.rvwr-nickname` | maro-j |
| 총 건수 | `.c-page-count__num strong`(마지막) → 텍스트 폴백 | 9399 |
| 페이지네이션 | `a[rel="next"]` | 次の20件 → PG=2 |

## 해결된 미해결 항목
- **OI-11 해결**: 종합점(`simple-rvw__score-total-val`)과 리뷰어 개인점(`c-rating-v2__val`)의 클래스가 실측으로 명확히 구분됨. 휴리스틱 제거.
- **OI-2a 재확인**: 자식 지역 링크는 `.list-balloon` 내부 `a.c-link-arrow`. 비활성(伊豆諸島·小笠原)은 `span.list-balloon__item-nolink`라 앵커가 아니어서 자동 배제 확인.
- **OI-3 부분 진전**: 리뷰 상세 경로가 `/rvwr/{slug}/rvwdtl/B{id}/`로 확인됨. 이는 robots Disallow인 `visitdtl`과 **다른 경로**. 단, rvwdtl 접근 자체의 규약 적합성은 FR-08 착수 전 재확인 필요(C-8 유지).
- **OI-8 해결**: 최소 URL(`?pal=tokyo`)과 전체 파라미터 URL의 총 건수가 **둘 다 9399**로 동일 → `award_year=2026` 등 장식 파라미터는 결과를 필터링하지 않음. 고정 파라미터 세트 유지 안전.
- **FR-01b 추가**: 스택 소진 시 `reviewerQueue`에서 다음 슬러그를 꺼내 루트로 자동 전환(구 OI-10).

## 자식 수확 엄격 규칙 (오염 방지)
자식 판정: 현재 노드의 의미 파라미터를 **전부 동일 값으로 보존**하면서 **정확히 1개**의 새 키를 도입하고, 그 키가 **기대 축의 다음 키**일 것. 이 규칙으로 브레드크럼(값 변경)·건너뛰기 링크(2키 추가)·정렬/사이드바(화이트리스트 밖)·PG 링크·모바일(s.tabelog)·집계(pal=atw/japan)가 전부 자동 배제됨. 음성 테스트로 검증.

## 테스트
- `test_logic.mjs` (18): URL 정규화·트리 깊이·리프 생성·세그먼트·리뷰어 루트 — 배포 parsers.js 직접 import
- `test_dom.mjs` (42): jsdom으로 **실제 저장 페이지**에 배포 코드 실행 — 카드 전 필드, 20건 수집, 9399 건수, 자식 30개 수확, 엄격 규칙 음성 테스트
- **합계 60/60 통과**

## 남은 브라우저 검증
- 다른 지역/장르 노드에서 셀렉터 일반화(현재 pal=tokyo 1페이지로 확정)
- 수상 뱃지 마크업(이 페이지 미출현 → 텍스트 폴백 미검증)
- 실제 순회 시 커버리지 감사(자식 지역 건수 합 = 부모) 오차율
- rvwdtl 경로 접근의 규약 적합성 최종 확인(C-8)
