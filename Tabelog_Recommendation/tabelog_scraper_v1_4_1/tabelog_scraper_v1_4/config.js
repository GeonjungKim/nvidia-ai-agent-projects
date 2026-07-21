/* =====================================================================
 * config.js — 수집기 상수 (단일 정의 지점)
 * 요구사항분석서 v1.2의 C-4 / FR-04 / FR-06 집행 지점.
 * 이 값들은 하드코딩 상수이며, 런타임에 완화하지 않는다.
 * ===================================================================== */

const TBLG = {
  // --- 레이트리밋 (C-4, FR-06) ---
  // 근거: tabelog robots.txt는 명시적으로 throttle하는 봇(bingbot 등)에 Crawl-delay: 5를 부여.
  //       User-agent:* 그룹에는 Crawl-delay가 없으므로 이는 '지시'가 아니라 우리가 자율적으로
  //       채택하는 하한(self-imposed floor)임. 5초를 하한으로, 5~8초 랜덤으로 요청.
  MIN_DELAY_MS: 5000,          // 하한. 하향 금지.
  MAX_DELAY_MS: 8000,          // 상한(랜덤 지터 범위).

  // 지수 백오프(오류/빈 페이지 감지 시)
  BACKOFF_MS: [30000, 60000, 120000],  // 30s -> 60s -> 120s -> 중지

  // --- 페이지네이션 / 분할 (FR-04) ---
  // 근거(실측 2026-07-02): "61~80 件を表示" => 페이지당 20건.
  PAGE_SIZE: 20,
  // 근거(실측): maro 전체 14,389건에서 필터 없이 1,138건 수집 후 종료 => 약 60페이지(=1,200건) 노출 제한.
  //       임계값을 페이지 제한과 동일선(1,200)으로 두고, 초과 노드는 하위로 분할.
  PAGINATION_CEILING_PAGES: 60,
  SPLIT_THRESHOLD: 1200,       // = PAGE_SIZE * PAGINATION_CEILING_PAGES

  // --- URL 파라미터 (실측 확정) ---
  // 지역 축(서로소): pal(도도부현 슬러그) > LstPrf(2차 A코드) > LstAre(3차 A코드)
  // 장르 축(중복):   Cat(대분류) > LstCat(중분류) > LstCatD(소분류)
  // seen 키에 포함할 '의미' 파라미터 (정렬/장식 파라미터는 제외)
  MEANINGFUL_PARAMS: [
    "pal", "LstPrf", "LstAre",          // 지역 3계층
    "Cat", "LstCat", "LstCatD",         // 장르 3계층
    "genre_name",                        // 장르 대체 표기(실측에서 관찰)
    "PG"                                 // 페이지 번호
  ],
  // 크롤 전체 동안 고정할 정렬/장식 파라미터 (페이지 간 정렬 불일치 방지)
  FIXED_PARAMS: {
    "Srt": "D",
    "SrtT": "mfav",
    "bookmark_type": "1",
    "review_content_exist": "0"
    // award_year는 의도적으로 제외: 특정 연도 수상만 필터될 위험(OI-8에서 동일성 검증 전까지 미포함)
  },

  // --- 리스트 카드 셀렉터 후보 (FR-10) ---
  // 링크 강제 추적 패턴(실측 검증됨): /{pref}/A\d+/A\d+/\d+/
  RESTAURANT_URL_RE: /tabelog\.com\/[a-z]+\/A\d+\/A\d+\/\d+\/?$/,
  // 총 건수 텍스트 파싱(실측 표기 "全 14389 件"): 셀렉터 비의존
  TOTAL_COUNT_RE: /全\s*([\d,]+)\s*件/,

  // --- 저장소 관리 (NFR-02) ---
  EXPORT_REMINDER_AT: 3000     // 레코드 이 수 초과 시 export 권고 플래그
};

// 서비스워커/콘텐츠/팝업 어디서든 접근
if (typeof module !== "undefined") { module.exports = TBLG; }
