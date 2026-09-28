from __future__ import annotations

from typing import Any, Iterable


def _union(intervals: Iterable[tuple[float, float]]) -> list[tuple[float, float]]:
    merged: list[list[float]] = []
    for start, end in sorted(intervals):
        if end <= start:
            continue
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(start, end) for start, end in merged]


def _clip(intervals: Iterable[tuple[float, float]], start: float, end: float) -> list[tuple[float, float]]:
    return _union((max(start, left), min(end, right)) for left, right in intervals if right > start and left < end)


def _coverage_and_max_silence(intervals: list[tuple[float, float]], start: float, end: float) -> tuple[float, float]:
    if end <= start:
        raise ValueError("Semantic stage must have positive duration")
    speech = _clip(intervals, start, end)
    spoken = sum(right - left for left, right in speech)
    cursor = start
    gaps: list[float] = []
    for left, right in speech:
        gaps.append(max(0.0, left - cursor))
        cursor = max(cursor, right)
    gaps.append(max(0.0, end - cursor))
    return spoken / (end - start), max(gaps)


def score_trace(trace: dict[str, Any]) -> dict[str, Any]:
    user_end = float(trace["user_end_ms"])
    stages = sorted(trace["tool_stages"], key=lambda item: item["step_index"])
    speech = [(float(item["start_ms"]), float(item["end_ms"])) for item in trace["speech_segments"]]
    if not stages or [item["step_index"] for item in stages] != list(range(1, len(stages) + 1)):
        raise ValueError("tool_stages must be consecutively indexed")
    if not speech:
        raise ValueError("At least one audible speech segment is required")

    annotation = trace["semantic_annotation"]
    handoffs = {int(item["from_step_index"]): item for item in annotation.get("handoffs", [])}
    boundaries = [user_end]
    for index in range(1, len(stages)):
        result_ms = float(stages[index - 1]["result_ms"])
        next_result_ms = float(stages[index]["result_ms"])
        handoff = handoffs.get(index, {})
        candidates = [
            float(value)
            for value in (handoff.get("result_report_ms"), handoff.get("next_lookup_ms"))
            if value is not None and float(value) < next_result_ms
        ]
        boundaries.append(max(result_ms, min(candidates)) if candidates else result_ms)
    final_answer_ms = annotation.get("final_answer_start_ms")
    if final_answer_ms is None:
        raise ValueError("final_answer_start_ms is required for continuous stage metrics")
    boundaries.append(float(final_answer_ms))
    if any(right <= left for left, right in zip(boundaries, boundaries[1:])):
        raise ValueError(f"Semantic boundaries must be strictly increasing: {boundaries}")

    rows = []
    for index, (start, end) in enumerate(zip(boundaries, boundaries[1:]), start=1):
        coverage, max_silence = _coverage_and_max_silence(speech, start, end)
        rows.append({
            "stage": index,
            "start_ms": start,
            "end_ms": end,
            "speech_coverage": round(coverage, 6),
            "maximum_silence_ms": round(max_silence, 3),
        })

    first_speech = min(max(start, user_end) for start, end in speech if end > user_end)
    final_result = float(stages[-1]["result_ms"])
    if float(final_answer_ms) < final_result:
        raise ValueError("Final answer must start after the final tool result")
    quality = trace.get("judge", {})
    return {
        "task_id": trace.get("task_id"),
        "initial_response_latency_ms": round(first_speech - user_end, 3),
        "final_result_to_answer_latency_ms": round(float(final_answer_ms) - final_result, 3),
        "stages": rows,
        "stage_hallucination": quality.get("stage_hallucination"),
        "final_answer_correct": quality.get("final_answer_correct"),
    }
