"""Regrade the frozen Ollama responses without running inference."""
import json
from pathlib import Path

from run_local_evaluation import grade

DATA = Path(__file__).resolve().parents[1] / "docs" / "real-model-evaluation"


def main():
    cases = {case["id"]: case for case in json.loads((DATA / "cases.json").read_text(encoding="utf-8"))}
    scores = {"baseline": [], "grounded": []}
    pending = {(variant, case_id) for variant in scores for case_id in cases}
    for line in (DATA / "outputs.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        key = (row["variant"], row["case_id"])
        if key not in pending:
            raise ValueError(f"Duplicate or unexpected response: {key}")
        pending.remove(key)
        try:
            output = json.loads(row["raw_content"] or "null")
        except json.JSONDecodeError:
            output = None
        result = grade(output, cases[row["case_id"]])
        scores[row["variant"]].append(result)
        if key == ("grounded", "negation-04"):
            example = (output, cases[row["case_id"]]["expected_citations"], result)
    if pending:
        raise ValueError(f"Missing responses: {sorted(pending)}")
    print("Prompt     Answer correct    Answer + citations correct")
    for variant, results in scores.items():
        answers = sum(r["strict_answer_match"] for r in results)
        passes = sum(r["passed"] for r in results)
        print(f"{variant:10} {answers}/{len(results)}             {passes}/{len(results)}")
    output, expected, result = example
    print(f"grounded / negation-04: {output}; expected citations {expected}")
    print(f"Answer match: {result['strict_answer_match']}; citation set match: {result['citation_set_match']}")


if __name__ == "__main__":
    main()
