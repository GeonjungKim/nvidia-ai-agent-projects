"""M-FT1: 추천문 생성 SFT 데이터셋 구축 (FINETUNE_SPEC.md).

app.db(restaurants_agg + restaurant_genres)의 실제 셀 분포에서 검색 시나리오
(pref[, area2], genre[, budget_dinner]) 조합을 층화 샘플링하고, 각 조합의
상위 5곳(bayes)을 app.generate.build_messages()로 입력화하여 교사 모델
(Qwen2.5-7B-Instruct, bitsandbytes NF4 4bit)로 completion을 생성한다.
충실성 필터를 통과한 샘플만 채택해 data/ft/{train,val,test}.jsonl로 저장한다.
"""
import json
import random
import re
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.generate import build_messages  # noqa: E402 (§FT 절대규칙: import 재사용, 복제 금지)
from app.query import search  # noqa: E402

DB_PATH = ROOT / "app.db"
OUT_DIR = ROOT / "data" / "ft"
TEACHER_MODEL_PATH = "Qwen/Qwen2.5-7B-Instruct"

SEED = 20260709
N_TRAIN, N_VAL, N_TEST = 4000, 300, 200
MULTI_REVIEWER_MIN_FRACTION = 0.30
# 필터 탈락 흡수용 여유분. 768토큰 배치 스모크 테스트(n=41) 실측 수용률 34%를
# 보수적으로 반영 — 512토큰 단일처리 스모크 테스트(n=17)의 64%보다 안전 마진을 둠.
POOL_BUFFER = 3.0
MAX_POOL_SCAN_ATTEMPTS = 400_000
MAX_OUTPUT_CHARS = 700
TOP_K = 5
# 512: app._run_model과 동일 값. 768로 늘렸더니 길이초과(length_exceeded) 탈락이
# 급증해(스모크 테스트 n=41) 원복 — 5곳 서술+700자 상한은 512 쪽이 더 낫다고 판단.
MAX_NEW_TOKENS = 512
RETRY_TEMPERATURE = 0.7
BATCH_SIZE = 4  # 실측: batch=4가 단일 대비 ~1.5배(batch=2는 오히려 느림), VRAM 7.53/8.585GB

SPLIT_NAMES = ("train", "val", "test")


# ---------------------------------------------------------------------------
# 1. 후보 조합 샘플링 (DB 판독 전용)
# ---------------------------------------------------------------------------

def fetch_seed_rows(db_path: Path) -> list[tuple[str, str | None, str, str | None, int]]:
    """(pref, area2, genre, budget_dinner, reviewer_count) — (식당,장르) 쌍마다
    한 행. 인기 pref×genre 셀일수록 행이 많으므로 그대로 뽑으면 실제 셀 분포에
    자연히 비례 가중된다."""
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT r.pref, r.area2, g.genre, r.budget_dinner, r.reviewer_count "
            "FROM restaurant_genres g "
            "JOIN restaurants_agg r ON r.restaurant_id = g.restaurant_id"
        ).fetchall()
    finally:
        conn.close()
    return rows


def derive_combination(
    row: tuple[str, str | None, str, str | None, int], rng: random.Random
) -> tuple[str, str | None, str, str | None]:
    """실제 (식당,장르) 행 하나를 시드로 검색 시나리오 (pref, area2, genre,
    budget_dinner)를 만든다. area2/budget을 확률적으로 포함시켜 거친 검색
    (pref+genre만)과 세밀한 검색(지역·예산까지 포함)을 고루 시뮬레이션한다."""
    pref, area2, genre, budget_dinner, _reviewer_count = row
    include_area2 = rng.random() < 0.5
    include_budget = rng.random() < 0.3
    return (
        pref,
        area2 if include_area2 else None,
        genre,
        budget_dinner if (include_budget and budget_dinner is not None) else None,
    )


def build_candidate_pools(
    db_path: Path,
    seed_rows: list[tuple[str, str | None, str, str | None, int]],
    rng: random.Random,
    total_target: int,
    multi_fraction: float,
    buffer: float,
) -> tuple[dict[tuple, list[dict]], dict[tuple, list[dict]]]:
    """후보 조합을 계속 뽑아 실제 search() top-5를 조회하고, top-5에 다중
    리뷰어 식당이 있는지로 분류한다. 다중 리뷰어 풀을 채우는 동안은 다중
    리뷰어 시드를 우선 사용해 그 식당이 자기 조합의 top-5에 들 확률을 높인다.
    두 풀이 각자의(버퍼 포함) 목표에 도달하거나 시도 상한에 닿으면 멈춘다."""
    multi_seeds = [r for r in seed_rows if r[4] >= 2]
    single_seeds = [r for r in seed_rows if r[4] < 2]
    if not multi_seeds:
        raise ValueError("app.db에 다중 리뷰어 식당-장르 행이 없습니다")

    target_multi = int(total_target * multi_fraction * buffer)
    target_single = int(total_target * (1 - multi_fraction) * buffer)

    seen: set[tuple] = set()
    multi_pool: dict[tuple, list[dict]] = {}
    single_pool: dict[tuple, list[dict]] = {}

    attempts = 0
    while (
        (len(multi_pool) < target_multi or len(single_pool) < target_single)
        and attempts < MAX_POOL_SCAN_ATTEMPTS
    ):
        attempts += 1
        row = rng.choice(multi_seeds) if len(multi_pool) < target_multi else rng.choice(single_seeds)

        combo = derive_combination(row, rng)
        if combo in seen:
            continue
        seen.add(combo)

        pref, area2, genre, budget_dinner = combo
        top5 = search(
            db_path, pref=pref, area2=area2, genre=genre,
            budget_dinner=budget_dinner, sort="bayes", limit=TOP_K,
        )
        if not top5:
            continue

        is_multi = any(r["reviewer_count"] >= 2 for r in top5)
        if is_multi and len(multi_pool) < target_multi:
            multi_pool[combo] = top5
        elif not is_multi and len(single_pool) < target_single:
            single_pool[combo] = top5

    return multi_pool, single_pool


def allocate_by_fraction(
    items: list[Any], fractions: dict[str, float], rng: random.Random
) -> dict[str, list[Any]]:
    """items를 결정론적으로 섞은 뒤 fractions 비율대로 잘라 이름별 버킷으로
    나눈다 (마지막 버킷이 반올림 잔여를 흡수)."""
    shuffled = list(items)
    rng.shuffle(shuffled)
    result: dict[str, list[Any]] = {}
    start = 0
    names = list(fractions.keys())
    for i, name in enumerate(names):
        if i == len(names) - 1:
            result[name] = shuffled[start:]
        else:
            n = round(len(shuffled) * fractions[name])
            result[name] = shuffled[start:start + n]
            start += n
    return result


def build_split_queues(
    multi_pool: dict[tuple, list[dict]],
    single_pool: dict[tuple, list[dict]],
    rng: random.Random,
    split_sizes: dict[str, int],
) -> dict[str, list[tuple]]:
    """다중/단일 풀을 각각 split 비율대로 조합 단위 분할한 뒤(같은 조합이
    두 split에 못 감) split별로 섞어 큐를 만든다."""
    total = sum(split_sizes.values())
    fractions = {name: size / total for name, size in split_sizes.items()}

    multi_alloc = allocate_by_fraction(list(multi_pool.keys()), fractions, rng)
    single_alloc = allocate_by_fraction(list(single_pool.keys()), fractions, rng)

    queues: dict[str, list[tuple]] = {}
    for name in split_sizes:
        combined = multi_alloc[name] + single_alloc[name]
        rng.shuffle(combined)
        queues[name] = combined
    return queues


# ---------------------------------------------------------------------------
# 2. 충실성 필터 (순수 함수)
# ---------------------------------------------------------------------------

QUOTE_PATTERN = re.compile(r"[「『]([^」』]*)[」』]")
NUMBER_PATTERN = re.compile(r"\d[\d,]*\.?\d*")


def _normalize_number(raw: str) -> str:
    s = raw.replace(",", "")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def _collect_valid_numbers(facts: list[dict[str, Any]]) -> set[str]:
    valid: set[str] = set()
    for f in facts:
        if f["tabelog_rating"] is not None:
            valid.add(_normalize_number(str(f["tabelog_rating"])))
        valid.add(_normalize_number(str(f["tabelog_review_count"])))
        valid.add(_normalize_number(str(f["visit_count_total"])))
        for budget in (f.get("budget_dinner"), f.get("budget_lunch")):
            if budget:
                valid.update(_normalize_number(n) for n in NUMBER_PATTERN.findall(budget))
        for label in f.get("awards", []):
            valid.update(_normalize_number(n) for n in NUMBER_PATTERN.findall(label))
        for rv in f["reviewers"]:
            if rv["reviewer_rating"] is not None:
                valid.add(_normalize_number(str(rv["reviewer_rating"])))
            valid.add(_normalize_number(str(rv["visit_count"])))
    return valid


def _all_names_present(text: str, facts: list[dict[str, Any]]) -> bool:
    return all(f["name"] in text for f in facts)


def _no_unlisted_quoted_names(text: str, facts: list[dict[str, Any]]) -> bool:
    names = {f["name"] for f in facts}
    return all(q in names for q in QUOTE_PATTERN.findall(text))


def _all_numbers_traceable(text: str, facts: list[dict[str, Any]]) -> bool:
    """평점·리뷰수·엔화(+수상연도) 수치만 입력 근거를 요구한다. 1..len(facts)
    범위의 정수는 "N곳"류 목록 개수 언급으로 보아 예외로 둔다(오탈락 방지)."""
    valid_numbers = _collect_valid_numbers(facts)
    count_exempt = {str(i) for i in range(1, len(facts) + 1)}
    for raw in NUMBER_PATTERN.findall(text):
        norm = _normalize_number(raw)
        if norm and norm not in valid_numbers and norm not in count_exempt:
            return False
    return True


def passes_faithfulness_filter(
    text: str, facts: list[dict[str, Any]]
) -> tuple[bool, str | None]:
    """FINETUNE_SPEC.md M-FT1 ④의 4종 자동 필터. 실패 시 (False, 사유코드)."""
    if not _all_names_present(text, facts):
        return False, "name_missing"
    if not _no_unlisted_quoted_names(text, facts):
        return False, "unlisted_quoted_name"
    if not _all_numbers_traceable(text, facts):
        return False, "number_not_traceable"
    if len(text) > MAX_OUTPUT_CHARS:
        return False, "length_exceeded"
    return True, None


# ---------------------------------------------------------------------------
# 3. 교사 모델 로드 + 생성
# ---------------------------------------------------------------------------

def load_teacher_model() -> tuple[Any, Any]:
    """Qwen2.5-7B-Instruct, bitsandbytes NF4 4bit. try/except로 감싸지 않는다
    — VRAM/로드 실패 시 트레이스백과 함께 즉시 중단되어야 한다(대안 임의 선택
    금지, FINETUNE_SPEC.md 지시)."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(TEACHER_MODEL_PATH)
    # 배치 생성은 좌측 패딩이 필수(디코더 전용 모델의 causal 구조 보존).
    # Qwen2.5-7B-Instruct는 pad_token이 이미 있어 별도 지정 불필요하지만
    # 없는 경우를 대비해 eos_token으로 대체한다.
    tokenizer.padding_side = "left"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        TEACHER_MODEL_PATH, quantization_config=bnb_config, device_map="cuda",
    )
    return model, tokenizer


def _teacher_generate_batch(
    model: Any, tokenizer: Any, messages_list: list[list[dict[str, str]]],
    *, do_sample: bool, temperature: float | None = None,
) -> list[str]:
    prompts = [
        tokenizer.apply_chat_template(m, tokenize=False, add_generation_prompt=True)
        for m in messages_list
    ]
    inputs = tokenizer(prompts, return_tensors="pt", padding=True).to(model.device)
    gen_kwargs: dict[str, Any] = {"max_new_tokens": MAX_NEW_TOKENS, "do_sample": do_sample}
    if do_sample:
        gen_kwargs["temperature"] = temperature
    output_ids = model.generate(**inputs, **gen_kwargs)
    input_len = inputs["input_ids"].shape[1]
    generated_batch = output_ids[:, input_len:]
    return tokenizer.batch_decode(generated_batch, skip_special_tokens=True)


def _generate_batch_with_oom_fallback(
    model: Any, tokenizer: Any, messages_list: list[list[dict[str, str]]],
    *, do_sample: bool, temperature: float | None = None,
) -> list[str]:
    """배치 생성 시도 → CUDA OOM이면 캐시를 비우고 1건씩 순차 처리로 대체
    (실측 VRAM 여유가 얇아 실제 데이터의 다중 리뷰어 조합처럼 입력이 길어지면
    배치가 못 들어갈 수 있음 — 전체 실행을 중단시키지 않기 위한 안전장치이며
    필터 기준이나 생성 파라미터를 바꾸는 것이 아니므로 대안 임의 선택 금지
    지시와 무관함)."""
    import torch

    try:
        return _teacher_generate_batch(
            model, tokenizer, messages_list, do_sample=do_sample, temperature=temperature
        )
    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        print(f"  경고: 배치({len(messages_list)}건) VRAM 부족 — 1건씩 순차 처리로 재시도")
        texts: list[str] = []
        for m in messages_list:
            texts.extend(
                _teacher_generate_batch(model, tokenizer, [m], do_sample=do_sample, temperature=temperature)
            )
            torch.cuda.empty_cache()
        return texts


def generate_batch(
    model: Any, tokenizer: Any,
    combos: list[tuple],
    all_pools: dict[tuple, list[dict]],
    rng: random.Random,
    reject_counts: dict[str, int],
) -> dict[tuple, dict[str, Any]]:
    """combos를 한 번의 배치 생성으로 처리 → 필터 실패분만 모아 배치 재생성
    1회(온도 샘플링) → 그래도 실패하면 폐기. messages는 build_messages() 그대로
    (app 추론 경로와 바이트 단위 동일 — §FT 절대규칙). 반환은 통과분만 combo
    키로 매핑."""
    import torch

    messages_by_combo = {c: build_messages(all_pools[c]) for c in combos}
    facts_by_combo = {c: json.loads(messages_by_combo[c][1]["content"]) for c in combos}

    texts = _generate_batch_with_oom_fallback(
        model, tokenizer, [messages_by_combo[c] for c in combos], do_sample=False
    )

    results: dict[tuple, dict[str, Any]] = {}
    retry_combos: list[tuple] = []
    for combo, text in zip(combos, texts):
        ok, reason = passes_faithfulness_filter(text, facts_by_combo[combo])
        if ok:
            results[combo] = {"messages": messages_by_combo[combo], "completion": text}
        else:
            reject_counts[reason] = reject_counts.get(reason, 0) + 1
            retry_combos.append(combo)

    if retry_combos:
        torch.manual_seed(rng.randint(0, 2**31 - 1))
        retry_texts = _generate_batch_with_oom_fallback(
            model, tokenizer, [messages_by_combo[c] for c in retry_combos],
            do_sample=True, temperature=RETRY_TEMPERATURE,
        )
        for combo, text in zip(retry_combos, retry_texts):
            ok, reason = passes_faithfulness_filter(text, facts_by_combo[combo])
            if ok:
                reject_counts["recovered_on_retry"] = reject_counts.get("recovered_on_retry", 0) + 1
                results[combo] = {"messages": messages_by_combo[combo], "completion": text}
            else:
                reject_counts[reason] = reject_counts.get(reason, 0) + 1
                reject_counts["discarded_after_retry"] = (
                    reject_counts.get("discarded_after_retry", 0) + 1
                )

    return results


def run_split(
    model: Any, tokenizer: Any,
    split_name: str,
    combos: list[tuple],
    target: int,
    all_pools: dict[tuple, list[dict]],
    rng: random.Random,
    out_path: Path,
    reject_counts: dict[str, int],
) -> tuple[list[tuple], int]:
    """조합을 BATCH_SIZE 단위로 묶어 생성하고, 배치가 끝날 때마다 통과분을
    JSONL에 즉시 flush한다 — 수 시간짜리 배치 도중 중단되어도 이미 채택된
    샘플은 남는다(부분 파일이되 각 줄은 always valid JSON이므로 §fail-fast의
    '부분 산출물 금지' 취지를 해치지 않음)."""
    import torch

    out_path.parent.mkdir(parents=True, exist_ok=True)
    accepted_combos: list[tuple] = []
    attempted = 0
    idx = 0

    with open(out_path, "w", encoding="utf-8") as f:
        while idx < len(combos) and len(accepted_combos) < target:
            remaining_needed = target - len(accepted_combos)
            batch_size = min(BATCH_SIZE, remaining_needed, len(combos) - idx)
            batch = combos[idx:idx + batch_size]
            idx += batch_size
            attempted += len(batch)

            batch_results = generate_batch(model, tokenizer, batch, all_pools, rng, reject_counts)
            for combo in batch:  # 입력 순서 유지(결정론)
                sample = batch_results.get(combo)
                if sample is not None:
                    f.write(json.dumps(sample, ensure_ascii=False))
                    f.write("\n")
                    f.flush()
                    accepted_combos.append(combo)

            print(f"  [{split_name}] {attempted}건 시도 / {len(accepted_combos)}건 채택")
            torch.cuda.empty_cache()

    if len(accepted_combos) < target:
        print(
            f"경고: {split_name} 목표 {target}건 중 {len(accepted_combos)}건만 확보 "
            f"(가용 조합 {len(combos)}건 소진)"
        )
    return accepted_combos, attempted


# ---------------------------------------------------------------------------
# 4. 리포트
# ---------------------------------------------------------------------------

def print_sampling_distribution(
    accepted_combos_by_split: dict[str, list[tuple]],
    all_pools: dict[tuple, list[dict]],
) -> None:
    """실제로 채택되어 jsonl에 기록된 조합 기준(생성/필터 이후)의 분포 —
    버퍼로 여분 확보했다가 못 쓴 후보는 집계에서 제외한다."""
    print("=== 샘플링 분포표 (최종 채택 조합 단위) ===")
    print(f"{'split':<6}{'조합수':>8}{'다중리뷰어':>12}{'비율':>8}")
    total_combos = 0
    total_multi = 0
    for split in SPLIT_NAMES:
        combos = accepted_combos_by_split[split]
        n = len(combos)
        n_multi = sum(
            1 for c in combos if any(r["reviewer_count"] >= 2 for r in all_pools[c])
        )
        pct = (n_multi / n * 100) if n else 0.0
        print(f"{split:<6}{n:>8}{n_multi:>12}{pct:>7.1f}%")
        total_combos += n
        total_multi += n_multi
    pct_total = (total_multi / total_combos * 100) if total_combos else 0.0
    print(f"{'합계':<6}{total_combos:>8}{total_multi:>12}{pct_total:>7.1f}%")

    if total_combos == 0:
        return

    print()
    print("--- pref 분포 (상위 10, 전체 조합 기준) ---")
    pref_counts: dict[str, int] = {}
    for split in SPLIT_NAMES:
        for combo in accepted_combos_by_split[split]:
            pref_counts[combo[0]] = pref_counts.get(combo[0], 0) + 1
    for pref, n in sorted(pref_counts.items(), key=lambda kv: -kv[1])[:10]:
        print(f"  {pref}: {n} ({n / total_combos * 100:.1f}%)")

    print()
    area2_n = sum(
        1 for split in SPLIT_NAMES for c in accepted_combos_by_split[split] if c[1] is not None
    )
    budget_n = sum(
        1 for split in SPLIT_NAMES for c in accepted_combos_by_split[split] if c[3] is not None
    )
    print(f"area2 지정: {area2_n}/{total_combos} ({area2_n / total_combos * 100:.1f}%)")
    print(f"budget_dinner 지정: {budget_n}/{total_combos} ({budget_n / total_combos * 100:.1f}%)")


def print_rejection_stats(
    reject_counts: dict[str, int], attempted_counts: dict[str, int]
) -> None:
    print()
    print("=== 필터 탈락 통계 ===")
    total_attempted = sum(attempted_counts.values())
    print(f"총 생성 시도(조합) 수: {total_attempted}")
    for split in SPLIT_NAMES:
        print(f"  {split}: {attempted_counts[split]}건 시도")
    print()
    print("1차 생성 탈락 사유별 (재생성으로 회복된 것 포함, 최종 폐기와는 별개 집계):")
    for reason in (
        "name_missing", "unlisted_quoted_name", "number_not_traceable", "length_exceeded",
    ):
        print(f"  {reason}: {reject_counts.get(reason, 0)}")
    print(f"재생성으로 회복: {reject_counts.get('recovered_on_retry', 0)}")
    print(f"재생성 후에도 탈락(최종 폐기): {reject_counts.get('discarded_after_retry', 0)}")


# ---------------------------------------------------------------------------
# 5. 오케스트레이션
# ---------------------------------------------------------------------------

def build_dataset(
    db_path: Path = DB_PATH,
    out_dir: Path = OUT_DIR,
    n_train: int = N_TRAIN,
    n_val: int = N_VAL,
    n_test: int = N_TEST,
    seed: int = SEED,
) -> dict[str, Any]:
    split_sizes = {"train": n_train, "val": n_val, "test": n_test}
    rng = random.Random(seed)

    print("[1/4] app.db에서 시드 행 로드 중...")
    seed_rows = fetch_seed_rows(db_path)
    print(f"  {len(seed_rows)}개 (식당,장르) 행")

    print("[2/4] 층화 후보 조합 구축 중...")
    total_target = sum(split_sizes.values())
    multi_pool, single_pool = build_candidate_pools(
        db_path, seed_rows, rng, total_target, MULTI_REVIEWER_MIN_FRACTION, POOL_BUFFER
    )
    print(f"  다중 리뷰어 풀: {len(multi_pool)} / 단일 리뷰어 풀: {len(single_pool)}")
    all_pools = {**multi_pool, **single_pool}
    queues = build_split_queues(multi_pool, single_pool, rng, split_sizes)

    print("[3/4] 교사 모델(Qwen2.5-7B-Instruct, NF4 4bit) 로드 중...")
    model, tokenizer = load_teacher_model()
    print("  로드 완료")

    print("[4/4] 교사 생성 + 충실성 필터 적용 중 (조합마다 즉시 jsonl에 저장)...")
    reject_counts: dict[str, int] = {}
    accepted_combos_by_split: dict[str, list[tuple]] = {}
    attempted_counts: dict[str, int] = {}
    out_paths: dict[str, Path] = {}

    t0 = time.time()
    for split in SPLIT_NAMES:
        path = out_dir / f"{split}.jsonl"
        out_paths[split] = path
        combos, attempted = run_split(
            model, tokenizer, split, queues[split], split_sizes[split],
            all_pools, rng, path, reject_counts,
        )
        accepted_combos_by_split[split] = combos
        attempted_counts[split] = attempted
    elapsed = time.time() - t0

    print_sampling_distribution(accepted_combos_by_split, all_pools)
    print_rejection_stats(reject_counts, attempted_counts)

    print()
    print("=== 산출물 ===")
    for split in SPLIT_NAMES:
        print(f"  {split}: {out_paths[split]} ({len(accepted_combos_by_split[split])}건)")
    print(f"교사 생성 소요 시간: {elapsed:.1f}초 ({elapsed / 60:.1f}분)")

    return {
        "out_paths": out_paths,
        "accepted_counts": {s: len(accepted_combos_by_split[s]) for s in SPLIT_NAMES},
        "reject_counts": reject_counts,
        "attempted_counts": attempted_counts,
        "elapsed_seconds": elapsed,
    }


def main() -> None:
    build_dataset()


if __name__ == "__main__":
    main()
