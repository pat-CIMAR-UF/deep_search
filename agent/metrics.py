"""Per-run usage accounting: tokens, model calls, tool calls, and sub-agent delegations.

`RunMetrics` is opt-in. `run_deep_agent()` attaches `UsageCallbackHandler` only when a caller
has installed a `RunMetrics` through `api.context.set_run_metrics`, so the API path pays nothing.
LangChain callbacks propagate into the sub-agent graphs, which is why this counts specialist
model calls and tool calls that the coordinator's own update stream never surfaces.
"""
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


@dataclass
class RunMetrics:
    input_tokens: int = 0
    output_tokens: int = 0
    llm_calls: int = 0
    tool_calls: Counter = field(default_factory=Counter)
    subagent_calls: Counter = field(default_factory=Counter)
    # Gemini grounding runs inside internet_search and is billed separately from the coordinator.
    gemini_calls: int = 0
    gemini_input_tokens: int = 0
    gemini_output_tokens: int = 0
    # Ordered tool events for evaluation graders: sub-agent delegations, outbound web queries
    # and their sources, and the chunks RAGFlow retrieved. Recorded only when metrics are installed.
    events: list[dict] = field(default_factory=list)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def tool_call_count(self) -> int:
        return sum(self.tool_calls.values())

    def add_usage(self, usage: dict | None) -> None:
        """Add a LangChain `usage_metadata` mapping (input_tokens / output_tokens)."""
        if not usage:
            return
        self.input_tokens += int(usage.get("input_tokens") or 0)
        self.output_tokens += int(usage.get("output_tokens") or 0)

    def add_gemini_usage(self, prompt_tokens: int | None, candidate_tokens: int | None) -> None:
        self.gemini_calls += 1
        self.gemini_input_tokens += int(prompt_tokens or 0)
        self.gemini_output_tokens += int(candidate_tokens or 0)

    def add_event(self, kind: str, **data: Any) -> None:
        """Append one tool event (``delegation``, ``internet_search``, ``ragflow_retrieval``)."""
        self.events.append({"kind": kind, **data})

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["tool_calls"] = dict(sorted(self.tool_calls.items()))
        data["subagent_calls"] = dict(sorted(self.subagent_calls.items()))
        data["total_tokens"] = self.total_tokens
        data["tool_call_count"] = self.tool_call_count
        return data


class UsageCallbackHandler(BaseCallbackHandler):
    """Accumulate model usage and tool calls from coordinator and sub-agent runs alike."""

    def __init__(self, metrics: RunMetrics):
        super().__init__()
        self.metrics = metrics

    def on_chat_model_start(self, serialized, messages, **kwargs) -> None:
        self.metrics.llm_calls += 1

    def on_llm_start(self, serialized, prompts, **kwargs) -> None:
        self.metrics.llm_calls += 1

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        counted = False
        for generations in response.generations:
            for generation in generations:
                usage = getattr(getattr(generation, "message", None), "usage_metadata", None)
                if usage:
                    self.metrics.add_usage(usage)
                    counted = True
        if not counted and response.llm_output:
            usage = response.llm_output.get("token_usage") or response.llm_output.get("usage") or {}
            self.metrics.add_usage({"input_tokens": usage.get("prompt_tokens"),
                                    "output_tokens": usage.get("completion_tokens")})

    # Tool results kept as grounding evidence for the LLM judge (web and RAGFlow tools record their own
    # events): the MongoDB tools plus the file tools whose output the coordinator may describe.
    EVIDENCE_TOOLS = frozenset({"find_documents", "aggregate_documents", "count_documents",
                                "list_collections", "get_collection_schema",
                                "read_file_content", "ls", "read_file", "glob", "grep"})
    EVIDENCE_CHARS = 20_000

    def on_tool_end(self, output, **kwargs) -> None:
        name = kwargs.get("name")
        if name not in self.EVIDENCE_TOOLS:
            return
        text = getattr(output, "content", output)
        if not isinstance(text, str):
            text = str(text)
        self.metrics.add_event("tool_result", tool=name, output=text[:self.EVIDENCE_CHARS])

    def on_tool_start(self, serialized, input_str, *, inputs=None, **kwargs) -> None:
        name = kwargs.get("name") or (serialized or {}).get("name") or "unknown"
        self.metrics.tool_calls[name] += 1
        if name == "task":
            args = inputs if isinstance(inputs, dict) else {}
            target = args.get("subagent_type")
            self.metrics.subagent_calls[target or "unknown"] += 1
            self.metrics.add_event("delegation", subagent=target or "unknown",
                                   description=str(args.get("description") or ""))
