import json
import os
from typing import Any

DEFAULT_MODEL_PATH = "Qwen/Qwen2.5-1.5B-Instruct"

SYSTEM_PROMPT = (
    "아래 구조화된 사실만 근거로 한국어 추천문을 작성하라. "
    "사실에 없는 내용(맛, 분위기 묘사 등)은 창작하지 마라. "
    "복수 리뷰어의 평가를 종합하되 사실 외 창작 금지. "
    "각 식당 1~2문장과 전체 요약 1문장으로 구성하라."
)


def load_model() -> tuple[Any, Any, str | None]:
    path = os.environ.get("QWEN_MODEL_PATH", DEFAULT_MODEL_PATH)
    try:
        # Lazy import: transformers/torch are optional at import time so that
        # `import app.generate` (and anything importing it, e.g. app.ui)
        # still succeeds when they're absent — only load_model() needs them,
        # and its ImportError branch below is how that absence fails soft.
        from transformers import AutoModelForCausalLM, AutoTokenizer

        model = AutoModelForCausalLM.from_pretrained(
            path, torch_dtype="auto", device_map="cuda"
        )
        tokenizer = AutoTokenizer.from_pretrained(path)
        return model, tokenizer, None
    except (OSError, RuntimeError, ValueError, ImportError) as exc:
        # fail-soft per spec: CUDA-unavailable/OOM/missing-checkpoint etc. all
        # surface as one of these from transformers/torch — fall back to template.
        warning = f"모델 로드 실패({path}): {exc}. 템플릿 폴백으로 전환합니다."
        return None, None, warning


def _extract_facts(r: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": r["name"],
        "genres": r["genres"],
        "stations": r["stations"],
        "tabelog_rating": r["tabelog_rating"],
        "tabelog_review_count": r["tabelog_review_count"],
        "budget_dinner": r.get("budget_dinner"),
        "budget_lunch": r.get("budget_lunch"),
        "awards": [a["label"] for a in r.get("awards", [])],
        "visit_count_total": r["visit_count_total"],
        # §14.4: per-reviewer breakdown so the model can synthesize multiple
        # reviewers' evaluations instead of only ever seeing one.
        "reviewers": [
            {
                "display_name": rv["reviewer_display_name"],
                "reviewer_rating": rv["reviewer_rating"],
                "visit_count": rv["visit_count"],
            }
            for rv in r["reviewers"]
        ],
    }


def build_messages(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    facts = [_extract_facts(r) for r in records]
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(facts, ensure_ascii=False)},
    ]


def _all_names_present(text: str, records: list[dict[str, Any]]) -> bool:
    return all(r["name"] in text for r in records)


def _template_fallback(records: list[dict[str, Any]]) -> str:
    lines = []
    for r in records:
        genre_text = "、".join(r["genres"]) if r["genres"] else "장르 정보 없음"
        if r["tabelog_rating"] is not None:
            rating_text = f"tabelog {r['tabelog_rating']}"
        else:
            rating_text = "평점 정보 없음"
        lines.append(
            f"- {r['name']}: {genre_text} · {rating_text} "
            f"(리뷰 {r['tabelog_review_count']}건) · "
            f"리뷰어 {len(r['reviewers'])}명 방문 {r['visit_count_total']}회"
        )
    summary = f"조건에 맞는 {len(records)}곳을 안내드립니다."
    return "\n".join([summary, *lines])


def _run_model(
    records: list[dict[str, Any]],
    model: Any,
    tokenizer: Any,
    *,
    do_sample: bool,
    temperature: float | None = None,
) -> str:
    messages = build_messages(records)
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    gen_kwargs: dict[str, Any] = {"max_new_tokens": 512, "do_sample": do_sample}
    if do_sample:
        gen_kwargs["temperature"] = temperature
    output_ids = model.generate(**inputs, **gen_kwargs)
    generated = output_ids[0][inputs["input_ids"].shape[1] :]
    return tokenizer.decode(generated, skip_special_tokens=True)


def generate(
    records: list[dict[str, Any]], model: Any = None, tokenizer: Any = None
) -> str:
    if model is None or tokenizer is None:
        return _template_fallback(records)

    text = _run_model(records, model, tokenizer, do_sample=False)
    if _all_names_present(text, records):
        return text

    text = _run_model(records, model, tokenizer, do_sample=True, temperature=0.7)
    if _all_names_present(text, records):
        return text

    return _template_fallback(records)
