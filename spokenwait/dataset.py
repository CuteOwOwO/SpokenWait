from __future__ import annotations

import hashlib
import json
import sysconfig
from pathlib import Path
from typing import Any, Iterable


_CHECKOUT_ROOT = Path(__file__).resolve().parents[1]
ROOT = _CHECKOUT_ROOT if (_CHECKOUT_ROOT / "data" / "tasks").is_dir() else Path(sysconfig.get_path("data")) / "share" / "spokenwait"
TASK_ROOT = ROOT / "data" / "tasks"


def task_files(root: Path = TASK_ROOT) -> list[Path]:
    return sorted(root.glob("*/[12]_step/tasks.json"))


def load_documents(root: Path = TASK_ROOT) -> list[dict[str, Any]]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in task_files(root)]


def iter_tasks(root: Path = TASK_ROOT) -> Iterable[dict[str, Any]]:
    for document in load_documents(root):
        yield from document["tasks"]


def get_task(task_id: str, root: Path = TASK_ROOT) -> dict[str, Any]:
    for task in iter_tasks(root):
        if task["id"] == task_id:
            return task
    raise KeyError(f"Unknown task: {task_id}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_dataset(root: Path = TASK_ROOT) -> dict[str, Any]:
    files = task_files(root)
    if len(files) != 20:
        raise ValueError(f"Expected 20 task files, found {len(files)}")

    ids: set[str] = set()
    domain_counts: dict[str, dict[int, int]] = {}
    for path in files:
        document = json.loads(path.read_text(encoding="utf-8"))
        category = document.get("category")
        step_count = document.get("step_count")
        tasks = document.get("tasks")
        if not isinstance(category, str) or step_count not in (1, 2):
            raise ValueError(f"Invalid document metadata: {path}")
        if not isinstance(tasks, list) or len(tasks) != 5:
            raise ValueError(f"Expected five tasks: {path}")
        domain_counts.setdefault(category, {})[step_count] = len(tasks)

        for task in tasks:
            task_id = task.get("id")
            if not isinstance(task_id, str) or task_id in ids:
                raise ValueError(f"Missing or duplicate task id: {task_id}")
            ids.add(task_id)
            if task.get("category") != category or task.get("step_count") != step_count:
                raise ValueError(f"Task/document mismatch: {task_id}")
            if len(task.get("steps", [])) != step_count:
                raise ValueError(f"Wrong step count: {task_id}")
            tools = {tool.get("name") for tool in task.get("tools", [])}
            for index, step in enumerate(task["steps"], start=1):
                if step.get("index") != index or step.get("tool_name") not in tools:
                    raise ValueError(f"Invalid workflow: {task_id} step {index}")
                if "tool_input" not in step or "mocked_result" not in step:
                    raise ValueError(f"Incomplete deterministic step: {task_id} step {index}")
            for field in ("user_prompt", "expected_final_answer"):
                if not isinstance(task.get(field), str) or not task[field].strip():
                    raise ValueError(f"Missing {field}: {task_id}")

    if len(domain_counts) != 10 or any(counts != {1: 5, 2: 5} for counts in domain_counts.values()):
        raise ValueError(f"Expected ten balanced domains: {domain_counts}")
    if len(ids) != 100:
        raise ValueError(f"Expected 100 unique tasks, found {len(ids)}")

    spec_ids: list[str] = []
    required_slot_count = 0
    optional_slot_count = 0
    for path in sorted((ROOT / "judge" / "answer_specs").glob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        if document.get("schema_version") != "spokenwait-minimal-final-answer-spec-v17":
            raise ValueError(f"Unexpected answer-spec version: {path}")
        for entry in document.get("tasks", []):
            spec_ids.append(entry["task_id"])
            spec = entry.get("final_answer_spec", {})
            required = spec.get("required_slots", [])
            optional = spec.get("optional_slots", [])
            if not required or any(slot.get("name") == "complete_task_answer" for slot in required):
                raise ValueError(f"Answer spec is not minimally decomposed: {entry['task_id']}")
            if any(slot.get("requirement_basis") != "explicit_user_question" for slot in required):
                raise ValueError(f"Invalid required-slot basis: {entry['task_id']}")
            required_slot_count += len(required)
            optional_slot_count += len(optional)
    if len(spec_ids) != 100 or len(set(spec_ids)) != 100 or set(spec_ids) != ids:
        raise ValueError("Judge answer specifications must match the 100 frozen tasks exactly")
    if (required_slot_count, optional_slot_count) != (175, 97):
        raise ValueError("Unexpected v17 answer-slot counts")

    manifest_path = root.parent / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected = manifest.get("files", {})
        actual = {str(path.relative_to(root.parent)): sha256(path) for path in files}
        if expected != actual:
            raise ValueError("Dataset files differ from data/manifest.json")

    return {
        "task_count": len(ids),
        "domain_count": len(domain_counts),
        "one_step": sum(value[1] for value in domain_counts.values()),
        "two_step": sum(value[2] for value in domain_counts.values()),
        "answer_specs": len(spec_ids),
        "required_slots": required_slot_count,
        "optional_slots": optional_slot_count,
        "domains": sorted(domain_counts),
    }
