# Local real-model evaluation

This experiment runs the installed `llama3.2:latest` model through Ollama. It is separate from the application's authored-output fixtures. It does not require an external API key.

Both prompts answered **35/40** cases correctly. Requiring the correct answer and the exact supporting citation set reduced the baseline to **17/40** and the grounded prompt to **10/40**.

From the repository root, regrade all 80 saved responses with Python alone:

```bash
python scripts/score_saved_responses.py
```

### Worked example: a correct answer with an extra citation

**Question.** Is overnight delivery available for Zone 4? Answer Yes or No.

| Source | Passage supplied to the model |
| --- | --- |
| `policy-3` | Overnight delivery is not available for Zone 4. Standard delivery is available. |
| `notice-3` | The delivery FAQ was updated this month. |

**Saved response** (grounded prompt, `negation-04`):

```json
{"answer": "No", "citations": ["policy-3", "notice-3"]}
```

**How the grader scored it.** "No" matches the answer key. Both citation IDs exist in the context, but only `policy-3` establishes which delivery options Zone 4 offers. The FAQ update date gives no delivery information. Adding `notice-3` therefore fails the exact-set check and the joint score. The grader compares against the authored citation labels; it does not infer support from the passages itself.

[Inspect the case labels](cases.json) and [the original model responses](outputs.jsonl).

## Frozen setup

- 40 authored synthetic cases, five in each of eight categories: fact lookup, negation, missing evidence, version conflicts, multi-source arithmetic, currency/units, document prompt injection, and arithmetic.
- Two prompts fixed before inference: `baseline` and `grounded`.
- One model response per case and prompt, 80 measured inference calls. A warmup call is excluded.
- Model temperature 0, seed 41, context window 4,096, output cap 160 tokens. JSON schema constrains both prompts equally.
- Case order is shuffled with seed 41. Prompt order alternates by case to reduce order effects. Each request has a fresh chat history. There are no automatic retries.
- The model receives only the context and question, never the accepted answers or expected source labels.
- The primary pass requires valid output structure, a strict accepted-answer match, the exact expected citation set, and no unavailable citation IDs.

Strict matching lowercases and normalizes whitespace/punctuation. It can reject a semantically correct longer answer. It is a transparent task-compliance score, not a semantic factuality or hallucination metric. Inspect the raw answers before drawing conclusions.

## Reproduce

Install Ollama and the intended model first. Then, from the repository root:

```bash
python scripts/run_local_evaluation.py --model llama3.2:latest
```

The runner uses Python's standard library. It calls the local Ollama API at `http://127.0.0.1:11434`. Override `--base-url` only for an endpoint you intend to use. The default output directory is this folder; use `--out` to retain a separate repeat.

`manifest.json` captures the exact model digest, Ollama version, prompts, inference settings, and SHA-256 fingerprints. `cases.json` publishes every question and label. `outputs.jsonl` preserves the actual model response, grader outcome, errors, token counts, and timing for each call. `report.json` contains category-level summaries and paired outcomes.

## Interpretation limits

This is a small, templated synthetic challenge set aligned with this project's grounding and citation behavior. It is not an external benchmark, a production workload, or evidence of general model superiority. Related cases are not independent; descriptive Wilson intervals do not establish significance. Only one response is sampled per prompt and case. Local wall times depend on hardware, machine load, quantization, and model state; they are not the latency of the hosted Render app. This experiment evaluates answer and citation behavior, not agent tool selection.

Ollama API reference: https://docs.ollama.com/api/chat
