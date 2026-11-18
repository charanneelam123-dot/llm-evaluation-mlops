# Real-model results: local Llama 3.2

Run completed 2026-11-18T16:12:56.549679+00:00. Model `llama3.2:latest`, digest `a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`, quantization `Q4_K_M`.

40 authored cases across eight categories; two frozen prompts; 80 measured local inference calls. No fixture answers were used as model responses.

| Measure | Baseline | Grounded |
|---|---:|---:|
| Strict joint passes | 17/40 | 10/40 |
| Strict answer matches | 35/40 | 35/40 |
| Exact citation-set matches | 22/40 | 10/40 |
| Provider errors | 0/40 | 0/40 |
| Median local wall time | 2.76 s | 2.55 s |

## Category results

| Category | Baseline joint passes | Grounded joint passes |
|---|---:|---:|
| arithmetic | 1/5 | 0/5 |
| context_injection | 3/5 | 1/5 |
| currency_units | 0/5 | 0/5 |
| fact_lookup | 5/5 | 0/5 |
| missing_evidence | 0/5 | 5/5 |
| multi_source | 0/5 | 0/5 |
| negation | 5/5 | 0/5 |
| version_conflict | 3/5 | 4/5 |

## What the score means

A joint pass requires a strict accepted-answer match and the exact expected citation set. Extra citations, bracket-wrapped IDs, and otherwise correct verbose answers can fail this contract. This is not a semantic hallucination or general intelligence score. The two prompts are compared as written; they were not tuned against these outputs.

## Inspect the evidence

- [Method and reproduction](README.md)
- [Full report](report.json)
- [Every input and accepted answer](cases.json)
- [Raw model outputs, token counts, errors, and timings](outputs.jsonl)
- [Frozen prompts, model digest, and settings](manifest.json)
- [Failure table](failures.csv)

## Limits

- Small synthetic challenge set, not an external benchmark or production distribution.
- Five related cases per category are not independent samples; intervals are descriptive only.
- Strict answer matching can reject semantically correct verbose answers; inspect raw outputs.
- Single local run per prompt/case; wall times are hardware and load dependent, not hosted-service latency.
- Quantized 3.2B model; no claim about other model families or agent tool-selection quality.

## Failure analysis

Both prompts matched the required short answer in 35 of 40 cases. The baseline returned “Not specified” on the five missing-evidence cases, which fails the fixed abstention label despite communicating absence. The grounded prompt used the required abstention label but omitted USD on all five rent-increase answers. Citation formatting and extra sources account for much of the difference in joint passes. The longer prompt did not improve strict joint compliance in this run.
