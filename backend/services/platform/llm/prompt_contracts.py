"""Shared JSON LLM contract helpers — not interview-specific."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

from models.interview import DifficultyLevel
from utils.logger import get_logger

logger = get_logger("PromptContracts")

T = TypeVar("T")


@dataclass
class PromptExecutionError:
    category: str
    message: str


@dataclass
class PromptContractResult(Generic[T]):
    template_id: str
    ok: bool
    value: T
    error: Optional[PromptExecutionError] = None


PromptContractInput = Dict[str, Any]


def extract_json_payload(raw: str, *, fallback: Any) -> Any:
    text = (raw or "").strip()
    if not text:
        return fallback
    candidate = text.strip("`").strip()
    if candidate.lower().startswith("json"):
        candidate = candidate[4:].strip()
    start = candidate.find("{")
    end = candidate.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(candidate[start:end])
        except Exception:
            pass
    start_arr = candidate.find("[")
    end_arr = candidate.rfind("]") + 1
    if start_arr >= 0 and end_arr > start_arr:
        try:
            return json.loads(candidate[start_arr:end_arr])
        except Exception:
            pass
    return fallback


def extract_json_dict(raw: str) -> Dict[str, Any]:
    payload = extract_json_payload(raw, fallback={})
    return payload if isinstance(payload, dict) else {}


def _to_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _coerce_enum(value: Any, allowed: List[str], default: str) -> str:
    v = str(value or "").strip().lower()
    normalized = {a.lower(): a for a in allowed}
    return normalized.get(v, default)


async def execute_json_contract(
    *,
    template_id: str,
    engine: Any,
    prompt: str,
    temperature: float,
    fallback: T,
    normalizer: Callable[[Any], T],
    empty_fallback: str = "{}",
) -> PromptContractResult[T]:
    try:
        raw = await engine.generate_raw(prompt, temperature, empty_fallback=empty_fallback)
        parsed = extract_json_payload(raw, fallback=fallback)
        normalized = normalizer(parsed)
        return PromptContractResult(template_id=template_id, ok=True, value=normalized)
    except Exception as e:
        logger.warning("prompt_contract_error template_id=%s reason=%s", template_id, e)
        return PromptContractResult(
            template_id=template_id,
            ok=False,
            value=fallback,
            error=PromptExecutionError(category="provider_or_parse", message=str(e)),
        )


def normalize_question_payload(parsed: Any, *, fallback_question: str, difficulty: DifficultyLevel, q_type: str) -> Dict[str, Any]:
    obj = parsed if isinstance(parsed, dict) else {}
    return {
        "type": q_type,
        "question": str(obj.get("question") or fallback_question),
        "evaluation_criteria": str(obj.get("evaluation_criteria") or ""),
        "difficulty": difficulty.value,
    }


def normalize_answer_evaluation(parsed: Any) -> Dict[str, Any]:
    obj = parsed if isinstance(parsed, dict) else {}
    quality = _coerce_enum(
        obj.get("quality"),
        ["strong", "adequate", "weak", "confused", "no_answer"],
        "adequate",
    ).lower()
    confidence = _coerce_enum(obj.get("confidence_signal"), ["high", "medium", "low"], "medium").lower()
    action = _coerce_enum(
        obj.get("recommended_action"),
        ["probe", "challenge", "advance", "simplify", "hint"],
        "probe",
    ).lower()
    return {
        "quality": quality,
        "completeness": _clamp(_to_float(obj.get("completeness"), 0.5), 0.0, 1.0),
        "what_was_good": obj.get("what_was_good"),
        "what_was_missing": obj.get("what_was_missing"),
        "detected_misconception": obj.get("detected_misconception"),
        "confidence_signal": confidence,
        "recommended_action": action,
    }


def normalize_replay_highlights(parsed: Any, *, q_max: int, a_max: int, limit: int) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if not isinstance(parsed, list):
        return out
    for item in parsed:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question") or "").strip()[:q_max]
        answer = str(item.get("answer") or "").strip()[:a_max]
        if not question or not answer:
            continue
        row: Dict[str, Any] = {"question": question, "answer": answer, "source": "llm"}
        c = item.get("confidence")
        if isinstance(c, (int, float)):
            row["confidence"] = round(_clamp(float(c), 0.0, 1.0), 3)
        out.append(row)
        if len(out) >= limit:
            break
    return out
