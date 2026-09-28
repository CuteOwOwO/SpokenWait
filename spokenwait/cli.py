from __future__ import annotations

import argparse
import json
from pathlib import Path

from .dataset import get_task, iter_tasks, validate_dataset
from .demo import TASK_ID, run_demo
from .metrics import score_trace


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="spokenwait", description="Validate and score SpokenWait traces")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="validate the frozen 100-task release")
    subparsers.add_parser("list", help="list task IDs")
    show = subparsers.add_parser("show", help="print one task")
    show.add_argument("task_id")
    demo = subparsers.add_parser("demo", help="run the offline memory-card example")
    demo.add_argument("--delay-ms", type=int, default=3000)
    demo.add_argument("--output-dir", type=Path, default=Path("outputs/demo"))
    score = subparsers.add_parser("score", help="compute temporal metrics from a trace")
    score.add_argument("trace", type=Path)
    score.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    if args.command == "validate":
        print(json.dumps(validate_dataset(), indent=2))
    elif args.command == "list":
        for task in iter_tasks():
            print(f'{task["id"]}\t{task["category"]}\t{task["step_count"]}-step')
    elif args.command == "show":
        print(json.dumps(get_task(args.task_id), indent=2, ensure_ascii=False))
    elif args.command == "demo":
        if args.delay_ms <= 0:
            parser.error("--delay-ms must be positive")
        trace, metrics = run_demo(args.output_dir, args.delay_ms)
        print(f"Task: {TASK_ID}\nTrace: {trace}\nMetrics: {metrics}")
        print(metrics.read_text(encoding="utf-8"), end="")
    elif args.command == "score":
        result = score_trace(json.loads(args.trace.read_text(encoding="utf-8")))
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
    return 0
