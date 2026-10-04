"""Sample graded outputs for human grading (judge calibration).

Usage:
    uv run python evals/calibration/sample.py --run v1_baseline            # 25 rows, stratified by specialist
    uv run python evals/calibration/sample.py --run v1_baseline --n 25 --seed 3
    uv run python evals/calibration/sample.py --run v1_baseline --keep --add kb=10   # keep graded ids, add 10 kb rows

``--keep`` reuses the ids already in human_grades.jsonl (grades are never overwritten), regenerates
the review sheet for them from the latest recorded answers, and ``--add specialist=N`` appends N
new rows of that specialist (null grades) so the sample can grow after a re-run.

Writes evals/calibration/<run>/review_sheet.md (question, gold answer, evidence, answer; the judge's
verdicts are deliberately not shown) and evals/calibration/<run>/human_grades.jsonl, one line per
sampled row for the grader to fill in:
    groundedness    true/false   every specific claim is supported by the evidence shown
    completeness    true/false   the gold answer's facts are present and not contradicted
    report_quality  1..5         the rubric in prompt/prompts.yaml (evals.judge.report_quality)
Then run evals/calibration/agreement.py --run <run>.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evals.graders.code import evidence_text  # noqa: E402
from evals.run_golden import RUNS_DIR, load_results, load_rows  # noqa: E402

CALIBRATION_DIR = PROJECT_ROOT / "evals" / "calibration"


def stratified_sample(rows: list[dict], n: int, seed: int) -> list[dict]:
    """Proportional allocation per specialist (largest remainder, at least one each), deterministic for a seed."""
    rng = random.Random(seed)
    groups: dict[str, list[dict]] = {}
    for row in rows:
        groups.setdefault(row["specialist"], []).append(row)
    total = len(rows)
    shares = {key: n * len(group) / total for key, group in groups.items()}
    quotas = {key: max(1, int(share)) for key, share in shares.items()}
    for key in sorted(groups, key=lambda k: shares[k] - int(shares[k]), reverse=True):
        if sum(quotas.values()) >= n:
            break
        quotas[key] += 1
    chosen = []
    for key in sorted(groups):
        group = sorted(groups[key], key=lambda r: r["id"])
        rng.shuffle(group)
        chosen.extend(group[:min(quotas[key], len(group))])
    return sorted(chosen, key=lambda r: r["id"])


# Restates the judge rubrics in prompt/prompts.yaml (evals.judge) so humans and the judge grade to one standard.
GRADING_GUIDE = """\
Grade each answer on three metrics and record the grades in `human_grades.jsonl` (same directory, one line
per row id): `groundedness` and `completeness` as `true`/`false`, `report_quality` as an integer 1–5, and
`notes`. These are the metrics the LLM judge grades (`prompt/prompts.yaml`, `evals.judge`); the criteria
below restate its rubrics. Grade the three metrics independently: a wrong answer can still be grounded,
and a padded answer can still be complete.

### What each row shows

- **Question**: what the user asked.
- **Gold answer**: the minimum a correct answer must convey. Use it for completeness only.
- **Route**: expected versus actual delegation. Context only; not graded here.
- **Evidence**: every tool output recorded during the run (database results, web search summaries with
  their source lists, knowledge-base answers and passages), exactly as the judge receives it. Tool
  arguments such as query filters or aggregation pipelines are not recorded, only outputs. If the block
  ends with `[evidence truncated]`, the judge saw the same cut: grade against what is shown.
- **Answer**: the text being graded.

### groundedness (true / false)

Is every material factual claim in the answer supported by the evidence block? Use only the evidence,
not your own knowledge of the data or the gold answer.

- **Supported**: the evidence states it, or it follows arithmetically from the evidence (sums, ratios,
  percentages, counts of listed items). Check the arithmetic; a miscalculated figure is unsupported.
- **Unsupported**: it contradicts the evidence, or it asserts a specific fact (number, date, name, dosage,
  quotation, citation) that appears in no evidence. A data-quality assurance ("no null quantities",
  "no expired batches", "no orphan ids") is unsupported unless the outputs shown establish it; an empty
  result from an unrecorded query does not.
- **Inferred from complete results**: a claim that necessarily follows from outputs covering every record
  (an unfiltered count, or groups that add up to the collection total) is supported, even when no query
  testing it directly is shown. Example: if all 20 sales fall within a 2025 date range, none has a null
  `sale_date`. If the outputs do not show that every record is covered, the claim is unsupported.
- **Labelled inferences**: a claim the answer itself marks as an inference, assumption or estimate
  ("inferred from", "assuming", "likely") is neutral, provided the answer does not state it elsewhere as
  fact. The same claim stated flatly is graded normally.
- **Web sources**: a claim attributed to a web source is supported only when the search summary states
  it. A title or URL in a source list shows that the page exists, not what it says.
- **Neutral (ignore)**: general background a reader would accept without a source (definitions,
  well-known drug classes) unless the answer attributes it to a source; process narration (which tools or
  collections were consulted and the query or pipeline used, whether files were attached, what the
  assistant could not do); and
  statements of what a figure includes or excludes by construction ("gross stock, not net of
  reservations"), which describe the method rather than the data.
- An answer that honestly says information was unavailable is grounded.
- **Material** means any specific fact a reader could rely on, including side tables, comparisons and
  caveats, not only the headline answer. `true` only when no material claim is unsupported; one is
  enough for `false`.

### completeness (true / false)

Does the answer convey every fact in the gold answer?

- `true`: every gold fact is present and not contradicted elsewhere in the answer. Equivalent forms count
  (25,000 = 25000; "third generation" = "3rd-generation"; a more precise value that falls within the gold
  one, such as 27 October 1999 for "October 1999"). Extra content does not matter here.
- `false`: a gold fact is missing, wrong, contradicted, or hedged into uselessness.
- If the gold answer says no record exists or that the request should be declined, an answer that
  invents data is `false`.
- Ignore the evidence here: a gold fact stated without supporting evidence still counts as present (that
  is a groundedness failure, not a completeness one).

### report_quality (1–5)

Rate the answer as a research deliverable:

- **5**: answers the question first; structure fits the content (a table for tabular data, prose for a
  single fact); states provenance (which database, document or web source); no padding; no invented
  detail; in the user's language.
- **4**: answers directly with minor issues: slightly long, one vague provenance statement, or a small
  formatting problem.
- **3**: answers the question but is hard to use: buried answer, padded sections, unclear provenance, or
  unnecessary caveats.
- **2**: partial or confusing: important parts missing, contradictory statements, or mostly process
  narration ("I queried...") instead of results.
- **1**: does not answer, is wrong throughout, or is unreadable.

When two levels fit, choose the one whose description matches the most serious problem.

### notes

For every `false` and every rating below 5, name the specific claim (groundedness), the missing or wrong
gold fact (completeness), or the main problem (report_quality). Leave a metric `null` if you cannot
decide; rows with `null` grades are skipped as pending.
"""


def review_sheet(run: str, rows: list[dict], results: dict[str, dict]) -> str:
    parts = [f"# Calibration review sheet: {run}", "", "## Grading criteria", "", GRADING_GUIDE]
    for index, row in enumerate(rows, 1):
        record = results[row["id"]]
        events = record["metrics"].get("events", [])
        evidence = evidence_text(events) or "(no evidence recorded)"
        parts += [f"## {index}. {row['id']} ({row['specialist']}, {row['difficulty']})", "",
                  f"**Question:** {row['question']}", "",
                  f"**Gold answer:** {row['expected_answer']}", "",
                  f"**Route:** expected {row['expected_route']}; delegated {record['metrics'].get('subagent_calls', {})}", "",
                  "<details><summary>Evidence retrieved during the run</summary>", "", "```", evidence, "```", "", "</details>", "",
                  "**Answer:**", "", record["answer"] or f"(agent error: {record.get('error')})", "", "---", ""]
    return "\n".join(parts)


def load_grades(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def blank_grade(row_id: str) -> dict:
    return {"id": row_id, "groundedness": None, "completeness": None, "report_quality": None, "notes": ""}


def parse_add(specs: list[str] | None) -> dict[str, int]:
    added = {}
    for spec in specs or []:
        key, _, count = spec.partition("=")
        added[key] = int(count or 0)
    return added


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", required=True)
    parser.add_argument("--n", type=int, default=25)
    parser.add_argument("--seed", type=int, default=3)
    parser.add_argument("--keep", action="store_true", help="reuse the ids in human_grades.jsonl instead of sampling")
    parser.add_argument("--add", nargs="*", metavar="SPECIALIST=N", help="with --keep: append N new rows of a specialist")
    args = parser.parse_args(argv)
    results = load_results(RUNS_DIR / args.run / "results.jsonl")
    rows = [r for r in load_rows() if r["id"] in results and results[r["id"]].get("answer")]
    out_dir = CALIBRATION_DIR / args.run
    out_dir.mkdir(parents=True, exist_ok=True)
    grades_path = out_dir / "human_grades.jsonl"
    grades = load_grades(grades_path)
    if args.keep:
        kept_ids = [g["id"] for g in grades]
        by_id = {r["id"]: r for r in rows}
        missing = [i for i in kept_ids if i not in by_id]
        if missing:
            print(f"ids in human_grades.jsonl without an answered result: {missing}", file=sys.stderr)
        chosen = [by_id[i] for i in kept_ids if i in by_id]
        for specialist, count in parse_add(args.add).items():
            pool = [r for r in rows if r["specialist"] == specialist and r["id"] not in kept_ids]
            extra = stratified_sample(pool, min(count, len(pool)), args.seed) if pool else []
            chosen.extend(extra)
            grades.extend(blank_grade(r["id"]) for r in extra)
        chosen.sort(key=lambda r: r["id"])
        grades.sort(key=lambda g: g["id"])
        with grades_path.open("w", encoding="utf-8") as sink:
            for grade in grades:
                sink.write(json.dumps(grade, ensure_ascii=False) + "\n")
    else:
        if len(rows) < args.n:
            print(f"only {len(rows)} answered rows available for {args.run}", file=sys.stderr)
        chosen = stratified_sample(rows, min(args.n, len(rows)), args.seed)
        if grades_path.exists():
            print(f"{grades_path} exists; not overwriting human grades (use --keep to extend it).")
        else:
            with grades_path.open("w", encoding="utf-8") as sink:
                for row in chosen:
                    sink.write(json.dumps(blank_grade(row["id"])) + "\n")
    (out_dir / "review_sheet.md").write_text(review_sheet(args.run, chosen, results), encoding="utf-8")
    print(f"{len(chosen)} rows in the sheet: {dict(Counter(r['specialist'] for r in chosen))}")
    print(f"Review sheet: {out_dir / 'review_sheet.md'}\nGrades file:  {grades_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
