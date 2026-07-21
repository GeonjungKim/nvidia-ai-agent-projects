// test_logic_v14.mjs — v1.4 로직 단위 테스트 (픽스처 불필요, jsdom은 합성 DOM에만 사용)
import { JSDOM } from "jsdom";
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const P = require("./parsers.js");
const CFG = require("./config.js");

let pass = 0, fail = 0;
function T(name, cond, detail = "") {
  if (cond) { pass++; console.log(`  ✅ ${name}`); }
  else { fail++; console.log(`  ❌ ${name}  ${detail}`); }
}
const q = (href) => new URL(href).searchParams;

console.log("\n[L1] normalizeUrl");
{
  const raw = "https://tabelog.com/rvwr/maro/visited_restaurants/list?pal=tokyo&my_site_uri=maro&award_year=2026&PG=3&LstPrf=A1307";
  const n = P.normalizeUrl(raw);
  const s = q(n);
  T("의미 파라미터 보존 (pal, LstPrf, PG)", s.get("pal") === "tokyo" && s.get("LstPrf") === "A1307" && s.get("PG") === "3");
  T("장식 파라미터 제거 (my_site_uri, award_year)", !s.has("my_site_uri") && !s.has("award_year"));
  T("고정 파라미터 부착 (Srt=D, SrtT=mfav, bookmark_type=1, review_content_exist=0)",
    s.get("Srt") === "D" && s.get("SrtT") === "mfav" && s.get("bookmark_type") === "1" && s.get("review_content_exist") === "0");
  T("경로 끝 슬래시 보정", new URL(n).pathname.endsWith("/list/"));
  T("멱등성 normalize(normalize(x)) == normalize(x)", P.normalizeUrl(n) === n);
  const a = P.normalizeUrl("https://tabelog.com/rvwr/maro/visited_restaurants/list/?LstPrf=A1307&pal=tokyo");
  const b = P.normalizeUrl("https://tabelog.com/rvwr/maro/visited_restaurants/list/?pal=tokyo&LstPrf=A1307&SrtT=mfav");
  T("파라미터 순서·장식 무관 동일 키", a === b, `\n      a=${a}\n      b=${b}`);
}

console.log("\n[L2] meaningfulFilters");
{
  const href = "https://tabelog.com/rvwr/maro/visited_restaurants/list/?pal=tokyo&PG=4&SrtT=mfav";
  const m1 = P.meaningfulFilters(href);
  const m2 = P.meaningfulFilters(href, true);
  T("기본: PG 제외, 장식 제외", m1.size === 1 && m1.get("pal") === "tokyo");
  T("includePG=true: PG 포함", m2.size === 2 && m2.get("PG") === "4");
}

console.log("\n[L3] buildPageUrls (60페이지 캡 = SPLIT_THRESHOLD 1200/20)");
{
  const base = "https://tabelog.com/rvwr/maro/visited_restaurants/list/?pal=tokyo";
  const u100 = P.buildPageUrls(base, 100);
  T("100페이지 요청 → 59개(PG=2..60)로 캡", u100.length === 59, `got=${u100.length}`);
  T("첫 URL PG=2, 마지막 PG=60", q(u100[0]).get("PG") === "2" && q(u100[58]).get("PG") === "60");
  const u3 = P.buildPageUrls(base, 3);
  T("3페이지 → PG=2,3 (2개)", u3.length === 2 && q(u3[1]).get("PG") === "3");
  T("전부 정규화(고정 파라미터 부착)", u100.every(u => q(u).get("Srt") === "D"));
}

console.log("\n[L4] buildRootUrl / reviewerSlugFromPath / cleanRestaurantUrl / urlSegments / sourceNodeLabel");
{
  const r = P.buildRootUrl("maro");
  T("루트 URL 경로", r.startsWith("https://tabelog.com/rvwr/maro/visited_restaurants/list/?"));
  T("루트 URL 고정 파라미터", q(r).get("SrtT") === "mfav" && q(r).get("bookmark_type") === "1");
  T("슬러그 추출", P.reviewerSlugFromPath("/rvwr/maro/visited_restaurants/list/") === "maro");
  T("슬러그 아님 → null", P.reviewerSlugFromPath("/tokyo/A1307/A130704/13299970/") === null);
  T("식당 URL 정리(쿼리·해시 제거)",
    P.cleanRestaurantUrl("https://tabelog.com/tokyo/A1307/A130704/13299970/?ref=x#top") === "https://tabelog.com/tokyo/A1307/A130704/13299970/");
  const seg = P.urlSegments("https://tabelog.com/tokyo/A1307/A130704/13299970/");
  T("세그먼트 분해", seg.pref === "tokyo" && seg.area2 === "A1307" && seg.area3 === "A130704" && seg.restaurantId === "13299970");
  T("sourceNodeLabel root", P.sourceNodeLabel("https://tabelog.com/rvwr/maro/visited_restaurants/list/?SrtT=mfav") === "root");
  T("sourceNodeLabel 필터+PG 포함", P.sourceNodeLabel("https://tabelog.com/rvwr/maro/visited_restaurants/list/?pal=tokyo&PG=2") === "pal=tokyo&PG=2");
}

console.log("\n[L5] regionDepth / genreDepth");
{
  const mk = (o) => new Map(Object.entries(o));
  T("region: {}=0, {pal}=1, {pal,LstPrf}=2, {…LstAre}=3",
    P.regionDepth(mk({})) === 0 && P.regionDepth(mk({ pal: "t" })) === 1 &&
    P.regionDepth(mk({ pal: "t", LstPrf: "A" })) === 2 && P.regionDepth(mk({ pal: "t", LstPrf: "A", LstAre: "B" })) === 3);
  T("genre: {Cat}=1, {Cat,LstCat}=2, {…LstCatD}=3, {genre_name}=3(말단 취급)",
    P.genreDepth(mk({ Cat: "RC" })) === 1 && P.genreDepth(mk({ Cat: "RC", LstCat: "x" })) === 2 &&
    P.genreDepth(mk({ Cat: "RC", LstCat: "x", LstCatD: "y" })) === 3 && P.genreDepth(mk({ genre_name: "ramen" })) === 3);
}

console.log("\n[L6] 엄격 자식 규칙 (합성 패널) — 스코프 격리의 근거");
{
  const PAGE = "https://tabelog.com/rvwr/maro/visited_restaurants/list/?pal=tokyo";
  const html = `<body><div class="list-balloon">
    <a href="/rvwr/maro/visited_restaurants/list/?pal=tokyo&LstPrf=A1301">銀座OK</a>
    <a href="/rvwr/maro/visited_restaurants/list/?pal=tokyo&LstPrf=A1302&LstAre=A130201">2키 건너뛰기</a>
    <a href="/rvwr/maro/visited_restaurants/list/?LstPrf=A1303">pal 소실</a>
    <a href="/rvwr/maro/visited_restaurants/list/?pal=osaka&LstPrf=A2701">pal 변조</a>
    <a class="list-balloon__breadcrumb" href="/rvwr/maro/visited_restaurants/list/?pal=atw">브레드크럼</a>
    <a href="https://s.tabelog.com/rvwr/maro/visited_restaurants/list/?pal=tokyo&LstPrf=A1304">모바일 호스트</a>
    <a href="/rvwr/maro/visited_restaurants/list/?pal=tokyo&PG=2">PG 링크</a>
    <a href="/rvwr/other/visited_restaurants/list/?pal=tokyo&LstPrf=A1305">타 리뷰어</a>
    <a href="/rvwr/maro/visited_restaurants/list/?pal=tokyo&Cat=RC">기대키 불일치(Cat)</a>
    <a href="/rvwr/maro/visited_restaurants/list/?pal=tokyo&LstPrf=A1301&SrtT=rvcn">중복(장식만 상이)</a>
  </div></body>`;
  const doc = new JSDOM(html, { url: PAGE }).window.document;
  const det = P.collectChildLinksDetailed(doc, PAGE, "LstPrf");
  T("10개 앵커 중 정확히 1개만 수용 (중복은 정규화로 합침)", det.length === 1, `got=${det.length}: ${JSON.stringify(det)}`);
  T("수용된 자식 = A1301, 라벨 보존", det[0]?.value === "A1301" && det[0]?.text === "銀座OK");
  T("문자열 API 일치", JSON.stringify(P.collectChildLinks(doc, PAGE, "LstPrf")) === JSON.stringify(det.map(c => c.url)));
  const g = P.collectChildLinksDetailed(doc, PAGE, "Cat");
  T("기대키 Cat일 땐 Cat 링크만 수용", g.length === 1 && g[0].value === "RC");
}

console.log("\n[L7] parseAwards — 구조 파싱 + 안전망 폴백");
{
  const mk = (inner) => new JSDOM(`<div class="simple-rvw simple-rvw--rstdata">${inner}</div>`).window.document.querySelector(".simple-rvw--rstdata");
  const badge = (cls, label) =>
    `<div class="simple-rvw__award-badge rvwr-award-badge"><span class="${cls}"><i>${label}</i></span>
     <div class="rvwr-award-badge__tooltip-wrap"><div class="c-tooltip"><p>tooltip ${label}</p></div></div></div>`;

  const a1 = P.parseAwards(mk(badge("c-badge-award c-badge-award--square c-badge-award--2026gold", "2026年Gold受賞店")));
  T("award gold", a1.length === 1 && a1[0].type === "tabelog_award" && a1[0].year === 2026 && a1[0].rank === "gold" && a1[0].label === "2026年Gold受賞店", JSON.stringify(a1));

  const a2 = P.parseAwards(mk(badge("c-badge-hyakumeiten c-badge-hyakumeiten--square c-badge-hyakumeiten--2025sushi", "寿司 TOKYO 百名店 2025 選出店")));
  T("hyakumeiten 카테고리·연도 기계판독 + 라벨 보존", a2[0].type === "hyakumeiten" && a2[0].year === 2025 && a2[0].category === "sushi" && /TOKYO/.test(a2[0].label), JSON.stringify(a2));

  const a3 = P.parseAwards(mk(badge("c-badge-hot-restaurant c-badge-hot-restaurant--square c-badge-hot-restaurant--2026", "食べログ ホットレストラン 2026 受賞店")));
  T("hot_restaurant (v1.3에서 전량 누락되던 유형)", a3[0].type === "hot_restaurant" && a3[0].year === 2026, JSON.stringify(a3));

  const a4 = P.parseAwards(mk(badge("c-badge-newthing c-badge-newthing--2027mystery", "謎の新バッジ 2027")));
  T("미지 뱃지 → unknown으로 보존(스키마 방어)", a4[0].type === "unknown" && a4[0].year === 2027 && /c-badge-newthing/.test(a4[0].cls), JSON.stringify(a4));

  const a5 = P.parseAwards(mk(badge("c-badge-award c-badge-award--2026silver", "2026年Silver受賞店") + badge("c-badge-hyakumeiten c-badge-hyakumeiten--2025french", "フレンチ TOKYO 百名店 2025 選出店")));
  T("복수 뱃지 전부 수집", a5.length === 2 && a5[0].rank === "silver" && a5[1].category === "french");

  const a6 = P.parseAwards(mk(`<p>The Tabelog Award 2026 Gold 受賞店 / 百名店 2025 選出</p>`));
  T("구조 뱃지 0개 → 텍스트 폴백 발동 (type=text_fallback ×2)",
    a6.length === 2 && a6.every(x => x.type === "text_fallback") && a6[0].rank === "gold" && a6[1].label === "百名店2025", JSON.stringify(a6));

  const a7 = P.parseAwards(mk(`<p>수상 없음 일반 카드</p>`));
  T("무수상 카드 → []", Array.isArray(a7) && a7.length === 0);

  const a8 = P.parseAwards(mk(badge("c-badge-award c-badge-award--2026bronze", "2026年Bronze受賞店") + `<p>본문에 우연히 百名店 2024 언급</p>`));
  T("구조 뱃지 존재 시 텍스트 폴백 미발동(이중계상 방지)", a8.length === 1 && a8[0].rank === "bronze", JSON.stringify(a8));
}

console.log(`\n[로직] ${pass} 통과 / ${fail} 실패`);
process.exit(fail ? 1 : 0);
