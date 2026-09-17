"""ContextVar isolation guarantees that tools rely on."""
import asyncio

from api import context


def test_session_and_thread_context_round_trip():
    assert context.get_session_context() is None or isinstance(context.get_session_context(), str)
    session_token = context.set_session_context("/tmp/session_x")
    thread_token = context.set_thread_context("thread-x")
    run_token = context.set_run_context("run-x")
    try:
        assert context.get_session_context() == "/tmp/session_x"
        assert context.get_thread_context() == "thread-x"
        assert context.get_run_context() == "run-x"
    finally:
        context.reset_run_context(run_token)
        context.reset_session_context(session_token, thread_token)
    assert context.get_run_context() is None


def test_reset_without_thread_token_keeps_thread_context():
    thread_token = context.set_thread_context("keep-me")
    session_token = context.set_session_context("/tmp/a")
    context.reset_session_context(session_token)
    try:
        assert context.get_thread_context() == "keep-me"
    finally:
        context.reset_session_context(context.set_session_context(None), thread_token)


def test_concurrent_tasks_see_their_own_context():
    async def worker(name):
        session_token = context.set_session_context(f"/tmp/session_{name}")
        thread_token = context.set_thread_context(name)
        try:
            await asyncio.sleep(0)
            return context.get_session_context(), context.get_thread_context()
        finally:
            context.reset_session_context(session_token, thread_token)

    async def run():
        return await asyncio.gather(worker("alice"), worker("bob"))

    results = asyncio.run(run())
    assert results == [("/tmp/session_alice", "alice"), ("/tmp/session_bob", "bob")]
