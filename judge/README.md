# Frozen evaluator materials

The paper evaluation used `gemma-4-31b-it` with temperature 0. `prompt.md` records the fixed policy; `output.schema.json` specifies its machine-readable result. `answer_specs/final_answer_specs.json` contains one task-specific minimal-answer specification for each benchmark task.

Required slots contain only facts needed to answer the user's explicit request. Supporting calculations, explanations, alternatives, and verification may appear as optional slots, whose omission does not make an answer incorrect. The evaluator receives these slots together with the user request, accepted deterministic tool results, timestamped provider transcript segments, and tool timestamps; it does not receive the task record's narrative `expected_final_answer` as a checklist.

An interaction is counted as correct only when it satisfies the published minimal-answer specification and contains no materially incompatible answer pair.

Hosted judge execution is intentionally not automatic: it incurs cost and requires a provider key. Implementations should render `prompt.md`, validate the response against `output.schema.json`, cache by a hash of the complete prompt, and preserve the raw response for audit.
