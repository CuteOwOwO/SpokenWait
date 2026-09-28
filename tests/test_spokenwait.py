import unittest

from spokenwait.dataset import get_task, validate_dataset
from spokenwait.demo import TASK_ID, build_demo_trace
from spokenwait.metrics import score_trace


class SpokenWaitTests(unittest.TestCase):
    def test_frozen_dataset(self):
        summary = validate_dataset()
        self.assertEqual(summary["task_count"], 100)
        self.assertEqual(summary["one_step"], 50)
        self.assertEqual(summary["two_step"], 50)

    def test_memory_card_task(self):
        task = get_task(TASK_ID)
        self.assertEqual(task["step_count"], 2)
        self.assertEqual(task["steps"][1]["tool_name"], "batch_get_memory_card_inventory")

    def test_demo_metrics(self):
        metrics = score_trace(build_demo_trace())
        self.assertEqual(metrics["initial_response_latency_ms"], 600)
        self.assertEqual(metrics["final_result_to_answer_latency_ms"], 500)
        self.assertEqual(len(metrics["stages"]), 2)


if __name__ == "__main__":
    unittest.main()
