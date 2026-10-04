"""LLM-as-judge on an Azure-hosted judge model, with rubrics from ``prompt/prompts.yaml``.

Configuration (``.env``): ``AZURE_ENDPOINT`` (the resource's OpenAI-compatible ``/openai/v1`` base
URL), ``AZURE_API_KEY``, ``AZURE_DEPLOYMENT_NAME`` (default ``gpt-6.1-sol``), ``AZURE_REASONING_EFFORT``
(``low`` | ``medium`` | ``high``, default ``medium``).

Two backends on the same resource and key, chosen by deployment name:
- ``claude-*`` deployments go through the Anthropic SDK's Microsoft Foundry client (Azure serves Claude
  only on its Anthropic endpoint, not ``/openai/v1``): Messages API with ``output_config`` effort and a
  JSON-schema format. A refusal raises instead of falling back, so every verdict comes from one model.
- anything else uses the OpenAI SDK on ``/openai/v1``: GPT deployments reject ``temperature`` and
  ``max_tokens``, so requests send ``max_completion_tokens``, ``reasoning_effort`` and a strict JSON schema.
Ragas needs an OpenAI-API deployment; with a Claude judge it uses ``AZURE_RAGAS_DEPLOYMENT_NAME``
(default ``gpt-6.1-sol``).

Templates use ``{{name}}`` placeholders, filled by ``render``.
"""
from __future__ import annotations

import json
import os
import re
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_DEPLOYMENT = "gpt-6.1-sol"
DEFAULT_REASONING_EFFORT = "medium"
REASONING_EFFORTS = ("low", "medium", "high")
MAX_COMPLETION_TOKENS = 1500
CLAUDE_MAX_TOKENS = 16000  # thinking counts toward it; a verdict itself is a few hundred tokens
# gpt-6.1-sol occasionally spends the whole budget on reasoning and returns empty content (finish_reason
# "length"); a fresh attempt almost always answers. A larger budget only turns those into slow timeouts.
JUDGE_ATTEMPTS = 3
_PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")

GRADE_SCHEMA = {
    "type": "object",
    "properties": {
        "pass": {"type": "boolean"},
        "score": {"type": "number"},
        "reason": {"type": "string"},
        "unsupported_claims": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["pass", "score", "reason", "unsupported_claims"],
    "additionalProperties": False,
}

_client = None
_client_lock = threading.Lock()


def judge_prompts() -> dict[str, str]:
    from agent.prompts import prompt_yaml_content
    prompts = prompt_yaml_content.get("evals", {}).get("judge")
    if not prompts:
        raise RuntimeError("prompt/prompts.yaml has no evals.judge section")
    return prompts


def render(template: str, **values: Any) -> str:
    """Replace ``{{name}}`` placeholders; unknown names are left as-is."""
    return _PLACEHOLDER.sub(lambda m: str(values[m.group(1)]) if m.group(1) in values else m.group(0), template)


def judge_settings() -> dict[str, str]:
    from dotenv import find_dotenv, load_dotenv
    load_dotenv(find_dotenv(usecwd=True))
    endpoint = os.getenv("AZURE_ENDPOINT", "").rstrip("/")
    key = os.getenv("AZURE_API_KEY", "")
    if not endpoint or not key:
        raise RuntimeError("Set AZURE_ENDPOINT and AZURE_API_KEY in .env to use the LLM judge.")
    effort = (os.getenv("AZURE_REASONING_EFFORT") or DEFAULT_REASONING_EFFORT).strip().lower()
    if effort not in REASONING_EFFORTS:
        raise RuntimeError(f"AZURE_REASONING_EFFORT must be one of {REASONING_EFFORTS}, not {effort!r}.")
    model = os.getenv("AZURE_DEPLOYMENT_NAME") or DEFAULT_DEPLOYMENT
    return {"base_url": endpoint + "/", "api_key": key, "model": model, "reasoning_effort": effort,
            "provider": "anthropic" if model.startswith("claude-") else "openai",
            "resource": urlparse(endpoint).netloc.split(".")[0]}


def record_judge(run_dir: Path) -> str:
    """Write the judge deployment and grading time into ``run.json`` so the scorecard names the judge.

    Called by ``evals/promptfoo/eval.sh`` after promptfoo finishes; ``evals/score.py`` reads the ``judge`` key.
    """
    settings = judge_settings()
    path = run_dir / "run.json"
    meta = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"name": run_dir.name}
    meta["judge"] = settings["model"]
    meta["graded_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return settings["model"]


def _get_client():
    global _client
    with _client_lock:
        if _client is None:
            settings = judge_settings()
            if settings["provider"] == "anthropic":
                from anthropic import AnthropicFoundry
                _client = AnthropicFoundry(api_key=settings["api_key"], resource=settings["resource"],
                                           timeout=180, max_retries=4)
            else:
                from openai import OpenAI
                _client = OpenAI(base_url=settings["base_url"], api_key=settings["api_key"], timeout=120, max_retries=2)
        return _client


def _openai_call(settings: dict, prompt: str, system: str | None, schema: dict | None) -> tuple[str, int, int]:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    kwargs: dict[str, Any] = {"model": settings["model"], "messages": messages,
                              "max_completion_tokens": MAX_COMPLETION_TOKENS,
                              "reasoning_effort": settings["reasoning_effort"]}
    if schema is not None:
        kwargs["response_format"] = {"type": "json_schema",
                                     "json_schema": {"name": "grade", "strict": True, "schema": schema}}
    else:
        kwargs["response_format"] = {"type": "json_object"}
    response = _get_client().chat.completions.create(**kwargs)
    usage = getattr(response, "usage", None)
    return (response.choices[0].message.content or "",
            usage.prompt_tokens if usage else 0, usage.completion_tokens if usage else 0)


def _claude_call(settings: dict, prompt: str, system: str | None, schema: dict | None) -> tuple[str, int, int]:
    output_config: dict[str, Any] = {"effort": settings["reasoning_effort"]}
    if schema is not None:
        output_config["format"] = {"type": "json_schema", "schema": schema}
    kwargs: dict[str, Any] = {"model": settings["model"], "max_tokens": CLAUDE_MAX_TOKENS,
                              "messages": [{"role": "user", "content": prompt}], "output_config": output_config}
    if system:
        kwargs["system"] = system
    response = _get_client().messages.create(**kwargs)
    if response.stop_reason == "refusal":
        category = getattr(getattr(response, "stop_details", None), "category", None)
        raise RuntimeError(f"judge model refused the request (category: {category})")
    text = "".join(block.text for block in response.content if block.type == "text")
    return text, response.usage.input_tokens, response.usage.output_tokens


def complete_json(prompt: str, system: str | None = None, schema: dict | None = None) -> dict[str, Any]:
    """One judge call returning the parsed JSON object (strict schema when given)."""
    settings = judge_settings()
    call = _claude_call if settings["provider"] == "anthropic" else _openai_call
    prompt_tokens = completion_tokens = 0
    text = ""
    for _ in range(JUDGE_ATTEMPTS):
        text, used_in, used_out = call(settings, prompt, system, schema)
        prompt_tokens += used_in
        completion_tokens += used_out
        if text.strip():
            break
    data = parse_json(text)
    if prompt_tokens or completion_tokens:
        data["_usage"] = {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens}
    return data


def parse_json(text: str) -> dict[str, Any]:
    """Parse the judge's JSON, tolerating code fences or leading prose."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.S)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    raise ValueError(f"judge returned non-JSON output: {text[:200]!r}")


def normalize_grade(data: dict[str, Any]) -> dict[str, Any]:
    score = data.get("score")
    try:
        score = min(1.0, max(0.0, float(score)))
    except (TypeError, ValueError):
        score = 1.0 if data.get("pass") else 0.0
    return {"pass": bool(data.get("pass")), "score": round(score, 4), "reason": str(data.get("reason", "")),
            "unsupported_claims": list(data.get("unsupported_claims") or []),
            "usage": data.get("_usage")}


def judge_groundedness(question: str, answer: str, evidence: str) -> dict[str, Any]:
    prompts = judge_prompts()
    prompt = render(prompts["groundedness"], question=question, evidence=evidence or "(no evidence recorded)", answer=answer)
    return normalize_grade(complete_json(prompt, system=prompts["system"], schema=GRADE_SCHEMA))


def _rubric_call(rubric_key: str, question: str, answer: str, **values: Any) -> dict[str, Any]:
    prompts = judge_prompts()
    rubric = render(prompts[rubric_key], **values)
    prompt = render(prompts["rubric_prompt"], question=question, output=answer, rubric=rubric, **values)
    return normalize_grade(complete_json(prompt, system=prompts["system"], schema=GRADE_SCHEMA))


def judge_completeness(question: str, answer: str, expected_answer: str) -> dict[str, Any]:
    return _rubric_call("completeness", question, answer, expected_answer=expected_answer)


def judge_report_quality(question: str, answer: str) -> dict[str, Any]:
    result = _rubric_call("report_quality", question, answer)
    result["rating"] = rating_from_reason(result["reason"], result["score"])
    return result


def rating_from_reason(reason: str, score: float | None = None) -> int | None:
    """The 1-5 rating the report-quality rubric puts at the start of ``reason`` ("[rating 4/5]")."""
    match = re.search(r"rating\s*(\d)\s*/\s*5", reason or "", re.I)
    if match:
        return int(match.group(1))
    if score is not None:
        return max(1, min(5, round(score * 5)))
    return None


def build_judge_chat_model():
    """LangChain chat model for Ragas: the judge deployment, or an OpenAI-API one when the judge is Claude."""
    from langchain_openai import ChatOpenAI
    from pydantic import SecretStr
    settings = judge_settings()
    model = settings["model"]
    if settings["provider"] == "anthropic":
        model = os.getenv("AZURE_RAGAS_DEPLOYMENT_NAME") or DEFAULT_DEPLOYMENT
    return ChatOpenAI(model=model, base_url=settings["base_url"], api_key=SecretStr(settings["api_key"]),
                      reasoning_effort=settings["reasoning_effort"], timeout=120, max_retries=2)
