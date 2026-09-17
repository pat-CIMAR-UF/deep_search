from contextvars import ContextVar
from typing import Optional

# =================================================================================================
# 核心知识点: ContextVars (上下文变量) / Core Concept: ContextVars (Context Variables)
# =================================================================================================
# Q: 为什么我们需要 ContextVar？为什么不能直接用全局变量？
#    Why do we need ContextVar? Why can't we just use global variables?
#
# A: 在开发异步 Web 服务 (如 FastAPI) 时，系统是 "并发" 处理多个用户请求的。
#    但在 Python 的 asyncio 机制下，这些并发请求通常运行在 *同一个线程 (Thread)* 中。
#    When developing asynchronous web services (e.g., FastAPI), the system handles multiple user
#    requests concurrently. Under Python's asyncio mechanism, these concurrent requests typically
#    run in the *same thread*.
#
#    1. 如果使用全局变量 (Global Variable) / If using global variables:
#       当 User A 的请求正在处理时，User B 的请求进来了。如果修改了全局变量，User A 的数据
#       就会被 User B 覆盖，导致严重的 "串台" 事故（例如 User A 的文件存到了 User B 的目录）。
#       When User A's request is being processed, User B's request arrives. Modifying a global
#       variable will overwrite User A's data with User B's data, leading to severe cross-talk
#       issues (e.g., User A's files being saved to User B's directory).
#
#    2. 如果使用 threading.local / If using threading.local:
#       它是基于线程隔离的。因为 asyncio 所有协程都在同一个线程跑，所以 threading.local
#       在异步场景下失效，无法隔离不同用户的请求。
#       It provides thread-based isolation. Since all asyncio coroutines run in the same thread,
#       threading.local fails in asynchronous scenarios and cannot isolate different user requests.
#
#    3. ContextVar 的解决方案 / The ContextVar solution:
#       ContextVar 是 Python 3.7+ 专门为异步编程设计的 "协程级局部变量"。
#       它能确保变量在每一个 asyncio Task (即每个用户请求) 中是 *独立隔离* 的。
#       无论代码调用多深，只要是在同一个请求链路（Context）中，get() 到的都是属于当前请求的数据。
#       ContextVar is a "coroutine-level local variable" specifically designed for asynchronous
#       programming in Python 3.7+. It guarantees that variables are *independently isolated*
#       within each asyncio Task (i.e., each user request). No matter how deep the call stack is,
#       as long as it's within the same request execution chain (Context), get() will retrieve data
#       belonging to the current request.
# =================================================================================================


# 定义 ContextVar 上下文变量 / Define ContextVar context variables
# -------------------------------------------------------------------------
# 这里的变量名只是一个标识符 (Identifier)，真正的值是存储在当前的 Context 环境中的。
# The variable name here is only an identifier; the actual value is stored in the current Context environment.

# - 作用 ：用来记录 “当前是谁在执行任务” 。
# - 场景 ：当 Agent 打印日志或者通过 WebSocket 给前端发消息时，它需要知道：“我现在是正在服务张三，还是李四？” 这样消息才不会发错人。
# - Purpose: Track "who is currently executing the task".
# - Scenario: When an Agent logs messages or sends updates to the frontend via WebSocket, it needs to know: "Am I currently serving User A or User B?" to prevent misdelivering messages.
_session_dir_ctx: ContextVar[Optional[str]] = ContextVar("session_dir", default=None)

# - 作用 ：用来记录 “当前是谁在执行任务” 。
# - 场景 ：当 Agent 打印日志或者通过 WebSocket 给前端发消息时，它需要知道：“我现在是正在服务张三，还是李四？” 这样消息才不会发错人。
# - Purpose: Track "who is currently executing the task".
# - Scenario: When an Agent logs messages or sends updates to the frontend via WebSocket, it needs to know: "Am I currently serving User A or User B?" to prevent misdelivering messages.
_thread_id_ctx: ContextVar[Optional[str]] = ContextVar("thread_id", default=None)
_run_id_ctx: ContextVar[Optional[str]] = ContextVar("run_id", default=None)


def get_run_context():
    return _run_id_ctx.get()


def set_run_context(run_id: str):
    return _run_id_ctx.set(run_id)


def reset_run_context(token):
    _run_id_ctx.reset(token)


def set_session_context(path: str):
    """
    设置当前请求链路的会话目录。通常在 Agent 开始执行任务前调用。
    Set the session directory for the current request execution chain. Typically called before an Agent begins executing a task.

    Returns:
        Token: 返回一个 Token 对象，后续可用它来恢复(reset)变量状态。
               Returns a Token object that can be used later to reset the variable state.
    """
    return _session_dir_ctx.set(path)


def get_session_context() -> Optional[str]:
    """
    获取当前请求链路的会话目录。可以在任何深层调用的工具函数中直接使用，无需层层传递参数。
    Get the session directory for the current request execution chain. Can be used directly in any deeply nested tool functions without passing parameters through every layer.
    """
    return _session_dir_ctx.get()


def set_thread_context(thread_id: str):
    """
    设置当前请求链路的 Thread ID。
    Set the Thread ID for the current request execution chain.
    """
    return _thread_id_ctx.set(thread_id)


def get_thread_context() -> Optional[str]:
    """
    获取当前请求链路的 Thread ID。
    Get the Thread ID for the current request execution chain.
    """
    return _thread_id_ctx.get()


def reset_session_context(session_token, thread_token=None):
    """
    清理/重置上下文。通常在请求处理结束 (finally 块) 中调用，防止内存泄漏或污染后续请求。
    Clean up / reset the context. Typically called after request processing finishes (in a finally block) to prevent memory leaks or polluting subsequent requests.
    """
    _session_dir_ctx.reset(session_token)
    if thread_token:
        _thread_id_ctx.reset(thread_token)


# =================================================================================================
# 运行指标 / Run metrics
# 评估脚本在调用 run_deep_agent 之前设置一个 RunMetrics，运行期间由回调和工具填充；
# API 路径不设置它，因此默认关闭，不影响正常请求。
# Evaluation scripts set a RunMetrics before calling run_deep_agent; callbacks and tools fill
# it during the run. The API path never sets it, so it is off by default.
# =================================================================================================
_run_metrics_ctx: ContextVar[Optional["RunMetrics"]] = ContextVar("run_metrics", default=None)


def set_run_metrics(metrics):
    return _run_metrics_ctx.set(metrics)


def get_run_metrics():
    return _run_metrics_ctx.get()


def reset_run_metrics(token):
    _run_metrics_ctx.reset(token)
