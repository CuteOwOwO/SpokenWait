# Evaluation protocol

SpokenWait evaluates 100 tasks at fixed per-tool delays of 3, 5, 8, and 12 seconds, with three trials per task-delay cell. A two-step task applies the delay independently to both calls. The paper's five-agent core therefore contains 6,000 interactions.

For each intermediate result `i`, let `R_i` be result arrival, `A_i` the first utterance reporting that result, and `L_(i+1)` the first utterance announcing the next lookup. Eligible cues occur before the next result. The next boundary is the earliest eligible cue no earlier than `R_i`; if no cue exists, it falls back to `R_i`. The first boundary is user-speech end. The final boundary is the onset of the first substantive answer after the final result.

The scorer derives:

- initial response latency: first audible assistant speech minus user-speech end;
- stage speech coverage: audible speech duration divided by semantic-stage duration;
- maximum silence: the longest gap within a semantic stage, including its leading and trailing gaps;
- final-result-to-answer latency: final-answer onset minus final result arrival.

Quality annotations are stage-level premature hallucination and interaction-level final-answer correctness. Cross-model summaries first average repetitions and delays within task, then average tasks with equal weight.

Provider adapters should emit the trace shape demonstrated by `outputs/demo/memory_card_trace.json`. Timestamp values are milliseconds on one monotonic interaction clock. Use provider transcript text aligned to audible playback. Preserve raw provider events separately for audit.
