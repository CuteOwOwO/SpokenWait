from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .dataset import get_task
from .metrics import score_trace


TASK_ID = "product_inventory_2step_camera_mode_savings_004"


def build_demo_trace(delay_ms: int = 3000) -> dict[str, Any]:
    task = get_task(TASK_ID)
    first_call = 1500
    first_result = first_call + delay_ms
    handoff_start = first_result + 300
    second_call = handoff_start + 1300
    second_result = second_call + delay_ms
    answer_start = second_result + 500
    return {
        "schema_version": "spokenwait-trace-v1",
        "task_id": task["id"],
        "user_end_ms": 0,
        "tool_stages": [
            {"step_index": 1, "tool_name": task["steps"][0]["tool_name"], "call_ms": first_call, "result_ms": first_result},
            {"step_index": 2, "tool_name": task["steps"][1]["tool_name"], "call_ms": second_call, "result_ms": second_result},
        ],
        "speech_segments": [
            {"start_ms": 600, "end_ms": 1400, "text": "I'll check the camera requirements first."},
            {"start_ms": handoff_start, "end_ms": handoff_start + 1200, "text": "I found the supported card types. Now I'll check inventory."},
            {"start_ms": answer_start, "end_ms": answer_start + 4400, "text": task["expected_final_answer"]},
        ],
        "semantic_annotation": {
            "handoffs": [{"from_step_index": 1, "result_report_ms": handoff_start, "next_lookup_ms": handoff_start + 450}],
            "final_answer_start_ms": answer_start,
        },
        "judge": {"stage_hallucination": [0, 0], "final_answer_correct": 1},
    }


def run_demo(output_dir: Path, delay_ms: int = 3000) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    trace = build_demo_trace(delay_ms)
    metrics = score_trace(trace)
    trace_path = output_dir / "memory_card_trace.json"
    metrics_path = output_dir / "memory_card_metrics.json"
    trace_path.write_text(json.dumps(trace, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return trace_path, metrics_path
