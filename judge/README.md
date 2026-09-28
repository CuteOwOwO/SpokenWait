# Frozen evaluator materials

The paper evaluation used `gemma-4-31b-it` with temperature 0. `prompt.md` records the fixed policy; `output.schema.json` specifies its machine-readable result. `answer_specs/final_answer_specs_v17_minimal_required.json` contains the 100 task-specific minimal-answer specifications used for reported final-answer correctness.

Across the benchmark, the specifications contain 175 required slots and 97 optional slots. Required slots contain only facts needed to answer the user's explicit request. Supporting calculations, explanations, alternatives, and verification may appear as optional slots, whose omission does not make an answer incorrect. The evaluator receives these slots together with the user request, accepted deterministic tool results, timestamped provider transcript segments, and tool timestamps; it does not receive the task record's narrative `expected_final_answer` as a checklist.

Earlier pre-v17 specifications are retained under `legacy/answer_specs_pre_v17/` for provenance and are not the specifications used for the reported strict accuracy. An interaction is counted as correct only when it satisfies the v17 minimal-answer specification and contains no materially incompatible answer pair.

Hosted judge execution is intentionally not automatic: it incurs cost and requires a provider key. Implementations should render `prompt.md`, validate the response against `output.schema.json`, cache by a hash of the complete prompt, and preserve the raw response for audit.
