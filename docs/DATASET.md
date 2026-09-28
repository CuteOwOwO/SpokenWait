# Dataset format

`data/tasks/<domain>/<depth>_step/tasks.json` contains five tasks. Each task includes:

- `user_prompt`, `category`, and `step_count`;
- public tool names, descriptions, parameter schemas, and response schemas;
- an ordered workflow with deterministic `tool_input` and `mocked_result` values;
- dependency annotations for two-step tasks;
- evaluator-only `expected_final_answer` and review metadata.

Do not expose `steps`, deterministic results, answer specifications, or expected answers to the evaluated agent before their corresponding tool events. Public tool definitions are model-visible. `data/manifest.json` pins every paper-v1 task file by SHA-256.
