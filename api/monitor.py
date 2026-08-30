import datetime
import asyncio
from typing import Any, Dict, Optional
from fastapi import WebSocket
from api.context import get_thread_context

# 尝试导入全局运行时（用于脚本模式下的流式输出） / Try to import global runtime (used for streaming output in script mode)
try:
    import builtins
except ImportError:
    builtins = None


class ToolMonitor:
    """
    工具监控类，用于在工具执行过程中上报进度和状态。
    设计为单例模式，可在任何工具中直接导入使用。
    兼容 FastAPI WebSocket 和 脚本运行时的 stream_writer。

    Tool monitor class used to report progress and status during tool execution.
    Designed as a singleton pattern, can be directly imported and used in any tool.
    Compatible with FastAPI WebSocket and script runtime stream_writer.

    使用示例 / Usage Example:
    from api.monitor import monitor

    def my_tool(arg1):
        monitor.report_tool("my_tool", {"arg1": arg1})
        ...
        monitor.report_task_result(result)
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolMonitor, cls).__new__(cls)
            cls._instance.websocket_manager = None  # 预留给 FastAPI WebSocketManager / Reserved for FastAPI WebSocketManager
        return cls._instance

    def set_websocket_manager(self, manager):
        """设置 FastAPI 的 WebSocket 管理器 / Set the FastAPI WebSocket manager"""
        self.websocket_manager = manager

    def _emit(self, event_type: str, message: str, data: Optional[Dict[str, Any]] = None):
        """内部发送方法 / Internal emit method"""
        payload = {
            "type": "monitor_event",
            "event": event_type,
            "message": message,
            "data": data or {},
            "timestamp": datetime.datetime.now().isoformat()
        }

        # 1. 优先尝试通过 FastAPI WebSocket 发送 (定向推送) / 1. Prefer sending via FastAPI WebSocket (targeted push)
        if self.websocket_manager:
            try:
                # 获取当前线程 ID / Get current thread ID
                thread_id = get_thread_context()

                # 确保 loop 已加载 / Ensure loop is loaded
                manager_loop = self.websocket_manager.loop

                if manager_loop:
                    if thread_id:
                        # 检查当前是否在同一个事件循环中 / Check if currently in the same event loop
                        try:
                            current_loop = asyncio.get_running_loop()
                        except RuntimeError:
                            current_loop = None

                        if current_loop and current_loop == manager_loop:
                            # 如果在同一个循环中（例如在 create_task 中运行），直接创建任务 / If in the same loop (e.g., running within create_task), create task directly
                            current_loop.create_task(
                                self.websocket_manager.send_to_thread(payload, thread_id)
                            )
                        else:
                            # FastAPI 的 WebSocket 依赖异步事件循环，且协程必须在创建它的循环中运行：
                            # - 如果当前线程和 WebSocket 管理器在同一个循环（比如在 FastAPI 的接口 / 任务中运行）：直接 create_task 效率最高；
                            # - 如果在不同循环 / 不同线程（比如同步线程调用）：必须用 asyncio.run_coroutine_threadsafe（线程安全的方式），否则会报错 “协程在错误的循环中运行”。
                            # FastAPI's WebSocket relies on an async event loop, and coroutines must run in the loop where they were created:
                            # - If current thread and WebSocket manager are in the same loop (e.g., running in FastAPI endpoint/task): create_task directly for highest efficiency;
                            # - If in different loop / different thread (e.g., called from synchronous thread): must use asyncio.run_coroutine_threadsafe (thread-safe way), otherwise it raises "Coroutine running in wrong loop".
                            # 如果在不同线程，使用 threadsafe 方法 / If in a different thread, use threadsafe method
                            asyncio.run_coroutine_threadsafe(
                                self.websocket_manager.send_to_thread(payload, thread_id),
                                manager_loop
                            )
                    else:
                        # 如果没有 thread_id，说明可能是系统级消息，或者未在上下文环境中 / If no thread_id, indicates it may be a system-level message, or outside of context
                        pass
            except Exception as e:
                print(f"[Monitor] WebSocket send failed: {e}")

        # 2. 尝试通过全局 runtime 输出 (DeepAgents 脚本模式) / 2. Try outputting via global runtime (DeepAgents script mode)
        # 这使得 simple_agents.py 中的 MockRuntime 能接收到数据 / This allows MockRuntime in simple_agents.py to receive data
        if builtins and hasattr(builtins, 'runtime') and hasattr(builtins.runtime, 'stream_writer'):
            try:
                builtins.runtime.stream_writer(payload)
            except Exception:
                pass

        # 3. 控制台保底输出 (方便调试) / 3. Fallback console output (for debugging convenience)
        # 加上特殊前缀，方便肉眼识别 / Prefix with special tag for easy visual identification
        print(f"\n[Monitor:{event_type}] {message}")

    def report_tool(self, tool_name: str, args: Dict[str, Any] = None):
        """报告工具开始执行 / Report tool execution start"""
        self._emit("tool_start", f"Tool execution started: {tool_name}", {"tool_name": tool_name, "args": args})

    def report_assistant(self, assistant_name: str, args: Dict[str, Any] = None):
        """报告正在调用的子智能体进度 / Report progress of invoked assistant"""
        self._emit("assistant_call", f"Calling assistant: {assistant_name}",
                   {"assistant_name": assistant_name, "args": args})

    def report_task_result(self, result: str):
        """报告任务最终结果 / Report final task result"""
        self._emit("task_result", "Task execution completed", {"result": result})

    def report_session_dir(self, path: str):
        """报告任务工作目录 / Report task working directory"""
        self._emit("session_created", f"Working directory created: {path}", {"path": path})


# 全局单例实例 / Global singleton instance
monitor = ToolMonitor()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        # 延迟绑定 loop，防止初始化时 loop 不一致 / Lazily bind loop to prevent loop mismatch during initialization
        self.loop = None

    def set_loop(self, loop):
        """显式设置事件循环 / Explicitly set event loop"""
        self.loop = loop
        monitor.set_websocket_manager(self)
        print(f"[Monitor] ConnectionManager manually bound to loop: {id(self.loop)}")

    async def connect(self, websocket: WebSocket, thread_id: str):
        await websocket.accept()
        self.active_connections[thread_id] = websocket
        print(f"Client connected: {thread_id}")

    def disconnect(self, websocket: WebSocket, thread_id: str):
        if thread_id in self.active_connections:
            del self.active_connections[thread_id]
        print(f"Client disconnected: {thread_id}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_to_thread(self, message: dict, thread_id: str):
        if thread_id in self.active_connections:
            websocket = self.active_connections[thread_id]
            await websocket.send_json(message)


manager = ConnectionManager()