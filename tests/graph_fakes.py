"""Scripted chat model for driving the real DeepAgents graph without a provider."""
import importlib

from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel

from agent import main_agent


class ScriptedToolModel(FakeMessagesListChatModel):
    """Replays the given AIMessages in order; tool bindings are accepted and ignored."""

    def bind_tools(self, tools, **kwargs):
        return self

    def get_num_tokens_from_messages(self, messages, tools=None):
        return sum(len(str(message.content)) // 4 for message in messages)


def install_model(monkeypatch, responses):
    """Make the next get_main_agent() build the graph on a model that replays ``responses``."""
    model = ScriptedToolModel(responses=responses)
    monkeypatch.setattr(importlib.import_module("agent.llm"), "llm", model)
    monkeypatch.setattr(main_agent, "main_agent", None)
    return model
