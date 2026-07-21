// test_dom_v14.mjs — v1.4 파서를 사용자 제공 실측 HTML(2026-07-02, pal=tokyo 페이지)에 실행
// 픽스처: fixtures_page.html(전체 페이지 ③), fixtures_card.html(단독 카드 ①)
import { JSDOM } from "jsdom";
import { readFileSync } from "fs";
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const P = require("./parsers.js");

const PAGE_URL = "https://tabelog.com/rvwr/maro/visited_restaurants/list/?pal=tokyo&SrtT=mfav&my_site_uri=maro";

let pass = 0, fail = 0;
function T(name, cond, detail = "") {
  if (cond) { pass++; console.log(`  ✅ ${name}`); }
  else { fail++; console.log(`  ❌ ${name}  ${detail}`); }
}

const doc = new JSDOM(readFileSync(new URL("./fixtures_page.html", import.meta.url), "utf-8"), { url: PAGE_URL }).window.document;

console.log("\n[D1] 페이지 레벨");
T("총 건수 = 9399 (⑤ 실측과 일치)", P.parseTotalCount(doc) === 9399, `got=${P.parseTotalCount(doc)}`);
T("isErrorPage = false", P.isErrorPage(doc) === false);
const nx = P.findNextPageFallback(doc);
T("rel=next 폴백 → PG=2 (④ 실측과 일치)", !!nx && /PG=2/.test(nx), `got=${nx}`);

console.log("\n[D2] 카드 수집 (v1.3 회귀 확인)");
const { records, mode } = P.harvestRestaurants(doc, PAGE_URL);
T("mode = card / 20건", mode === "card" && records.length === 20, `mode=${mode} n=${records.length}`);
T("표시명 maro-j", records[0]?.reviewer_display_name === "maro-j");
T("종합점 전부 존재·범위(2.0~5.0)", records.every(r => r.tabelog_rating !== null && r.tabelog_rating >= 2 && r.tabelog_rating <= 5));
T("개인점 전부 존재·범위(0.5~5.0)", records.every(r => r.reviewer_rating !== null && r.reviewer_rating >= 0.5 && r.reviewer_rating <= 5));
T("review_url 전부 rvwdtl (visitdtl 0건 — robots 구획 준수)", records.every(r => r.review_url && /\/rvwdtl\//.test(r.review_url) && !/\/visitdtl\//.test(r.review_url)));
T("url 전부 표준형 /{pref}/A####/A######/{id}/ (쿼리·해시 제거)", records.every(r => /tabelog\.com\/[a-z]+\/A\d{4}\/A\d{6}\/\d+\/$/.test(r.url)));
T("개인점 요소는 정확히 24개, 전부 .p-preview-visit 스코프 내 (48은 grep 부분문자열 중복이었음)",
  doc.querySelectorAll(".c-rating-v2__val").length === 24 && doc.querySelectorAll(".p-preview-visit .c-rating-v2__val").length === 24);

console.log("\n[D3] 수상 뱃지 v1.4 — 실측 36개 전수 대조");
const allAwards = records.flatMap(r => r.awards);
T("awards 합계 = 36 (v1.3은 35, hot_restaurant 1건 누락이었음)", allAwards.length === 36, `got=${allAwards.length}`);
const cnt = (f) => allAwards.filter(f).length;
T("The Tabelog Award 2026: gold 7 / silver 5 / bronze 6 (계 18)",
  cnt(a => a.type === "tabelog_award" && a.year === 2026 && a.rank === "gold") === 7 &&
  cnt(a => a.type === "tabelog_award" && a.rank === "silver") === 5 &&
  cnt(a => a.type === "tabelog_award" && a.rank === "bronze") === 6 &&
  cnt(a => a.type === "tabelog_award") === 18);
T("百名店 계 17 (sushi4·japanese3·creative_innovative3·french2·sukiyaki_shabushabu2·yakitori1·yakiniku1·spanish1)",
  cnt(a => a.type === "hyakumeiten") === 17 &&
  cnt(a => a.type === "hyakumeiten" && a.category === "sushi") === 4 &&
  cnt(a => a.type === "hyakumeiten" && a.category === "japanese") === 3 &&
  cnt(a => a.type === "hyakumeiten" && a.category === "creative_innovative") === 3 &&
  cnt(a => a.type === "hyakumeiten" && a.category === "french") === 2 &&
  cnt(a => a.type === "hyakumeiten" && a.category === "sukiyaki_shabushabu") === 2 &&
  cnt(a => a.type === "hyakumeiten" && a.category === "yakitori") === 1 &&
  cnt(a => a.type === "hyakumeiten" && a.category === "yakiniku") === 1 &&
  cnt(a => a.type === "hyakumeiten" && a.category === "spanish") === 1);
T("hot_restaurant 2026 ×1", cnt(a => a.type === "hot_restaurant" && a.year === 2026) === 1);
T("이 페이지에서 unknown/text_fallback 0건 (전 뱃지 구조 판독 성공)", cnt(a => a.type === "unknown" || a.type === "text_fallback") === 0);
T("전 뱃지 label 비어있지 않음", allAwards.every(a => typeof a.label === "string" && a.label.length > 0));
const yoro = records.find(r => r.name === "よろにく");
T("よろにく = 3뱃지 (bronze + 焼肉百名店 + hot) — v1.3 누락 카드",
  !!yoro && yoro.awards.length === 3 &&
  yoro.awards.some(a => a.type === "tabelog_award" && a.rank === "bronze") &&
  yoro.awards.some(a => a.type === "hyakumeiten" && a.category === "yakiniku") &&
  yoro.awards.some(a => a.type === "hot_restaurant"), JSON.stringify(yoro?.awards));
const badgeDivs = doc.querySelectorAll(".simple-rvw--rstdata .simple-rvw__award-badge").length;
T("파서 출력 = DOM 뱃지 div 수 (36)", allAwards.length === badgeDivs, `dom=${badgeDivs}`);

console.log("\n[D4] 자식 수확 — 지역축(LstPrf)");
const det = P.harvestChildFilterLinksDetailed(doc, PAGE_URL);
T("축 region / 키 LstPrf / 30개", det.axis === "region" && det.key === "LstPrf" && det.children.length === 30,
  JSON.stringify({ axis: det.axis, key: det.key, n: det.children.length }));
T("값 = A1301..A1330 전부 유일", new Set(det.children.map(c => c.value)).size === 30 && det.children.every(c => /^A13(0[1-9]|[12]\d|30)$/.test(c.value)));
T("라벨(지역명) 전부 비어있지 않음 — 감사 리포트 가독성", det.children.every(c => c.text.length > 0));
T("銀座・新橋・有楽町 = A1301 매핑 확인", det.children.some(c => c.value === "A1301" && /銀座/.test(c.text)));
T("전 링크 pal=tokyo 보존 + 고정 파라미터 + PG 없음",
  det.children.every(c => /pal=tokyo/.test(c.url) && /LstPrf=A13\d\d/.test(c.url) && /Srt=D/.test(c.url) && !/PG=/.test(c.url)));
const legacy = P.harvestChildFilterLinks(doc, PAGE_URL);
T("문자열 API(기존 content.js 경로) 결과 동일", legacy.axis === "region" && JSON.stringify(legacy.links) === JSON.stringify(det.children.map(c => c.url)));

console.log("\n[D5] 장르축 1단계 (미래 분기 대비 — ② 덤프에서 Cat 6종 확인됨)");
const cats = P.collectChildLinksDetailed(doc, PAGE_URL, "Cat");
T("Cat 자식 = 6종 유일 (RC/MC/SC/BC/YC/ZZ, BC 중복은 정규화로 합침)",
  cats.length === 6 && JSON.stringify(cats.map(c => c.value).sort()) === JSON.stringify(["BC", "MC", "RC", "SC", "YC", "ZZ"]),
  JSON.stringify(cats.map(c => c.value)));
T("Cat 링크 전부 LstCat/LstCatD 미포함 (1단계만)", cats.every(c => !/LstCat/.test(c.url)));

console.log("\n[D6] 단독 카드(① 무수상 카드) 전 필드");
const cardHtml = readFileSync(new URL("./fixtures_card.html", import.meta.url), "utf-8");
const card = new JSDOM(`<body>${cardHtml}</body>`, { url: PAGE_URL }).window.document.querySelector(".simple-rvw--rstdata");
const r = P.parseCard(card, PAGE_URL, { reviewerId: "maro", displayName: "maro-j", sourceNode: "pal=tokyo" });
T("식당명·ID·지역 세그먼트", r.name === "たかむら別邸やまじん" && r.restaurant_id === "13299970" && r.pref === "tokyo" && r.area2 === "A1307" && r.area3 === "A130704");
T("종합 4.06 / 개인 5.0 / 리뷰수 49", r.tabelog_rating === 4.06 && r.reviewer_rating === 5.0 && r.tabelog_review_count === 49);
T("예산 夜만 존재, 昼 null", r.budget_dinner === "￥40,000～￥49,999" && r.budget_lunch === null);
T("정휴 null('-') / 방문 2024/08·1回", r.closed_days === null && r.visited_month === "2024/08" && r.visit_count === 1);
T("review_url = rvwdtl/B490866169 / bookmark_id 일치", /\/rvwdtl\/B490866169\/$/.test(r.review_url || "") && r.bookmark_id === "490866169");
T("역 3·장르 1(日本料理)", r.stations.length === 3 && JSON.stringify(r.genres) === '["日本料理"]');
T("무수상 카드 awards = [] (폴백 오발동 없음)", Array.isArray(r.awards) && r.awards.length === 0);

console.log(`\n[DOM] ${pass} 통과 / ${fail} 실패`);
process.exit(fail ? 1 : 0);
