"""Graders for the golden set: deterministic code graders and the LLM judge.

Code graders live in ``code.py`` and never call a network service except ``check_citations``,
which fetches cited URLs. ``judge.py`` wraps the Azure-hosted judge model with the rubrics in
``prompt/prompts.yaml`` (``evals.judge``). ``ragas_eval.py`` runs the Ragas RAG metrics on the
knowledge-base rows. promptfoo assertions in ``evals/promptfoo/asserts.py`` are thin adapters
over these functions so the same code grades in the harness, in tests, and in calibration.
"""
