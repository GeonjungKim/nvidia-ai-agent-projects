/* =====================================================================
 * content.js — 트리-DFS 오케스트레이터 (요구사항 v1.3)
 * 파싱·URL 로직은 parsers.js(TBLG_P)에 위임. 여기는 상태기계만.
 *   상태 흐름: 수집 → seen 기록 → 자식 push → pop → 단일 저장 → 대기 → 이동
 *   (단일 chrome.storage.set 후 콜백 내 이동 = 원자성, D-2 fix)
 * ===================================================================== */

(async function main() {
  if (typeof TBLG === "undefined" || typeof TBLG_P === "undefined") {
    console.error("[Tabelog DFS] config/parsers 미로드 — manifest의 js 순서 확인");
    return;
  }
  const P = TBLG_P;

  const store = await getState();
  if (!store.isCrawling) return;

  // 현재 페이지가 진행 중인 리뷰어의 것인지 가드 (다른 탭/리뷰어 오염 방지)
  const slug = P.reviewerSlugFromPath(location.pathname);
  if (!slug || (store.currentReviewer && slug !== store.currentReviewer)) {
    log(`현재 크롤 대상(${store.currentReviewer})이 아닌 페이지 → 무시`);
    return;
  }

  // 오류/차단 페이지 → 지수 백오프 (FR-06)
  if (P.isErrorPage(document)) return handleBackoff(store);
  store.backoffLevel = 0;

  const nkey = P.normalizeUrl(location.href);
  log(`노드: ${decodeURIComponent(nkey)}`);

  // ── 1) 이 페이지의 카드 수집 (FR-02) ──
  const { records: harvested, mode } = P.harvestRestaurants(document, location.href);
  const added = mergeRecords(store, harvested);
  log(`카드 ${harvested.length}건 파싱(${mode}), 신규 ${added}, 누적 고유 ${store.records.length}`);

  // ── 2) 노드 진입 페이지에서만 분할/리프 결정 (FR-04) ──
  const pg = P.getParam(location.href, "PG");
  const isEntry = !pg || pg === "1";
  const toPush = [];

  if (isEntry) {
    const count = P.parseTotalCount(document);
    log(`총 건수: ${count === null ? "파싱 실패" : count}`);

    if (count !== null && count > TBLG.SPLIT_THRESHOLD) {
      const { axis, key, links } = P.harvestChildFilterLinks(document, location.href);
      if (links.length > 0) {
        log(`분할(${axis}:${key}): 자식 ${links.length}개 → 스택 적재, 이 노드는 페이지네이션 생략`);
        toPush.push(...links);
        store.expected[nkey] = { count, mode: "split", children: links.length };
      } else {
        const pages = TBLG.PAGINATION_CEILING_PAGES;
        log(`⚠ 분할축 소진 & ${count} > ${TBLG.SPLIT_THRESHOLD} → PG1..${pages} 수집, 잔여 ${count - TBLG.SPLIT_THRESHOLD}건 손실 기록`);
        store.losses.push({ node: nkey, total: count, capturedCap: TBLG.SPLIT_THRESHOLD });
        toPush.push(...P.buildPageUrls(location.href, pages));
        store.expected[nkey] = { count, mode: "leaf-with-loss" };
      }
    } else if (count !== null) {
      const pages = Math.ceil(count / TBLG.PAGE_SIZE);
      if (pages > 1) {
        log(`리프: ${count}건 → PG2..${pages} 생성`);
        toPush.push(...P.buildPageUrls(location.href, pages));
      }
      store.expected[nkey] = { count, mode: "leaf" };
    } else {
      // 건수 파싱 실패 → 안전측: 분할 시도, 없으면 다음버튼 폴백
      const { links } = P.harvestChildFilterLinks(document, location.href);
      if (links.length > 0) toPush.push(...links);
      else {
        const nx = P.findNextPageFallback(document);
        if (nx) { try { toPush.push(P.normalizeUrl(new URL(nx, location.href).toString())); } catch (_) {} }
      }
    }
  }

  // ── 3) seen 기록 + 미방문 자식만 push (FR-03) ──
  if (!store.seen.includes(nkey)) store.seen.push(nkey);
  // v1.4.2b (전국 크롤 2026-07-04 실측 반영): pal=atw는 지역 분할의 원소가 아니라 '전체' 집계
  // 노드다(실측: root와 동일 14,389건). 단, 60페이지 캡 안에서 패널 미노출 지층을 구조하는
  // 안전망 역할이 실증됨(pal 링크가 없던 kochi 1건·saga 4건이 atw 상위 1200에서 수집됨).
  // → 제외하지 않고 '마지막 방문'으로 강등: toPush 맨 앞 = 스택 바닥 = 최후 pop.
  // 효과: source_node가 리프 우선으로 귀속되고, atw발 신규 레코드 수 = 미도달 지층의 측정치.
  const isAtw = (u) => /[?&]pal=atw(?:&|$)/.test(u);
  toPush.sort((a, b) => (isAtw(a) ? -1 : 0) - (isAtw(b) ? -1 : 0));   // 안정 정렬: atw만 앞으로
  const inStack = new Set(store.stack);
  let pushed = 0;
  for (const child of toPush) {
    if (!store.seen.includes(child) && !inStack.has(child)) {
      store.stack.push(child); inStack.add(child); pushed++;
    }
  }
  log(`push ${pushed} / 스택 잔량 ${store.stack.length}`);

  // ── 4) 다음 목적지: pop → (스택 소진 시 리뷰어 전환 FR-01b) → 단일 저장 → 이동 ──
  const next = popNext(store);   // null이면 내부에서 isCrawling=false 처리

  await setState(store);   // ✅ 단일 set — 여기서 상태 확정 (FR-05)

  if (next) {
    const wait = randDelay();
    log(`⏳ ${(wait / 1000).toFixed(1)}s 후 이동`);
    setTimeout(() => { location.href = next; }, wait);
  } else {
    log("🛑 전체 순회 완료");
    notify(`수집 완료: 고유 ${store.records.length}건. 팝업에서 JSON을 다운로드하세요.`);
  }
})();

/* ---------------- 상태 저장소 (chrome 의존부) ---------------- */

function getState() {
  return new Promise((res) => {
    chrome.storage.local.get(
      ["isCrawling", "records", "seen", "stack", "backoffLevel", "losses", "expected", "reviewerQueue", "currentReviewer", "failures"],
      (r) => res({
        isCrawling: !!r.isCrawling,
        records: r.records || [],
        seen: r.seen || [],
        stack: r.stack || [],
        backoffLevel: r.backoffLevel || 0,
        losses: r.losses || [],
        expected: r.expected || {},
        reviewerQueue: r.reviewerQueue || [],
        currentReviewer: r.currentReviewer || null,
        failures: r.failures || []
      })
    );
  });
}
function setState(s) { return new Promise((res) => chrome.storage.local.set(s, res)); }

// (reviewer_id, restaurant_id) 복합키 병합. 기존 레코드의 null 필드는 새 값으로 보강.
function mergeRecords(store, incoming) {
  const key = (r) => `${r.reviewer_id}::${r.restaurant_id}`;
  const idx = new Map(store.records.map((r) => [key(r), r]));
  let added = 0;
  for (const r of incoming) {
    const k = key(r);
    if (!idx.has(k)) { idx.set(k, r); store.records.push(r); added++; }
    else {
      const old = idx.get(k);
      for (const f of Object.keys(r)) {
        if ((old[f] === null || old[f] === undefined || (Array.isArray(old[f]) && old[f].length === 0)) && r[f] !== null) old[f] = r[f];
      }
    }
  }
  return added;
}

// 다음 목적지: 스택 pop → 스택 소진 시 reviewerQueue에서 다음 리뷰어(FR-01b) → 없으면 종료.
// v1.4 fix: 백오프 실패 경로가 이 헬퍼를 공유하지 않아 마지막 노드 반복 실패 시
//           다음 리뷰어를 건너뛰던 결함 제거.
function popNext(store) {
  if (store.stack.length > 0) return store.stack.pop();
  if ((store.reviewerQueue || []).length > 0) {
    store.currentReviewer = store.reviewerQueue.shift();
    log(`✅ 리뷰어 완료 → 다음 리뷰어 '${store.currentReviewer}' 루트로 전환`);
    return TBLG_P.buildRootUrl(store.currentReviewer);
  }
  store.isCrawling = false;
  return null;
}

async function handleBackoff(store) {
  const lvl = store.backoffLevel || 0;
  if (lvl >= TBLG.BACKOFF_MS.length) {
    log("⛔ 백오프 한계 → 현재 URL 실패 기록 후 계속");
    store.failures.push({ url: P_safeNorm(location.href), ts: Date.now() });
    store.backoffLevel = 0;
    if (!store.seen.includes(P_safeNorm(location.href))) store.seen.push(P_safeNorm(location.href));
    const next = popNext(store);
    await setState(store);
    if (next) setTimeout(() => { location.href = next; }, randDelay());
    else notify("반복 오류로 수집을 종료했습니다. 실패 목록을 확인하세요.");
    return;
  }
  const wait = TBLG.BACKOFF_MS[lvl];
  store.backoffLevel = lvl + 1;
  await setState(store);
  log(`↩ 오류/빈 페이지 → ${wait / 1000}s 후 재시도 (백오프 ${store.backoffLevel}/${TBLG.BACKOFF_MS.length})`);
  setTimeout(() => location.reload(), wait);
}
function P_safeNorm(h) { try { return TBLG_P.normalizeUrl(h); } catch { return h; } }

function randDelay() {
  return Math.floor(Math.random() * (TBLG.MAX_DELAY_MS - TBLG.MIN_DELAY_MS)) + TBLG.MIN_DELAY_MS; // C-4: 하한 5초
}
function log(m) { console.log(`%c[Tabelog DFS] ${m}`, "color:#c9541f"); }
function notify(m) { try { alert("🍜 " + m); } catch (_) {} }

/* =====================================================================
 * 파일럿: 커버리지 감사 (v1.4, HANDOFF '다음 할 일 1')
 * 현재 노드의 자식(다음 한 단계)만 순차 fetch하여
 *   (1) Σ자식 건수 vs 부모 건수 (지역축은 서로소 → 검산 가능)
 *   (2) 자식 페이지들에서 셀렉터 일반화(카드/건수/뱃지 파싱 성공률)
 *   (3) 뱃지 클래스 변형 인벤토리
 * 를 JSON 리포트로 저장. 크롤 상태(storage)는 건드리지 않음(읽기 전용 파일럿).
 * 페이지 이동 없이 same-origin fetch + DOMParser 사용 — 파싱은 배포 코드
 * (TBLG_P) 그대로이므로 '테스트=배포' 원칙 유지. 요청 간 대기는 크롤과
 * 동일한 randDelay(5~8s) + 오류 시 30s 1회 재시도.
 * ===================================================================== */

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (!msg || msg.cmd !== "tblg_audit") return;
  if (window.__TBLG_AUDIT_RUNNING) { sendResponse({ ok: false, reason: "이미 감사가 실행 중입니다." }); return; }
  getState().then((s) => {
    if (s.isCrawling) { notify("크롤 진행 중에는 감사를 실행할 수 없습니다. 먼저 중지하세요."); return; }
    runCoverageAudit().catch((e) => {
      console.error(e);
      auditHud(null);
      window.__TBLG_AUDIT_RUNNING = false;
      notify("감사 실패: " + (e && e.message ? e.message : e));
    });
  });
  sendResponse({ ok: true });
});

async function runCoverageAudit() {
  const P = TBLG_P;
  window.__TBLG_AUDIT_RUNNING = true;
  const pageHref = location.href;
  const slug = P.reviewerSlugFromPath(location.pathname);
  if (!slug) { notify("리뷰어 방문 리스트 페이지에서 실행하세요."); window.__TBLG_AUDIT_RUNNING = false; return; }

  const parentCount = P.parseTotalCount(document);
  const det = P.harvestChildFilterLinksDetailed(document, pageHref);
  if (det.children.length === 0) {
    notify("이 노드에서 다음 단계 자식 링크를 찾지 못했습니다 (분할축 소진이거나 패널 미노출). 상위 노드에서 실행해 보세요.");
    window.__TBLG_AUDIT_RUNNING = false;
    return;
  }
  const MAX_CHILDREN = 40;                        // 파일럿 안전 상한
  const children = det.children.slice(0, MAX_CHILDREN);

  /* ── v1.4.1 사전 점검 (실측 2026-07-04: fetch가 s.tabelog.com/smartphone/으로 302되어
   *    cross-origin CORS 차단 → 전 자식 "Failed to fetch". 문서 내비게이션은 데스크톱 정상 수신.
   *    유력 원인: 탭의 모바일 UA(DevTools 디바이스 에뮬레이션) — fetch는 탭 UA를 그대로 쓰므로
   *    Tabelog 기기 라우팅이 SP로 보냄. 원인 확정 전이므로 가드는 원인 무관하게 동작.) ── */

  // (1) 모바일 UA면 30회 실패가 확정적이므로 시작 전 차단
  const uaMobile = /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent || "") ||
                   (navigator.userAgentData && navigator.userAgentData.mobile === true);
  if (uaMobile) {
    auditHud(null);
    window.__TBLG_AUDIT_RUNNING = false;
    notify("모바일 UA 감지 — DevTools 기기 에뮬레이션(Ctrl+Shift+M)이 켜져 있을 가능성이 큽니다.\n" +
           "이 상태에선 Tabelog가 요청을 스마트폰 사이트(s.tabelog.com)로 리다이렉트해 감사가 전부 실패합니다.\n" +
           "기기 툴바를 끄고 F5 후 다시 실행하세요.");
    return;
  }

  // (2) 프로브: 방금 내비게이션으로 성공한 '부모 URL 자체'를 fetch로 재요청해 경로 동등성 확인.
  //     실패하면 30회 낭비 없이 즉시 중단하고 원인 후보를 안내.
  // v1.4.2: 부모를 3중 측정으로 확장. 실측(2026-07-04)에서 라이브 DOM(베어 URL 내비게이션)=9399,
  //     정규화 fetch(고정 파라미터 부착)=9465로 불일치 관측 — 원인(장식 파라미터 영향 vs DOM/캐시
  //     스테일) 미확정. 자식 건수는 전부 '정규화 우주'에서 측정되므로 Δ는 count_fetch(정규화)
  //     기준으로 계산해야 동일 조건 비교가 된다. 베어 fetch를 1회 추가해 파라미터 효과를
  //     노드마다 자동 기록(param_delta = 정규화 - 베어). ⑤(07-02)에선 둘이 일치(9399)했음.
  auditHud("🍜 사전 점검: fetch 경로 확인 중…");
  await sleep(randDelay());
  let countFetchNorm = null, countFetchBare = null;
  try {
    const probe = await fetchDoc(P.normalizeUrl(pageHref));
    countFetchNorm = P.parseTotalCount(probe.doc);
    if (!probe.ok || countFetchNorm === null) throw new Error(`probe HTTP ${probe.status}, count=${countFetchNorm}`);
    log(`사전 점검 통과: 정규화 URL fetch → 全${countFetchNorm}件 (redirected=${probe.redirected}) / 라이브 DOM=${parentCount}`);
  } catch (e) {
    auditHud(null);
    window.__TBLG_AUDIT_RUNNING = false;
    const kind = (e instanceof TypeError) ? "네트워크 계층에서 차단됨(교차 출처 리다이렉트/CORS 추정)" : String(e && e.message || e);
    notify("사전 점검 실패 — 이 환경에서 fetch가 문서 내비게이션과 다르게 처리됩니다.\n" +
           `원인: ${kind}\n` +
           "① 콘솔에서 navigator.userAgent 가 데스크톱인지 확인(기기 에뮬레이션 OFF → F5)\n" +
           "② 데스크톱 UA인데도 재발하면 콘솔 로그를 공유해 주세요 — 내비게이션 기반 감사로 전환합니다.");
    return;
  }
  try {                                            // 베어 프로브(의미 파라미터만): 실패해도 감사는 계속
    await sleep(randDelay());
    const bare = await fetchDoc(bareUrl(pageHref));
    countFetchBare = P.parseTotalCount(bare.doc);
    log(`베어 URL fetch → 全${countFetchBare}件 (파라미터 효과 = ${countFetchNorm - countFetchBare})`);
  } catch (e) { log(`베어 프로브 실패(감사는 계속): ${e && e.message ? e.message : e}`); }

  // 패널의 링크 없는(nolink) 항목 — 자식으로 수확 불가한 영역의 존재 증거(예: 伊豆諸島・小笠原)
  const unlinked = [...document.querySelectorAll(".list-balloon .list-balloon__item-nolink")]
    .map((el) => (el.textContent || "").replace(/\s+/g, " ").trim()).filter(Boolean);

  const estMin = Math.ceil((children.length + 2) * (TBLG.MIN_DELAY_MS + TBLG.MAX_DELAY_MS) / 2 / 60000);
  log(`감사 시작: 부모 ${parentCount}건(DOM)/${countFetchNorm}건(fetch), 자식 ${children.length}개 (${det.axis}:${det.key}), 예상 ~${estMin}분`);

  const rows = [];
  const badgeVariants = {};                        // 뱃지 수식어 클래스 → {count, sample}
  for (let i = 0; i < children.length; i++) {
    const c = children[i];
    auditHud(`🍜 커버리지 감사 ${i + 1}/${children.length}\n${c.text}\n(탭을 닫거나 이동하면 중단됩니다)`);
    await sleep(randDelay());                      // 첫 요청 포함 매 요청 전 대기 (C-4)
    const row = { label: c.text, value: c.value, url: c.url,
                  http: null, count: null, cards: null, mode: null,
                  badges: 0, hasNext: null, nulls: {}, redirected: false, error: null };
    try {
      let r;
      try {
        r = await fetchDoc(c.url);
      } catch (e1) {                               // v1.4.1: 예외도 1회 재시도(일시 오류 대비).
        if (/오프사이트/.test(String(e1))) throw e1; // 단, 구조적 실패(호스트 이탈)는 재시도 무의미
        log(`  ⚠ ${c.text}: ${e1.message} → ${TBLG.BACKOFF_MS[0] / 1000}s 후 재시도`);
        await sleep(TBLG.BACKOFF_MS[0]);
        r = await fetchDoc(c.url);
      }
      row.http = r.status;
      row.redirected = r.redirected;
      if (r.redirected) row.final_url = r.finalUrl; // 리다이렉트 흔적은 리포트에 보존
      if (!r.ok || P.isErrorPage(r.doc)) {         // 1회 재시도 (백오프 1단계)
        log(`  ⚠ ${c.text}: HTTP ${r.status}/오류 페이지 → ${TBLG.BACKOFF_MS[0] / 1000}s 후 재시도`);
        await sleep(TBLG.BACKOFF_MS[0]);
        r = await fetchDoc(c.url);
        row.http = r.status;
      }
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      row.count = P.parseTotalCount(r.doc);
      const hv = P.harvestRestaurants(r.doc, c.url);
      row.cards = hv.records.length;
      row.mode = hv.mode;
      for (const f of ["tabelog_rating", "reviewer_rating", "visited_month", "review_url"])
        row.nulls[f] = hv.records.filter((x) => x[f] === null).length;
      row.badges = hv.records.reduce((n, x) => n + x.awards.length, 0);
      row.hasNext = !!r.doc.querySelector('a[rel="next"]');
      for (const s of r.doc.querySelectorAll(".simple-rvw--rstdata .simple-rvw__award-badge [class*='c-badge']")) {
        const mod = [...s.classList].find((cl) => /--20\d{2}/.test(cl)) || s.className;
        if (!badgeVariants[mod]) badgeVariants[mod] = { count: 0, sample: (s.textContent || "").replace(/\s+/g, " ").trim() };
        badgeVariants[mod].count++;
      }
      log(`  [${i + 1}/${children.length}] ${c.text}: 全${row.count}件, 카드 ${row.cards}(${row.mode}), 뱃지 ${row.badges}`);
    } catch (e) {
      row.error = String(e && e.message ? e.message : e);
      log(`  ❌ ${c.text}: ${row.error}`);
    }
    rows.push(row);
  }

  const known = rows.filter((r) => Number.isFinite(r.count));
  const childSum = known.reduce((a, r) => a + r.count, 0);
  const report = {
    meta: {
      kind: "coverage_audit",
      at: new Date().toISOString(),
      extension_version: chrome.runtime.getManifest().version,
      reviewer: slug,
      parent_url: P.normalizeUrl(pageHref)
    },
    parent: {
      count_dom: parentCount,                       // 라이브 DOM(사용자가 내비게이션으로 연 페이지) 건수
      count_fetch: countFetchNorm,                  // 정규화 URL fetch 건수 — 자식과 같은 우주(Δ의 기준)
      count_fetch_bare: countFetchBare,             // 베어 URL fetch 건수 — 파라미터 효과 관측용
      param_delta: (countFetchNorm !== null && countFetchBare !== null) ? countFetchNorm - countFetchBare : null,
      axis: det.axis, key: det.key,
      children_found: det.children.length, children_audited: children.length,
      unlinked_children: unlinked                   // 패널에 있으나 링크가 없어 수확 불가한 항목(커버리지 사각)
    },
    children: rows,
    sums: {
      child_sum: childSum,
      parsed_children: known.length,
      failed_children: rows.length - known.length,
      // Δ는 부모·자식이 같은 조건(정규화 URL fetch)일 때만 의미 → count_fetch 기준
      delta: (countFetchNorm ?? parentCount ?? 0) - childSum,
      delta_pct: countFetchNorm ? +((100 * (countFetchNorm - childSum)) / countFetchNorm).toFixed(3) : null,
      delta_vs_dom: (parentCount ?? 0) - childSum   // 참고용(교차 우주 비교 — 해석 주의)
    },
    selector_flags: {
      link_fallback_children: rows.filter((r) => r.mode === "link-fallback").map((r) => r.value),
      zero_cards_with_count: rows.filter((r) => r.cards === 0 && r.count > 0).map((r) => r.value),
      rating_nulls_total: rows.reduce((a, r) => a + (r.nulls.tabelog_rating || 0), 0),
      my_rating_nulls_total: rows.reduce((a, r) => a + (r.nulls.reviewer_rating || 0), 0)
    },
    badge_variants: badgeVariants
  };

  console.log("[Tabelog DFS] 커버리지 감사 리포트", report);
  try { console.table(rows.map((r) => ({ 지역: r.label, 건수: r.count, 카드: r.cards, 뱃지: r.badges, 오류: r.error || "" }))); } catch (_) {}
  downloadJson(report, `tabelog_audit_${slug}_${det.key}_${Date.now()}.json`);
  auditHud(null);
  window.__TBLG_AUDIT_RUNNING = false;
  notify(`감사 완료\n부모: DOM ${parentCount} / fetch ${countFetchNorm}${countFetchBare !== null ? ` (베어 ${countFetchBare})` : ""}\n` +
         `자식합 ${childSum} → Δ(동일조건) = ${report.sums.delta}` +
         (report.sums.failed_children ? `, 실패 ${report.sums.failed_children}개` : "") +
         (unlinked.length ? `\n링크 없는 항목: ${unlinked.join(", ")}` : "") +
         `\nJSON 리포트가 다운로드되었습니다.`);
}

// 베어 URL(의미 파라미터만, 고정/장식 파라미터 없음) — 파라미터 효과 관측용 (v1.4.2)
function bareUrl(href) {
  const u = new URL(href);
  const m = TBLG_P.meaningfulFilters(href, /*includePG*/ true);
  const q = new URLSearchParams();
  for (const [k, v] of m) q.set(k, v);
  let p = u.pathname.replace(/\/+$/, "/");
  if (!p.endsWith("/")) p += "/";
  const qs = q.toString();
  return `${u.origin}${p}${qs ? "?" + qs : ""}`;
}

async function fetchDoc(url) {
  // v1.4.1 주의: 교차 출처 리다이렉트(예: → s.tabelog.com)는 CORS로 fetch 자체가
  // TypeError를 던지므로 여기 도달하지 못함(호출부에서 분류). 아래 호스트 검증은
  // '동일 출처로 끝나되 경로가 바뀐' 리다이렉트를 잡는 보조 가드.
  const res = await fetch(url, {
    credentials: "same-origin",
    redirect: "follow",
    headers: { "Accept": "text/html,application/xhtml+xml" }  // 문서 요청임을 명시(협상 정렬)
  });
  const finalHost = (() => { try { return new URL(res.url).hostname; } catch (_) { return null; } })();
  if (finalHost !== "tabelog.com") {
    throw new Error(`오프사이트 리다이렉트: ${res.url}`);      // 실측: SP 라우팅 시 s.tabelog.com/smartphone/…
  }
  const html = await res.text();
  return { status: res.status, ok: res.ok, redirected: res.redirected, finalUrl: res.url,
           doc: new DOMParser().parseFromString(html, "text/html") };
}
function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }
function downloadJson(obj, name) {
  const blob = new Blob([JSON.stringify(obj, null, 2)], { type: "application/json" });
  const u = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = u; a.download = name;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(u), 5000);
}
function auditHud(text) {
  let el = document.getElementById("__tblg_audit_hud");
  if (text === null) { if (el) el.remove(); return; }
  if (!el) {
    el = document.createElement("div");
    el.id = "__tblg_audit_hud";
    el.style.cssText = "position:fixed;z-index:2147483647;right:12px;bottom:12px;background:#1c1a17;color:#fff;" +
      "font:12px/1.5 -apple-system,sans-serif;padding:10px 14px;border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,.35);" +
      "max-width:340px;white-space:pre-line";
    document.body.appendChild(el);
  }
  el.textContent = text;
}
