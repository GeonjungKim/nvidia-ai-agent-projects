/* =====================================================================
 * parsers.js — DOM 파싱·URL 로직 (chrome API 비의존)
 * 브라우저(content script)와 Node(jsdom 테스트)에서 '동일 코드'가 실행된다.
 * 모든 셀렉터·패턴은 2026-07-02 사용자 제공 실측 HTML에서 확정됨.
 *
 * 실측 근거 요약:
 *  - 카드 컨테이너: div.simple-rvw.simple-rvw--rstdata (페이지당 20개 확인)
 *  - 식당명/URL:   a.simple-rvw__rst-name-target
 *  - 역/장르:      p.simple-rvw__area-catg → "역1、역2/장르1、장르2" ('/' 구분)
 *  - 타베로그 종합점: b.simple-rvw__score-total-val (예 4.06)          ← OI-11 해결
 *  - 리뷰어 개인점:   .p-preview-visit .c-rating-v2__val (예 5.0)      ← OI-11 해결
 *  - 리뷰 수:      .simple-rvw__rvw-count em (예 49)
 *  - 예산:         .simple-rvw__budget (夜/昼 각 1블록, 값은 전각 ￥·～, 없으면 '-')
 *  - 정휴일:       .simple-rvw__holiday-text ('-'면 없음)
 *  - 방문월/횟수:  .p-preview-visit__visited-date / __visit-count-num
 *  - 리뷰 상세:    .p-preview-visit[data-detail-url] = "/rvwr/{slug}/rvwdtl/B{id}/"
 *                  (robots Disallow는 visitdtl — rvwdtl은 별개 경로. 접근은 FR-08에서 재검증)
 *  - 수상 뱃지(v1.4, 2026-07-03 실측): 카드 내 div.simple-rvw__award-badge, 그 안의
 *      span.c-badge-award--{YYYY}{gold|silver|bronze}   (예: 2026年Gold受賞店, 페이지에 18개)
 *      span.c-badge-hyakumeiten--{YYYY}{category}       (예: 寿司 TOKYO 百名店 2025 選出店, 17개)
 *      span.c-badge-hot-restaurant--{YYYY}              (例: 食べログ ホットレストラン 2026 受賞店, 1개)
 *      → 클래스 수식어에서 {연도, 등급/카테고리}를 기계판독, <i> 텍스트를 label로 보존.
 *      텍스트 정규식은 구조 뱃지가 0개일 때만 쓰는 안전망으로 강등(v1.3의 주경로였음).
 *  - 총 건수:      .c-page-count__num strong (마지막 값) / 텍스트 "全 N 件" 폴백
 *  - 필터 패널:    .list-balloon 내부 a. 브레드크럼(a.list-balloon__breadcrumb,
 *                  예: すべて→pal=atw)은 제외. 비활성은 span.list-balloon__item-nolink라
 *                  앵커가 아니어서 자동 배제. 상단 pal=japan 집계 링크는 패널 밖.
 *  - 페이지네이션: a[rel="next"].c-pagination__arrow--next + 번호 a.c-pagination__num
 * ===================================================================== */

(function () {
  const CFG = (typeof module !== "undefined" && module.exports)
    ? require("./config.js")
    : TBLG; // 브라우저: config.js가 먼저 로드됨 (동일 isolated world의 전역 렉시컬)

  const REGION_KEYS = ["pal", "LstPrf", "LstAre"];   // 서로소 축 (실측 3계층)
  const GENRE_KEYS = ["Cat", "LstCat", "LstCatD"];   // 중복 축 (실측 3계층)

  /* ---------------- URL 유틸 ---------------- */

  // 노드 정체성을 정의하는 의미 파라미터 (PG 제외 여부 선택 가능)
  function meaningfulFilters(href, includePG = false) {
    const m = new Map();
    let u; try { u = new URL(href); } catch { return m; }
    for (const p of CFG.MEANINGFUL_PARAMS) {
      if (!includePG && p === "PG") continue;
      const v = u.searchParams.get(p);
      if (v !== null && v !== "") m.set(p, v);
    }
    return m;
  }

  // seen/스택 키 정규화 (FR-03): 화이트리스트 + 고정 파라미터, 사전순, 빈값 제거
  function normalizeUrl(href) {
    let u; try { u = new URL(href); } catch { return href; }
    const keep = new URLSearchParams();
    for (const p of CFG.MEANINGFUL_PARAMS) {
      const v = u.searchParams.get(p);
      if (v !== null && v !== "") keep.set(p, v);
    }
    for (const [k, v] of Object.entries(CFG.FIXED_PARAMS)) keep.set(k, v);
    let path = u.pathname.replace(/\/+$/, "/");
    if (!path.endsWith("/")) path += "/";
    const sorted = [...keep.entries()].sort((a, b) => a[0].localeCompare(b[0]));
    const qs = sorted.map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join("&");
    return `${u.origin}${path}${qs ? "?" + qs : ""}`;
  }

  function getParam(href, key) {
    try { return new URL(href).searchParams.get(key); } catch { return null; }
  }

  function reviewerSlugFromPath(pathname) {
    const m = String(pathname).match(/\/rvwr\/([^\/]+)\//);
    return m ? m[1] : null;
  }

  // 식당 URL 세그먼트: /{pref}/A####/A######/{id}/
  function urlSegments(href) {
    try {
      const parts = new URL(href).pathname.split("/").filter(Boolean);
      const idIdx = parts.findIndex((p) => /^\d+$/.test(p));
      return {
        pref: parts[0] || null,
        area2: parts[1] || null,
        area3: parts[2] || null,
        restaurantId: idIdx >= 0 ? parts[idIdx] : null
      };
    } catch { return {}; }
  }

  function cleanRestaurantUrl(href) {
    try { const u = new URL(href); return `${u.origin}${u.pathname.replace(/\/+$/, "/")}`; }
    catch { return href; }
  }

  // 리프의 PG 페이지 URL 직접 생성 (실측: PG는 GET 파라미터)
  function buildPageUrls(baseHref, pages, from = 2) {
    const out = [];
    const cap = Math.min(pages, CFG.PAGINATION_CEILING_PAGES);
    for (let p = from; p <= cap; p++) {
      const u = new URL(baseHref);
      u.searchParams.set("PG", String(p));
      out.push(normalizeUrl(u.toString()));
    }
    return out;
  }

  function buildRootUrl(slug) {
    const base = `https://tabelog.com/rvwr/${encodeURIComponent(slug)}/visited_restaurants/list/`;
    const p = new URLSearchParams(CFG.FIXED_PARAMS);
    return `${base}?${p.toString()}`;
  }

  function sourceNodeLabel(pageHref) {
    const m = meaningfulFilters(pageHref, /*includePG*/ true);
    const s = [...m.entries()].map(([k, v]) => `${k}=${v}`).join("&");
    return s || "root";
  }

  /* ---------------- 페이지 레벨 파싱 ---------------- */

  // 총 건수 (FR-04). 1차: 구조 셀렉터(마지막 c-page-count__num = 全N件의 N, 실측 9399)
  //                2차: 텍스트 정규식 "全 N 件"
  function parseTotalCount(doc) {
    const nums = doc.querySelectorAll(".c-page-count .c-page-count__num strong, .c-page-count__num strong");
    if (nums.length) {
      const n = parseInt(nums[nums.length - 1].textContent.replace(/[^\d]/g, ""), 10);
      if (Number.isFinite(n)) return n;
    }
    const body = doc.body ? (doc.body.innerText || doc.body.textContent || "") : "";
    const m = body.match(CFG.TOTAL_COUNT_RE);
    return m ? parseInt(m[1].replace(/,/g, ""), 10) : null;
  }

  // 페이지네이션 폴백 (실측: a rel="next" class="c-pagination__arrow--next")
  function findNextPageFallback(doc) {
    const a = doc.querySelector('a[rel="next"]');
    return a && a.getAttribute("href") ? a.getAttribute("href") : null;
  }

  // 오류/차단 페이지 감지 (백오프 트리거)
  function isErrorPage(doc) {
    const body = doc.body ? (doc.body.innerText || doc.body.textContent || "") : "";
    if (body.replace(/\s+/g, "").length < 40) return true;
    if (/アクセスが集中|しばらく時間をおいて|Too Many Requests|一時的なエラー/.test(body)) return true;
    const hasCount = doc.querySelector(".c-page-count") !== null;
    const hasCards = doc.querySelector(".simple-rvw--rstdata") !== null;
    const hasPanel = doc.querySelector(".list-balloon") !== null;
    // 주의: '0건' 정상 페이지가 세 신호 모두 없다면 오탐 가능(백오프 3회 후 실패 기록으로 수렴) — 파일럿에서 확인
    return !hasCount && !hasCards && !hasPanel;
  }

  /* ---------------- 카드 파싱 (FR-02 / FR-10) ---------------- */

  function txt(el) { return el ? el.textContent.replace(/\s+/g, " ").trim() : ""; }
  function numOrNull(s) { const v = parseFloat(s); return Number.isFinite(v) ? v : null; }
  function dashNull(s) { const t = (s || "").trim(); return !t || t === "-" ? null : t; }

  /* 수상 뱃지 파싱 (v1.4, 실측 2026-07-03 사용자 제공 pal=tokyo 페이지)
   * 실측 마크업:
   *   <div class="simple-rvw__award-badge rvwr-award-badge">
   *     <span class="c-badge-award c-badge-award--square c-badge-award--2026gold"><i>2026年Gold受賞店</i></span>
   *     <div class="rvwr-award-badge__tooltip-wrap">…<p>The Tabelog Award 2026 Gold 受賞店</p>…</div>
   *   </div>
   * 한 카드에 복수 뱃지 가능(실측 최대 3: award+百名店+hot). 반환은 객체 배열:
   *   { type:"tabelog_award", year, rank:"gold|silver|bronze", label }
   *   { type:"hyakumeiten",  year, category:"sushi|french|…", label }   ← 라벨엔 TOKYO/EAST 등 지역 수식이 남음
   *   { type:"hot_restaurant", year, label }
   *   { type:"unknown", year|null, label, cls }                          ← 미지 뱃지도 보존(스키마 방어)
   * 구조 뱃지가 0개일 때만 v1.3의 텍스트 정규식을 안전망으로 실행(type:"text_fallback"). */
  function parseAwards(card) {
    const awards = [];
    for (const wrap of card.querySelectorAll(".simple-rvw__award-badge")) {
      const s = wrap.querySelector("[class*='c-badge']");
      if (!s) continue;
      const cls = s.getAttribute("class") || "";
      const label = txt(s);
      let m;
      if ((m = cls.match(/c-badge-award--(20\d{2})(gold|silver|bronze)/i))) {
        awards.push({ type: "tabelog_award", year: +m[1], rank: m[2].toLowerCase(), label });
      } else if ((m = cls.match(/c-badge-hyakumeiten--(20\d{2})([a-z0-9_]+)/i))) {
        awards.push({ type: "hyakumeiten", year: +m[1], category: m[2], label });
      } else if ((m = cls.match(/c-badge-hot-restaurant--(20\d{2})/i))) {
        awards.push({ type: "hot_restaurant", year: +m[1], label });
      } else {
        const y = label.match(/20\d{2}/);
        awards.push({ type: "unknown", year: y ? +y[0] : null, label, cls });
      }
    }
    if (awards.length === 0) {                       // 안전망(마크업 전면 변경 대비)
      const cardText = card.textContent || "";
      const medal = cardText.match(/(20\d{2})\s*(BRONZE|SILVER|GOLD)/i);
      if (medal) awards.push({ type: "text_fallback", year: +medal[1], rank: medal[2].toLowerCase(), label: `${medal[1]} ${medal[2].toUpperCase()}` });
      const hyaku = cardText.match(/百名店\s*(20\d{2})/);
      if (hyaku) awards.push({ type: "text_fallback", year: +hyaku[1], label: hyaku[0].replace(/\s+/g, "") });
    }
    return awards;
  }

  function parseCard(card, baseHref, ctx) {
    const nameA = card.querySelector(".simple-rvw__rst-name-target")
      || [...card.querySelectorAll("a")].find((a) => CFG.RESTAURANT_URL_RE.test(a.href || a.getAttribute("href") || ""));
    if (!nameA) return null;
    const rawHref = nameA.href || nameA.getAttribute("href") || "";
    let abs; try { abs = new URL(rawHref, baseHref).toString(); } catch { return null; }
    if (!CFG.RESTAURANT_URL_RE.test(abs)) return null;

    const seg = urlSegments(abs);
    if (!seg.restaurantId) return null;

    // 역 / 장르: "神谷町、六本木一丁目、虎ノ門ヒルズ/日本料理"
    let stations = [], genres = [];
    const ac = txt(card.querySelector(".simple-rvw__area-catg"));
    if (ac) {
      const i = ac.search(/[\/／]/);
      const st = i >= 0 ? ac.slice(0, i) : ac;
      const gn = i >= 0 ? ac.slice(i + 1) : "";
      stations = st.split(/[、,]/).map((s) => s.trim()).filter(Boolean);
      genres = gn.split(/[、,]/).map((s) => s.trim()).filter(Boolean);
    }

    // 예산: 夜/昼 블록 각각 (전각 ￥·～, '-'는 null)
    let budgetDinner = null, budgetLunch = null;
    for (const b of card.querySelectorAll(".simple-rvw__budget")) {
      const val = dashNull(txt(b.querySelector(".c-rating__val")));
      if (b.querySelector(".c-rating__time--dinner")) budgetDinner = val;
      else if (b.querySelector(".c-rating__time--lunch")) budgetLunch = val;
    }

    // 리뷰어 개인 점수(들): 夜の点数/昼の点数 등 복수 가능 → 최대값 채택
    const visit = card.querySelector(".p-preview-visit");
    const myScores = visit
      ? [...visit.querySelectorAll(".c-rating-v2__val")].map((e) => parseFloat(e.textContent)).filter(Number.isFinite)
      : [];

    // 리뷰 상세 URL: data-detail-url="/rvwr/{slug}/rvwdtl/B{bookmarkId}/"
    // robots Disallow(visitdtl) 경로면 저장하지 않음(C-8 조기 차단). rvwdtl은 별개 경로(실측).
    let reviewUrl = null, bookmarkId = null;
    if (visit) {
      bookmarkId = visit.getAttribute("data-bookmark-id") || null;
      const d = visit.getAttribute("data-detail-url");
      if (d) {
        try {
          const u = new URL(d, baseHref).toString();
          reviewUrl = /\/visitdtl\//.test(u) ? null : u;
        } catch { /* noop */ }
      }
    }

    // 수상 뱃지 (v1.4): 실측 구조 셀렉터. 상세는 parseAwards 참조.
    const awards = parseAwards(card);

    const vm = txt(card.querySelector(".p-preview-visit__visited-date")).match(/(20\d{2})\/(\d{1,2})/);
    const vc = txt(card.querySelector(".p-preview-visit__visit-count-num")).match(/(\d+)/);

    return {
      reviewer_id: ctx.reviewerId,
      reviewer_display_name: ctx.displayName,
      restaurant_id: seg.restaurantId,
      name: txt(nameA),
      url: cleanRestaurantUrl(abs),
      pref: seg.pref, area2: seg.area2, area3: seg.area3,
      genres, stations,
      tabelog_rating: numOrNull(txt(card.querySelector(".simple-rvw__score-total-val"))),
      tabelog_review_count: (() => {
        const t = txt(card.querySelector(".simple-rvw__rvw-count em"));
        const n = parseInt(t.replace(/,/g, ""), 10);
        return Number.isFinite(n) ? n : null;
      })(),
      budget_dinner: budgetDinner,
      budget_lunch: budgetLunch,
      closed_days: dashNull(txt(card.querySelector(".simple-rvw__holiday-text"))),
      awards,
      reviewer_rating: myScores.length ? Math.max(...myScores) : null,
      visited_month: vm ? `${vm[1]}/${vm[2].padStart(2, "0")}` : null,
      visit_count: vc ? parseInt(vc[1], 10) : null,
      review_url: reviewUrl,
      bookmark_id: bookmarkId,
      source_node: ctx.sourceNode
    };
  }

  // 페이지의 모든 카드 수집. 카드 셀렉터 실패 시 링크 패턴 폴백(마크업 변경 대비)
  function harvestRestaurants(doc, pageHref) {
    const ctx = {
      reviewerId: reviewerSlugFromPath(new URL(pageHref).pathname),
      displayName: txt(doc.querySelector(".rvwr-nickname")) || null,   // 실측: <strong class="rvwr-nickname">maro-j
      sourceNode: sourceNodeLabel(pageHref)
    };
    const records = [];
    const seen = new Set();
    const cards = doc.querySelectorAll(".simple-rvw--rstdata");
    if (cards.length > 0) {
      for (const card of cards) {
        const r = parseCard(card, pageHref, ctx);
        if (r && !seen.has(r.restaurant_id)) { seen.add(r.restaurant_id); records.push(r); }
      }
      return { records, mode: "card" };
    }
    // 폴백: 링크 패턴만으로 최소 레코드 (name/url/지역)
    for (const a of doc.querySelectorAll("a")) {
      const href = a.href || a.getAttribute("href") || "";
      let abs; try { abs = new URL(href, pageHref).toString(); } catch { continue; }
      if (!CFG.RESTAURANT_URL_RE.test(abs)) continue;
      const name = txt(a); if (name.length < 2) continue;
      const seg = urlSegments(abs);
      if (!seg.restaurantId || seen.has(seg.restaurantId)) continue;
      seen.add(seg.restaurantId);
      records.push({
        reviewer_id: ctx.reviewerId, reviewer_display_name: ctx.displayName,
        restaurant_id: seg.restaurantId, name, url: cleanRestaurantUrl(abs),
        pref: seg.pref, area2: seg.area2, area3: seg.area3,
        genres: [], stations: [], tabelog_rating: null, tabelog_review_count: null,
        budget_dinner: null, budget_lunch: null, closed_days: null, awards: [],
        reviewer_rating: null, visited_month: null, visit_count: null,
        review_url: null, bookmark_id: null, source_node: ctx.sourceNode
      });
    }
    return { records, mode: "link-fallback" };
  }

  /* ---------------- 자식 필터 링크 수확 (FR-04) ---------------- */
  /* 실측 규칙:
   *  - 스코프: .list-balloon 내부 a 만 (상단 nav의 pal=japan 집계 링크는 패널 밖 → 배제)
   *  - 브레드크럼 제외: a.list-balloon__breadcrumb (예: すべて → pal=atw 집계)
   *  - 비활성(span.list-balloon__item-nolink)은 앵커가 아니라 자동 배제
   *  - 동일 호스트 tabelog.com + 동일 리뷰어 경로만 (s.tabelog.com 모바일 링크 배제)
   *  - 자식 판정(strict): 현재 노드의 의미 파라미터를 '전부 동일 값으로 보존'하면서
   *    '정확히 1개'의 새 키를 도입하고, 그 키가 기대 축의 다음 키일 것.
   *    → 브레드크럼(값 변경)·건너뛰기 링크(2키 추가)·정렬/사이드바(화이트리스트 밖)·PG 링크 전부 자동 배제
   */
  function regionDepth(filters) {
    return filters.has("LstAre") ? 3 : filters.has("LstPrf") ? 2 : filters.has("pal") ? 1 : 0;
  }
  function genreDepth(filters) {
    if (filters.has("LstCatD") || filters.has("genre_name")) return 3; // genre_name은 계층 하강 불가 → 말단 취급
    if (filters.has("LstCat")) return 2;
    if (filters.has("Cat")) return 1;
    return 0;
  }

  // 상세 버전(v1.4): 커버리지 감사 리포트용으로 앵커 텍스트(지역/장르 라벨)와
  // 새로 도입된 키의 값(예: LstPrf=A1307)을 함께 반환. 판정 규칙은 기존과 동일.
  function collectChildLinksDetailed(doc, pageHref, expectedKey) {
    const cur = meaningfulFilters(pageHref);
    const slug = reviewerSlugFromPath(new URL(pageHref).pathname);
    const out = [];
    const dedup = new Set();
    for (const a of doc.querySelectorAll(".list-balloon a")) {
      if (a.classList && a.classList.contains("list-balloon__breadcrumb")) continue;
      const raw = a.getAttribute("href") || "";
      if (!raw || raw === "#") continue;
      let u; try { u = new URL(raw, pageHref); } catch { continue; }
      if (u.hostname !== "tabelog.com") continue;                                   // s.tabelog.com 배제
      if (!u.pathname.startsWith(`/rvwr/${slug}/visited_restaurants/list`)) continue;
      const ch = meaningfulFilters(u.toString());
      let preserved = true;
      for (const [k, v] of cur) { if (ch.get(k) !== v) { preserved = false; break; } }
      if (!preserved) continue;
      const newKeys = [...ch.keys()].filter((k) => !cur.has(k));
      if (newKeys.length !== 1 || newKeys[0] !== expectedKey) continue;
      const key = normalizeUrl(u.toString());
      if (dedup.has(key)) continue;
      dedup.add(key);
      out.push({ url: key, text: (a.textContent || "").replace(/\s+/g, " ").trim(), value: ch.get(expectedKey) });
    }
    return out;
  }

  function collectChildLinks(doc, pageHref, expectedKey) {
    return collectChildLinksDetailed(doc, pageHref, expectedKey).map((c) => c.url);
  }

  // 축 우선순위: 지역(서로소, 검산 가능) → 장르(중복). 각 축의 '다음 한 단계'만.
  function harvestChildFilterLinks(doc, pageHref) {
    const cur = meaningfulFilters(pageHref);
    const rd = regionDepth(cur);
    const gd = genreDepth(cur);
    const tryKeys = [];
    if (rd < REGION_KEYS.length) tryKeys.push({ axis: "region", key: REGION_KEYS[rd] });
    if (gd < GENRE_KEYS.length) tryKeys.push({ axis: "genre", key: GENRE_KEYS[gd] });
    for (const t of tryKeys) {
      const links = collectChildLinks(doc, pageHref, t.key);
      if (links.length > 0) return { axis: t.axis, key: t.key, links };
    }
    return { axis: null, key: null, links: [] };
  }

  // 상세 버전(v1.4): children = [{url, text, value}]
  function harvestChildFilterLinksDetailed(doc, pageHref) {
    const cur = meaningfulFilters(pageHref);
    const rd = regionDepth(cur);
    const gd = genreDepth(cur);
    const tryKeys = [];
    if (rd < REGION_KEYS.length) tryKeys.push({ axis: "region", key: REGION_KEYS[rd] });
    if (gd < GENRE_KEYS.length) tryKeys.push({ axis: "genre", key: GENRE_KEYS[gd] });
    for (const t of tryKeys) {
      const children = collectChildLinksDetailed(doc, pageHref, t.key);
      if (children.length > 0) return { axis: t.axis, key: t.key, children };
    }
    return { axis: null, key: null, children: [] };
  }

  const P = {
    REGION_KEYS, GENRE_KEYS,
    meaningfulFilters, normalizeUrl, getParam, reviewerSlugFromPath,
    urlSegments, cleanRestaurantUrl, buildPageUrls, buildRootUrl, sourceNodeLabel,
    parseTotalCount, findNextPageFallback, isErrorPage,
    parseAwards, parseCard, harvestRestaurants,
    regionDepth, genreDepth, collectChildLinks, collectChildLinksDetailed,
    harvestChildFilterLinks, harvestChildFilterLinksDetailed
  };

  if (typeof module !== "undefined" && module.exports) module.exports = P;
  else (typeof self !== "undefined" ? self : window).TBLG_P = P;
})();
