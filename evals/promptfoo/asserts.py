"""promptfoo Python assertions: thin adapters over ``evals/graders``.

Each function receives ``(output, context)``; ``context["vars"]`` holds the golden row fields set
by golden_tests.py and ``context["providerResponse"]["metadata"]`` the run trace from provider.py.
They return promptfoo GradingResult dicts (``pass``, ``score``, ``reason``, ``namedScores``).
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evals.graders import code  # noqa: E402
from evals.promptfoo.provider import decode_list  # noqa: E402


def _metadata(context: dict) -> dict:
    return ((context or {}).get("providerResponse") or {}).get("metadata") or {}


def _list(context: dict, name: str) -> list:
    """A list var of the test case (JSON-encoded by golden_tests.py)."""
    return decode_list((context.get("vars") or {}).get(name))


def _result(grade: dict, **named: float) -> dict:
    return {"pass": grade["pass"], "score": grade["score"], "reason": grade["reason"], "namedScores": named}


def _agent_error(output: str, context: dict) -> dict | None:
    """A failed row with no answer is graded as failed without running the grader."""
    meta = _metadata(context)
    if meta.get("error") and not (output or "").strip():
        return {"pass": False, "score": 0.0, "reason": f"agent error: {meta['error']}"}
    return None


def answer(output: str, context: dict) -> dict:
    if failed := _agent_error(output, context):
        return failed
    return _result(code.grade_answer(context["vars"]["grader_method"], output or "", _list(context, "grader_targets")))


def routing(output: str, context: dict) -> dict:
    meta = _metadata(context)
    grade = code.grade_routing(_list(context, "expected_route"), meta.get("events") or [], meta.get("subagent_calls") or {})
    return _result(grade, routing_exact=1.0 if grade["pass"] else 0.0,
                   routing_extra=1.0 if grade["details"].get("extra") else 0.0,
                   routing_missing=1.0 if grade["details"].get("missing") else 0.0)


def governance(output: str, context: dict) -> dict:
    meta = _metadata(context)
    return _result(code.grade_governance(_list(context, "must_not_leak"), meta.get("events") or []))


def citations(output: str, context: dict) -> dict:
    vars_ = context["vars"]
    terms = code.key_terms(_list(context, "grader_targets"), vars_.get("expected_answer", ""))
    grade = code.check_citations(output or "", terms)
    return _result(grade, citation_count=float(len(grade["details"].get("checked", []))))


def groundedness(output: str, context: dict) -> dict:
    from evals.graders.judge import judge_groundedness
    if failed := _agent_error(output, context):
        return failed
    meta = _metadata(context)
    evidence = meta.get("evidence") or code.evidence_text(meta.get("events") or [])
    verdict = judge_groundedness(context["vars"]["question"], output or "", evidence)
    reason = verdict["reason"]
    if verdict["unsupported_claims"]:
        reason += " Unsupported: " + "; ".join(verdict["unsupported_claims"][:5])
    return {"pass": verdict["pass"], "score": verdict["score"], "reason": reason,
            "namedScores": {"unsupported_claims": float(len(verdict["unsupported_claims"]))}}


# Completeness and report quality are Python assertions rather than promptfoo `llm-rubric`: a file://
# grading provider gets its own Python worker pool per assertion, and promptfoo 0.123 keeps every pool
# alive until the eval ends (hundreds of idle interpreters on a full run). These run once and exit.
def completeness(output: str, context: dict) -> dict:
    from evals.graders.judge import judge_completeness
    if failed := _agent_error(output, context):
        return failed
    vars_ = context["vars"]
    return _result(judge_completeness(vars_["question"], output or "", vars_["expected_answer"]))


def report_quality(output: str, context: dict) -> dict:
    from evals.graders.judge import judge_report_quality
    if failed := _agent_error(output, context):
        return failed
    verdict = judge_report_quality(context["vars"]["question"], output or "")
    return _result(verdict, report_quality_rating=float(verdict["rating"] or 0))
