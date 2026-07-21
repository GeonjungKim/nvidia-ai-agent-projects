/* popup.js — UI 제어 (v1.4)
 * 상태 표시 + 리뷰어 큐/루트 URL 시딩 + 스코프 크롤(파일럿) + 커버리지 감사 트리거 + JSON export
 * v1.4 변경:
 *  - 시작 노드 URL(선택): 특정 노드를 루트로 서브트리만 순회(파일럿/부분 재수집용).
 *    엄격 자식 규칙이 현재 노드의 의미 파라미터를 전부 보존하므로,
 *    서브트리 밖으로 나가지 않음은 규칙의 따름정리(parsers.js collectChildLinks 참조).
 *  - 커버리지 감사 버튼: 현재 탭 content script에 tblg_audit 메시지 전송(읽기 전용, 상태 불변).
 *  - rootUrlFor 중복 제거 → TBLG_P.buildRootUrl 단일 정의 사용(popup.html에서 parsers.js 로드).
 *  - 시작 시 기존 레코드가 있으면 confirm으로 초기화 경고.
 *  - export/헤더 버전을 manifest에서 동적으로 읽음(하드코딩 제거). */

const $ = (id) => document.getElementById(id);
const VER = chrome.runtime.getManifest().version;

function refresh() {
  chrome.storage.local.get(
    ["isCrawling", "records", "seen", "stack", "losses", "reviewerQueue", "currentReviewer"],
    (r) => {
      const running = !!r.isCrawling;
      $("n-records").textContent = (r.records || []).length;
      $("n-stack").textContent = (r.stack || []).length;
      $("n-seen").textContent = (r.seen || []).length;
      $("n-loss").textContent = (r.losses || []).length;
      $("cur-reviewer").textContent = r.currentReviewer || "—";

      const st = $("state");
      if (running) { st.textContent = "🔄 수집 중"; st.className = "badge run"; }
      else if ((r.records || []).length) { st.textContent = "완료/대기"; st.className = "badge"; }
      else { st.textContent = "대기 중"; st.className = "badge"; }

      $("start").disabled = running;
      $("stop").disabled = !running;
      $("audit").disabled = running;   // 크롤 중 감사 금지 (content.js에서도 이중 차단)
      $("warn").style.display = (r.records || []).length > TBLG.EXPORT_REMINDER_AT ? "block" : "none";

      if (!$("reviewers").value && r.currentReviewer) $("reviewers").value = r.currentReviewer;
    }
  );
}

$("start").addEventListener("click", () => {
  const startUrl = ($("start-url").value || "").trim();
  const slugs = $("reviewers").value.split(",").map(s => s.trim()).filter(Boolean);

  let first, queue, firstUrl;
  if (startUrl) {
    // ── 스코프 크롤(파일럿): 지정 노드를 루트로 그 서브트리만 순회 ──
    let u;
    try { u = new URL(startUrl); } catch (_) { alert("시작 노드 URL 형식이 올바르지 않습니다."); return; }
    const slug = TBLG_P.reviewerSlugFromPath(u.pathname);
    if (u.hostname !== "tabelog.com" || !slug) {
      alert("시작 노드 URL은 https://tabelog.com/rvwr/{슬러그}/visited_restaurants/list/... 형식이어야 합니다.");
      return;
    }
    first = slug;
    queue = [];                                 // 스코프 크롤은 단일 서브트리만 (큐 무시)
    firstUrl = TBLG_P.normalizeUrl(startUrl);   // PG/장식 제거 + 고정 파라미터 부착
  } else {
    if (slugs.length === 0) { alert("리뷰어 슬러그를 최소 1개 입력하세요 (예: maro)"); return; }
    first = slugs.shift();
    queue = slugs;                              // 다음 리뷰어들 (FR-01b)
    firstUrl = TBLG_P.buildRootUrl(first);
  }

  chrome.storage.local.get(["records", "losses", "expected", "failures"], (prev) => {
    const n = (prev.records || []).length;
    const keep = $("keep-records") && $("keep-records").checked;
    if (!keep && n > 0 && !confirm(`기존 수집 레코드 ${n}건이 초기화됩니다. 계속할까요?\n(보존하려면 취소 후 ⭳ JSON으로 내보내거나 '기존 레코드 유지'를 체크하세요)`)) return;

    // v1.4.2b 증분 병합 모드: 부족분 재수집용. records 등은 보존하고 seen/stack만 리셋해
    // 재방문을 허용한다. 동일 식당은 content.js mergeRecords가 reviewer_id::restaurant_id
    // 키로 병합(null 필드만 보강)하므로 중복이 생기지 않는다.
    // 주의: 보존된 expected는 재방문 노드에서 최신 값으로 덮어써지고, losses는 손실 노드를
    // 다시 방문하면 항목이 중복 기록될 수 있다(집계 시 node 기준 dedup 권장).
    const base = keep
      ? { records: prev.records || [], losses: prev.losses || [], expected: prev.expected || {}, failures: prev.failures || [] }
      : { records: [], losses: [], expected: {}, failures: [] };

    chrome.storage.local.set({
      isCrawling: true,
      seen: [], stack: [],
      backoffLevel: 0,
      reviewerQueue: queue,
      currentReviewer: first,
      ...base
    }, () => {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.tabs.update(tabs[0].id, { url: firstUrl });
        window.close();
      });
    });
  });
});

$("stop").addEventListener("click", () => {
  chrome.storage.local.set({ isCrawling: false }, refresh);
});

/* 커버리지 감사(파일럿): 현재 탭의 리스트 페이지에서 자식 한 단계 건수 검산.
 * 실제 실행·레이트리밋·리포트 생성은 content.js runCoverageAudit 담당. */
$("audit").addEventListener("click", () => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const t = tabs[0];
    if (!t || !/tabelog\.com\/rvwr\/[^/]+\/visited_restaurants\/list/.test(t.url || "")) {
      alert("리뷰어 방문 리스트 페이지를 연 탭에서 실행하세요.\n예: https://tabelog.com/rvwr/maro/visited_restaurants/list/?pal=tokyo");
      return;
    }
    chrome.tabs.sendMessage(t.id, { cmd: "tblg_audit" }, (res) => {
      if (chrome.runtime.lastError) {
        alert("content script 응답 없음 — 페이지를 새로고침(F5)한 뒤 다시 시도하세요.\n" + chrome.runtime.lastError.message);
        return;
      }
      if (res && res.ok === false) { alert(res.reason || "감사를 시작할 수 없습니다."); return; }
      window.close();   // 진행 상황은 페이지 우하단 HUD + 콘솔, 완료 시 JSON 자동 다운로드
    });
  });
});

$("download").addEventListener("click", () => {
  chrome.storage.local.get(["records", "losses", "currentReviewer", "expected", "failures"], (r) => {
    const records = r.records || [];
    if (records.length === 0) { alert("다운로드할 데이터가 없습니다."); return; }
    const payload = {
      meta: {
        collected_at: new Date().toISOString(),
        extension_version: VER,
        reviewer: r.currentReviewer || null,
        record_count: records.length,
        losses: r.losses || [],           // 손실 노드(1,200 초과 & 분할축 소진)
        failures: r.failures || [],        // 반복 실패 URL
        expected: r.expected || {}          // 노드별 기대 건수(커버리지 감사)
      },
      records
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `tabelog_${r.currentReviewer || "data"}_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const v = $("ver"); if (v) v.textContent = `v${VER} · tree-DFS`;
  refresh();
});
setInterval(refresh, 1500);   // 라이브 갱신
