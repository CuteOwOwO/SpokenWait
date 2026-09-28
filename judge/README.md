# Frozen evaluator materials

The paper evaluation used `gemma-4-31b-it` with temperature 0. `prompt.md` records the fixed policy; `output.schema.json` specifies its machine-readable result. The seven files in `answer_specs/` are the exact 100 task-specific specifications selected by the formal full-100 workflow. Their filenames retain provenance even where an original filename contains the word `draft` outside this repository.

The evaluator receives the user request, accepted deterministic tool results, timestamped provider transcript segments, tool timestamps, and the task-specific answer specification. It must not receive `expected_final_answer` as a checklist.

Hosted judge execution is intentionally not automatic: it incurs cost and requires a provider key. Implementations should render `prompt.md`, validate the response against `output.schema.json`, cache by a hash of the complete prompt, and preserve the raw response for audit.
