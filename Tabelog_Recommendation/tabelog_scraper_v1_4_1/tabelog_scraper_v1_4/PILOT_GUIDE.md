# 파일럿 실행 가이드 (v1.4)

HANDOFF '다음 할 일 1'의 파일럿 3목표 중 **뱃지 마크업은 실측으로 이미 해소**(CHANGELOG v1.4 §1).
남은 목표 = ① 커버리지 감사 ② 셀렉터 일반화 ③ 상태기계 E2E(+OI-6 임계 재확인).
전 단계에서 요청 간 5~8초 대기·오류 백오프가 자동 적용된다.

## 준비 (1회)

1. `chrome://extensions/` → 기존 익스텐션 **제거** 후 이 폴더(v1.4)를 다시 로드
   (또는 새로고침 ↻ — manifest가 1.4.0인지 팝업 헤더로 확인)
2. 로그인 불필요. 크롤/감사 중 해당 탭을 닫거나 이동하지 말 것.

## 단계 A — 커버리지 감사 (도쿄, ~30요청 · 3~4분)

1. 탭에서 열기: `https://tabelog.com/rvwr/maro/visited_restaurants/list/?pal=tokyo`
2. 팝업 → **📊 커버리지 감사** 클릭 → 우하단 HUD로 진행 표시
3. 완료 시 `tabelog_audit_maro_LstPrf_*.json` 자동 다운로드 + alert에 Δ 표시
4. **JSON을 채팅에 업로드** → 아래를 판독:
   - `sums.delta` : Σ자식(30개 LstPrf) 건수 − 부모 9399. **0이면 지역축 완전 분할 확정**,
     ≠0이면 미분류 잔여(자식에 안 잡히는 레코드) 존재 → 트리 순회 손실 규모의 직접 증거
   - `selector_flags.zero_cards_with_count` / `link_fallback_children` : 셀렉터가 일반화되지
     않는 자식 노드 목록(비어야 정상)
   - `badge_variants` : 도쿄 30개 하위지역에서 관측된 뱃지 수식어 클래스 전수
     (새 카테고리/연도 변형이 parseAwards로 판독되는지 확인)

## 단계 B — 스코프 크롤 E2E (리프 1개 완주)

1. 단계 A 리포트에서 노드 선택:
   - **기본**: 건수 200~600 사이 자식 1개 (10~30페이지, 상태기계·페이지네이션 검증)
   - **OI-6 겸사 확인용(권장)**: 건수 **1,200 초과** 자식 1개(예상 후보: A1301 銀座 등)
     → LstAre 재분할까지 발동해 3계층 전부 검증됨
2. 팝업 → **시작 노드 URL**에 해당 자식 URL 입력(리포트의 `children[].url` 복사) → 수집 시작
3. 완료 alert 후 팝업 → **⭳ JSON** → **채팅에 업로드** → 아래를 검산:
   - `records.length` vs 리포트상 그 노드의 `count` (완전 수집 여부)
   - `meta.losses` : 비어야 정상(있다면 분할축 소진 노드)
   - `meta.expected` : 노드별 기대 건수 맵 — 하위 검산에 사용
   - awards 객체 스키마(`type/year/rank|category/label`)가 실데이터에서 채워지는지

## 단계 C (선택) — 비도쿄 일반화

`?pal=osaka` (또는 hokkaido 등) 페이지에서 단계 A만 반복.
도쿄에서 확정한 셀렉터·규칙이 타 도도부현 마크업에서도 성립하는지 동일 리포트로 확인.

## 주의

- 감사는 **읽기 전용**(수집 데이터·상태 불변). 크롤 중에는 감사 버튼이 비활성화된다.
- 시작 버튼은 기존 레코드가 있으면 초기화 confirm을 띄운다 — 보존하려면 먼저 JSON export.
- 요청량: 단계 A ≈ 31, 단계 B ≈ (노드 페이지 수 + 자식 진입 수). 임계 초과 노드(B의 OI-6 경로)는
  60페이지 캡 때문에 최대 61 + LstAre 자식 수 요청 규모.

## 트러블슈팅: 감사가 전부 "Failed to fetch" (v1.4.1 반영)

증상: 콘솔에 `s.tabelog.com/smartphone/…` 로의 리다이렉트 + CORS 차단.
점검 순서(해당 탭 콘솔에서):
1. `navigator.userAgent` 입력 → `Mobile/iPhone/Android` 포함이면 **기기 에뮬레이션 ON 상태**.
   DevTools 기기 툴바(Ctrl+Shift+M) OFF → **F5** → 감사 재실행. (v1.4.1은 이 상태를 시작 전에 차단함)
2. UA가 데스크톱인데도 실패하면 아래 프로브 실행 후 출력 공유:
   ```js
   fetch("/rvwr/maro/visited_restaurants/list/?pal=tokyo&LstPrf=A1301", {credentials:"same-origin"})
     .then(r => console.log("OK", r.status, "redirected:", r.redirected, "→", r.url))
     .catch(e => console.log("FAIL", e.name, e.message));
   ```
   FAIL이면 fetch 계층이 구조적으로 차단되는 환경 → 내비게이션 기반 감사로 전환(다음 버전).
참고: 페이지 URL의 `__cf_chl_f_tk=`는 Cloudflare 챌린지 통과 흔적 — 봇 관리가 활성인 세션이라는 뜻.
내비게이션은 챌린지를 사람이 풀 수 있지만 fetch는 불가하므로, fetch 실패가 지속되면
내비게이션 방식이 근본 해법이다(프로덕션 크롤이 내비게이션인 이유이기도 함).
