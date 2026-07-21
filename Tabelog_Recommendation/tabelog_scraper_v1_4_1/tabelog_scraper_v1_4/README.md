# Tabelog Reviewer Scraper (v1.4, tree-DFS)

리뷰어의 방문 식당 리스트를 **지역×장르 트리**로 건수 기준 적응 분할하여 수집하는 크롬 익스텐션.
수업 내 비공개 분석용. 요구사항분석서 v1.2 준수.

## 파일
| 파일 | 역할 |
|---|---|
| `manifest.json` | MV3 설정. js 로드 순서 config→parsers→content. 매칭 경로 `visited_restaurants/list` 한정(robots Disallow 제외) |
| `config.js` | 상수 단일 정의(대기 하한 5초·분할 임계 1,200·20건/페이지·파라미터 화이트리스트) |
| `parsers.js` | **DOM 파싱·URL 로직(chrome 비의존).** 브라우저와 Node 테스트가 동일 코드 실행 |
| `content.js` | 트리-DFS 오케스트레이터(상태기계). 파싱은 parsers.js에 위임 |
| `popup.html` / `popup.js` | 상태 표시 + JSON 다운로드 + **커버리지 감사 버튼** + **시작 노드 URL(스코프 크롤)** |
| `test_logic_v14.mjs` | URL·트리 순수 로직 + 엄격 자식 규칙 합성 + parseAwards 단위(34개) |
| `test_dom_v14.mjs` | jsdom으로 실측 페이지에 배포 코드 실행 — 뱃지 36개 전수 대조 포함(33개) |
| `fixtures_page.html` / `fixtures_card.html` | 실측 픽스처(2026-07-02, pal=tokyo) |
| `CHANGELOG_v1_3.md` / `CHANGELOG_v1_4.md` | 실측 셀렉터 확정 내역 / v1.4 변경(뱃지 스키마·감사·스코프) |
| `PILOT_GUIDE.md` | 파일럿 실행 절차(감사 → 노드 선정 → 스코프 크롤 → 검산) |

## 설치
1. `chrome://extensions/` → 우측 상단 **개발자 모드** 켜기
2. **압축해제된 확장 프로그램을 로드** → 이 폴더 선택
3. 리뷰어 방문 리스트 페이지 열기: `https://tabelog.com/rvwr/{슬러그}/visited_restaurants/list/`
4. 퍼즐 아이콘 → 확장 팝업 → 리뷰어 슬러그 입력(예: `maro`) → **수집 시작**

## 동작 원리 (FR-04)
```
노드 진입(PG 없음/PG=1)
  → 총 건수 파싱 "全 N 件"
    ├ N > 1200 → 다음 축(지역 LstPrf→LstAre, 그다음 장르 Cat→LstCat→LstCatD)
    │            자식 링크를 '패널 DOM에서' 수확해 스택 push (하드코딩 안 함)
    │            자식이 없으면 PG1..60 수집 + 잔여 손실 기록
    └ N ≤ 1200 → 리프: PG2..ceil(N/20) URL을 직접 생성해 순회
  → 카드 수집 → seen 기록 → pop → 단일 저장 → 5~8초 뒤 이동
```
- **seen-set**으로 중복·순환 방지. **단일 `storage.set` 후 이동**으로 상태 원자성 보장.
- 대기 **하한 5초**(robots.txt가 검색봇에 부여한 값을 자율 하한으로 채택), 오류 시 30/60/120초 백오프.

## 기존(Gemini) 코드 대비 수정점
| 결함 | 수정 |
|---|---|
| seen-set 없음 → 순환 | 정규화 seen 키 도입 |
| `storage.set` 이중 호출 레이스 | pop 후 단일 저장 → 콜백 내 이동 |
| 미검증 "임시" 셀렉터 | 패널 DOM에서 자식 필터 링크 수확 |
| 60페이지 제한 대응 없음 | 건수 기준 분할 + 60페이지 클램프 |
| `pref_cd=1..47` 오류 | 실측 3계층(`pal/LstPrf/LstAre`) 재귀 |
| 리뷰어 1명 하드코딩 | 슬러그 큐 |

## 테스트
```bash
node test_logic_v14.mjs   # 34/34 (URL·트리 순수 로직 + 규칙 합성 + parseAwards)
npm install jsdom         # test_dom 실행 전 1회
node test_dom_v14.mjs     # 33/33 (실측 픽스처에 배포 코드 실행)
```
※ 픽스처(`fixtures_page.html`, `fixtures_card.html`)는 이 폴더에 동봉(2026-07-02 실측). 갱신하려면 카드가 보이는 리스트 페이지에서 `document.documentElement.outerHTML`을 저장.

## 브라우저 실사용 검증이 남은 부분 (→ PILOT_GUIDE.md)
정적 테스트로 커버 불가 — 파일럿으로 확인:
- 커버리지 감사: Σ자식(LstPrf 30개) 건수 = 부모 9399? (Δ가 순회 손실의 직접 증거)
- 셀렉터 일반화: 도쿄 하위 30개 지역·비도쿄(pal=osaka 등) 페이지에서 파서 성공률
- 상태기계 E2E: 스코프 크롤로 리프 1개 완주(records == count), 1,200 초과 노드면 OI-6 겸사 확인
- 리뷰 본문 경로의 robots 준수(OI-3, C-8)는 FR-08 착수 전 별도 확인

## 주의
- 리뷰 상세 경로 `/rvwr/*/visitdtl/`는 robots.txt Disallow → 접근 금지(C-8).
- 수집 데이터·산출물은 비공개 분석용(C-1). 리뷰 원문 UI 노출 금지(C-2).
