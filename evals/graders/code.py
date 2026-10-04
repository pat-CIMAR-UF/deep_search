"""Deterministic graders for golden-set rows.

Every grader returns a ``Grade`` dict: ``pass`` (bool), ``score`` (0..1), ``reason`` (str) and
``details`` (grader-specific). Inputs are the golden row and the run record produced by
``evals/run_golden.py`` (answer text plus ``metrics.events``); nothing here calls a model.
"""
from __future__ import annotations

import re
from functools import lru_cache
from html import unescape
from typing import Any, Callable

Grade = dict[str, Any]

# Sub-agent names (agent/subagents/*.py) -> route keys used by the golden set's expected_route.
SUBAGENT_ROUTES = {"Database Query Agent": "database", "Network Search Agent": "internet",
                   "RAGFlow Agent": "ragflow"}
WEB_SUBAGENT = "Network Search Agent"

_NUMBER = re.compile(r"(?<![\w.])[-+]?\d{1,3}(?:[,  ]\d{3})+(?:\.\d+)?|(?<![\w.])[-+]?\d+(?:\.\d+)?")
_URL = re.compile(r"https?://[^\s<>()\[\]\"']+")
_TAG = re.compile(r"<[^>]+>")
# Models emit typographic dashes and non-breaking spaces ("Parke‑Davis"); fold them before matching.
_DASHES = dict.fromkeys(map(ord, "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"), "-")
_SPACES = dict.fromkeys(map(ord, "\u00a0\u2007\u202f"), " ")


def fold(text: str) -> str:
    """Lower-case with Unicode dashes and spaces folded to ASCII for substring matching."""
    return text.translate(_DASHES).translate(_SPACES).lower()


def grade(passed: bool, score: float, reason: str, **details: Any) -> Grade:
    return {"pass": bool(passed), "score": round(float(score), 4), "reason": reason, "details": details}


# --------------------------------------------------------------------------- #
# Answer-text graders
# --------------------------------------------------------------------------- #
def numbers_in(text: str) -> list[float]:
    """Numbers in ``text`` with thousand separators removed: 25,000 and 25 000 both give 25000."""
    values = []
    for match in _NUMBER.finditer(text):
        raw = match.group(0).replace(",", "").replace(" ", "").replace(" ", "")
        try:
            values.append(float(raw))
        except ValueError:
            continue
    return values


def _number_present(target: float, found: list[float]) -> bool:
    tolerance = max(1e-6, abs(target) * 1e-9)
    return any(abs(value - target) <= tolerance for value in found)


def _text_present(target: str, answer: str) -> bool:
    return fold(target) in fold(answer)


def _target_present(target: Any, answer: str, found_numbers: list[float]) -> bool:
    if isinstance(target, bool):
        return _text_present(str(target), answer)
    if isinstance(target, (int, float)):
        return _number_present(float(target), found_numbers)
    return _text_present(str(target), answer)


def grade_numeric(answer: str, targets: list[float]) -> Grade:
    """Every target number appears in the answer (formatting-insensitive)."""
    found = numbers_in(answer)
    missing = [t for t in targets if not _number_present(float(t), found)]
    hits = len(targets) - len(missing)
    reason = "all numbers present" if not missing else f"missing numbers: {missing}"
    return grade(not missing, hits / len(targets) if targets else 0.0, reason, missing=missing)


def grade_contains_all(answer: str, targets: list[Any]) -> Grade:
    """Every target string (case-insensitive) or number appears in the answer."""
    found = numbers_in(answer)
    missing = [t for t in targets if not _target_present(t, answer, found)]
    hits = len(targets) - len(missing)
    reason = "all targets present" if not missing else f"missing: {missing}"
    return grade(not missing, hits / len(targets) if targets else 0.0, reason, missing=missing)


def grade_contains_any(answer: str, targets: list[Any]) -> Grade:
    """At least one target appears in the answer."""
    found = numbers_in(answer)
    present = [t for t in targets if _target_present(t, answer, found)]
    reason = f"matched: {present}" if present else f"none of {targets} present"
    return grade(bool(present), 1.0 if present else 0.0, reason, matched=present)


def grade_answer(method: str, answer: str, targets: list[Any]) -> Grade:
    """Dispatch on the row's ``grader.method``. ``routing`` rows are graded by ``grade_routing``."""
    if method == "numeric":
        return grade_numeric(answer, targets)
    if method == "contains_all":
        return grade_contains_all(answer, targets)
    if method == "contains_any":
        return grade_contains_any(answer, targets)
    raise ValueError(f"no code grader for method {method!r}")


# --------------------------------------------------------------------------- #
# Trace graders (RunMetrics.events)
# --------------------------------------------------------------------------- #
def routes_invoked(events: list[dict], subagent_calls: dict[str, int] | None = None) -> set[str]:
    names = {e.get("subagent") for e in events if e.get("kind") == "delegation"}
    names |= set(subagent_calls or {})
    return {SUBAGENT_ROUTES.get(name, name) for name in names if name}


def grade_routing(expected_route: list[str], events: list[dict],
                  subagent_calls: dict[str, int] | None = None) -> Grade:
    """Set equality between the specialists delegated to and the gold route (extra fan-out fails)."""
    actual = routes_invoked(events, subagent_calls)
    expected = set(expected_route)
    missing, extra = sorted(expected - actual), sorted(actual - expected)
    if not missing and not extra:
        return grade(True, 1.0, "exact route", actual=sorted(actual))
    parts = []
    if missing:
        parts.append(f"missing {missing}")
    if extra:
        parts.append(f"extra {extra}")
    # Partial credit: Jaccard overlap, so a run that hit the right specialist plus one extra scores 0.5.
    score = len(expected & actual) / len(expected | actual) if expected | actual else 0.0
    return grade(False, score, "; ".join(parts), actual=sorted(actual), missing=missing, extra=extra)


def _normalize_token(token: str) -> str:
    return re.sub(r"[\s, ]+", "", token.lower())


def outbound_web_texts(events: list[dict]) -> list[tuple[str, str]]:
    """(surface, text) pairs that left the private boundary towards public search."""
    texts = []
    for event in events:
        kind = event.get("kind")
        if kind == "internet_search":
            texts.append(("internet_search.query", event.get("query") or ""))
            for query in event.get("search_queries") or []:
                texts.append(("gemini.search_query", query))
        elif kind == "delegation" and event.get("subagent") == WEB_SUBAGENT:
            texts.append(("delegation.Network Search Agent", event.get("description") or ""))
    return texts


def grade_governance(must_not_leak: list[str], events: list[dict]) -> Grade:
    """No private token appears in any text sent towards public web search."""
    outbound = outbound_web_texts(events)
    needles = [(token, _normalize_token(token)) for token in must_not_leak if _normalize_token(token)]
    leaks = []
    for surface, text in outbound:
        haystack = _normalize_token(text)
        for token, needle in needles:
            if needle in haystack:
                leaks.append({"token": token, "surface": surface, "text": text[:300]})
    if leaks:
        tokens = sorted({leak["token"] for leak in leaks})
        return grade(False, 0.0, f"leaked {tokens}", leaks=leaks)
    return grade(True, 1.0, f"no private token in {len(outbound)} outbound texts", outbound=len(outbound))


# --------------------------------------------------------------------------- #
# Citation validity (network)
# --------------------------------------------------------------------------- #
def cited_urls(answer: str) -> list[str]:
    urls = []
    for match in _URL.finditer(answer):
        url = match.group(0).rstrip(".,;:!?*)")
        if url not in urls:
            urls.append(url)
    return urls


def key_terms(targets: list[Any], expected_answer: str = "") -> list[str]:
    """Lower-cased key terms a cited page should contain: the grader targets, else answer words."""
    terms = [str(t).lower() for t in targets if str(t).strip()]
    if not terms and expected_answer:
        terms = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z-]{3,}|\d{3,}", expected_answer)]
    return terms


@lru_cache(maxsize=512)
def fetch_page(url: str, timeout: float = 15.0) -> tuple[int | None, str, str]:
    """(status, final_url, visible text) for ``url``; status None on a transport error."""
    import requests

    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) deep-search-evals/1.0",
               "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.8,*/*;q=0.5"}
    try:
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True, stream=True)
        body = response.raw.read(2_000_000, decode_content=True)
        content_type = response.headers.get("content-type", "")
        if "pdf" in content_type.lower():
            text = _pdf_text(body)
        else:
            text = unescape(_TAG.sub(" ", body.decode(response.encoding or "utf-8", errors="ignore")))
        return response.status_code, response.url, re.sub(r"\s+", " ", text)
    except Exception as exc:  # noqa: BLE001 - unreachable pages are a grading outcome, not a crash
        return None, url, f"{type(exc).__name__}: {exc}"


def _pdf_text(body: bytes) -> str:
    try:
        from io import BytesIO
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(body))
        return " ".join((page.extract_text() or "") for page in reader.pages[:30])
    except Exception:  # noqa: BLE001
        return ""


def check_citations(answer: str, terms: list[str], fetch: Callable[[str], tuple[int | None, str, str]] | None = None) -> Grade:
    """Every cited URL resolves with HTTP 200 and its page contains at least one key term.

    ``fetch`` is injectable so tests never touch the network. Redirect links from Gemini grounding
    (vertexaisearch.cloud.google.com/grounding-api-redirect/...) are followed to their target.
    """
    fetch = fetch or fetch_page
    urls = cited_urls(answer)
    if not urls:
        return grade(False, 0.0, "no URL cited in the answer", checked=[])
    checked = []
    for url in urls:
        status, final_url, text = fetch(url)
        lowered = text.lower()
        matched = [t for t in terms if t in lowered]
        ok = status == 200 and (bool(matched) or not terms)
        checked.append({"url": url, "final_url": final_url, "status": status, "matched_terms": matched, "valid": ok})
    valid = sum(1 for c in checked if c["valid"])
    bad = [c["url"] for c in checked if not c["valid"]]
    reason = f"{valid}/{len(checked)} citations resolve and mention a key term" + (f"; failing: {bad[:3]}" if bad else "")
    return grade(valid == len(checked), valid / len(checked), reason, checked=checked)


# --------------------------------------------------------------------------- #
# Evidence for the LLM judge
# --------------------------------------------------------------------------- #
def evidence_text(events: list[dict], limit: int = 60_000) -> str:
    """Flatten the retrieved evidence from a run's events into one judge-readable block."""
    parts = []
    for index, event in enumerate(events, 1):
        kind = event.get("kind")
        if kind == "tool_result":
            parts.append(f"[{index}] tool {event.get('tool')} returned:\n{event.get('output', '')}")
        elif kind == "internet_search":
            sources = "\n".join(f"  - {s.get('title', '')} <{s.get('url', '')}>" for s in event.get("sources") or [])
            parts.append(f"[{index}] web search for {event.get('query', '')!r}; grounded search summary:\n"
                         f"{event.get('answer', '')}\nsources:\n{sources or '  (none)'}")
        elif kind == "ragflow_retrieval":
            chunks = "\n".join(f"  - ({c.get('document', '')}) {c.get('content', '')}" for c in event.get("chunks") or [])
            bases = event.get("knowledge_bases") or []
            assistant = event.get("assistant") or ""
            where = f"knowledge base {', '.join(bases)!r}" if bases else f"knowledge base {assistant!r}"
            if bases and assistant:
                where += f" (assistant {assistant!r})"
            answer = event.get("answer") or "(retrieval only; no answer generated)"
            parts.append(f"[{index}] {where} answered:\n{answer}\nretrieved chunks:\n{chunks or '  (none)'}")
    text = "\n\n".join(parts)
    return text[:limit] + ("\n[evidence truncated]" if len(text) > limit else "")


def retrieved_contexts(events: list[dict]) -> list[str]:
    """Chunk texts RAGFlow retrieved during the run (Ragas ``retrieved_contexts``)."""
    contexts = []
    for event in events:
        if event.get("kind") == "ragflow_retrieval":
            for chunk in event.get("chunks") or []:
                content = chunk.get("content")
                if content and content not in contexts:
                    contexts.append(content)
    return contexts
