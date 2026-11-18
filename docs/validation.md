# Validation record

## Local model experiment, November 18, 2026

- Ran the installed Ollama `llama3.2:latest` model (3.2B, Q4_K_M), digest `a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`.
- 40 synthetic challenge cases across eight categories, two frozen prompts, 80 measured inference calls; one excluded warmup. No external paid model calls.
- Baseline: 17/40 strict joint passes; grounded: 10/40. Both: 35/40 strict short-answer matches. There were no provider errors.
- Raw outputs, prompts, labels, token counts, timing, model settings, and hashes are in `real-model-evaluation/`.
- Runner and output SHA-256 hashes were verified against the report. Labels and prompts were not changed after inference.
- All 14 tests passed: the original eight application checks plus six tests for the standalone local runner's dataset and scoring contract.
- Scores describe strict output compliance on a small synthetic set, not general semantic accuracy, a hallucination rate, or hosted-app performance.

[Full measured results](real-model-evaluation/results.md).

Built on 2026-11-17 with Python 3.12.14 on Windows.

- Eight automated tests passed for this service.
- Dependencies are pinned to the versions used in this build.
- The Dockerfile and GitHub workflow are included. A local Docker engine is not installed;
  image build verification runs in GitHub Actions.
- No paid live-model calls were made.
- Interactive Chrome checks passed against the actual local Python API.
- All four browser interfaces passed 390px horizontal-overflow checks with no script errors.
- Render reports the deployment as live. Public health and functional API checks passed.
- GitHub Actions passed Python 3.12/3.13 tests and built the Docker image.
- Live app: https://llm-evaluation-mlops.onrender.com
- Verification details: `cloud-verification.json`.

Limitations and measured behavior are described in the README. This implementation
does not validate the workload sizes or performance figures in the source resume.
