import os
from pathlib import Path
from typing import Optional


def resolve_path(filename: str, session_dir: Optional[str] = None) -> str:
    """
    统一的文件路径解析工具方法。
    Unified file path resolution utility.

    核心功能：
    Core behavior:
    1. 清洗虚拟路径前缀 (/workspace, /mnt/data, /home/user)
       Strip virtual path prefixes (/workspace, /mnt/data, /home/user)
    2. 识别 updated/ 目录，优先相对于项目根目录解析
       Detect updated/ and resolve it relative to the project root first
    3. 结合 session_dir 处理相对/绝对路径，保证路径隔离
       Combine with session_dir for relative/absolute paths to keep isolation
    4. 防止路径嵌套 (session_id/session_id)
       Prevent path nesting (session_id/session_id)

    场景示例（基于测试环境：Windows系统、session_dir=D:/Project/output/session_123、CWD=D:/Project）：
    Scenario examples (test env: Windows, session_dir=D:/Project/output/session_123, CWD=D:/Project):
    | 输入场景                | filename                          | session_dir                      | 核心操作                          | 最终结果                          |
    |-------------------------|-----------------------------------|----------------------------------|-----------------------------------|-----------------------------------|
    | 虚拟路径清洗            | /workspace/report.md              | D:/Project/output/session_123    | 剥离/workspace → 拼接到会话目录   | D:/Project/output/session_123/report.md |
    | updated/ 特殊处理       | abc/updated/upload/file.pdf       | D:/Project/output/session_123    | 提取updated/后路径 → 解析到CWD    | D:/Project/updated/upload/file.pdf |
    | 无会话目录              | sub/test.md                       | None                             | 直接解析为CWD下绝对路径           | D:/Project/sub/test.md            |
    | 绝对路径（会话内）      | D:/Project/output/session_123/sub/report.md | D:/Project/output/session_123 | 验证在会话内 → 无嵌套 → 直接返回  | D:/Project/output/session_123/sub/report.md |
    | 绝对路径（会话外）      | D:/OtherDir/file.md               | D:/Project/output/session_123    | 验证不在会话内 → 保留原路径       | D:/OtherDir/file.md               |
    | Windows Unix风格绝对路径 | /sub/test.md                      | D:/Project/output/session_123    | /开头无盘符 → 拼接到会话目录      | D:/Project/output/session_123/sub/test.md |
    | 路径嵌套防护            | D:/Project/output/session_123/session_123/report.md | D:/Project/output/session_123 | 检测连续session_123 → 修正路径   | D:/Project/output/session_123/report.md |
    | 相对路径（含session名） | session_123/report.md             | D:/Project/output/session_123    | 含session名 → 防止嵌套 → 会话目录+文件名 | D:/Project/output/session_123/report.md |
    | 相对路径（output前缀）  | output/report.md                  | D:/Project/output/session_123    | 含output前缀 → 会话目录+文件名    | D:/Project/output/session_123/report.md |
    | 普通相对路径            | sub1/sub2/test.md                 | D:/Project/output/session_123    | 无特殊标识 → 拼接到会话目录       | D:/Project/output/session_123/sub1/sub2/test.md |
    | 虚拟路径+updated        | /mnt/data/updated/doc.md          | D:/Project/output/session_123    | 剥离/mnt/data → 触发updated处理   | D:/Project/updated/doc.md         |
    | Linux系统绝对路径       | /home/user/test.md                | /data/session_123（Linux）       | 剥离/home/user → 拼接到Linux会话目录 | /data/session_123/test.md         |

    | Input scenario                    | filename                          | session_dir                      | Core action                                      | Result                            |
    |-----------------------------------|-----------------------------------|----------------------------------|---------------------------------------------------|-----------------------------------|
    | Virtual path strip                | /workspace/report.md              | D:/Project/output/session_123    | Strip /workspace → join to session dir            | D:/Project/output/session_123/report.md |
    | updated/ special case             | abc/updated/upload/file.pdf       | D:/Project/output/session_123    | Take path after updated/ → resolve vs CWD       | D:/Project/updated/upload/file.pdf |
    | No session dir                    | sub/test.md                       | None                             | Resolve as absolute under CWD                      | D:/Project/sub/test.md            |
    | Absolute path (in session)       | D:/Project/output/session_123/sub/report.md | D:/Project/output/session_123 | In session, no nest → return as-is                | D:/Project/output/session_123/sub/report.md |
    | Absolute path (outside session)   | D:/OtherDir/file.md               | D:/Project/output/session_123    | Outside session → keep original                    | D:/OtherDir/file.md               |
    | Windows Unix-style absolute path   | /sub/test.md                      | D:/Project/output/session_123    | Leading / no drive → join to session dir           | D:/Project/output/session_123/sub/test.md |
    | Nested-path guard                 | D:/Project/output/session_123/session_123/report.md | D:/Project/output/session_123 | Detect consecutive session_123 → fix path        | D:/Project/output/session_123/report.md |
    | Relative path (contains session name) | session_123/report.md         | D:/Project/output/session_123    | Contains session name → avoid nest → session dir + filename | D:/Project/output/session_123/report.md |
    | Relative path (output prefix)     | output/report.md                  | D:/Project/output/session_123    | output prefix → session dir + filename            | D:/Project/output/session_123/report.md |
    | Ordinary relative path             | sub1/sub2/test.md                 | D:/Project/output/session_123    | No special marker → join to session dir            | D:/Project/output/session_123/sub1/sub2/test.md |
    | Virtual path + updated            | /mnt/data/updated/doc.md          | D:/Project/output/session_123    | Strip /mnt/data → trigger updated handling           | D:/Project/updated/doc.md         |
    | Linux absolute path               | /home/user/test.md                | /data/session_123 (Linux)         | Strip /home/user → join to Linux session dir        | /data/session_123/test.md         |

    Args:
        filename (str): 输入的文件名或路径
                        Input filename or path
        session_dir (str, optional): 会话上下文目录
                                   Session context directory

    Returns:
        str: 解析后的绝对路径
             Resolved absolute path
    """
    path = Path(filename)
    path_str = filename.replace("\\", "/")  # 统一处理字符串匹配 / Normalize separators for string matching

    # 1. 虚拟路径清洗 / Strip virtual path prefixes
    virtual_prefixes = ["/workspace", "/mnt/data", "/home/user"]
    for prefix in virtual_prefixes:
        if path_str.startswith(prefix):
            # 去掉前缀 / Drop the prefix
            cleaned = path_str[len(prefix):].lstrip("/")
            path = Path(cleaned)
            path_str = str(path).replace("\\", "/")
            break

    # 2. 特殊处理：updated/ (用户上传文件) / Special case: updated/ (user-uploaded files)
    # 只要路径中包含 updated/，就提取其后半部分，并相对于 CWD 解析
    # If the path contains updated/, take the remainder and resolve relative to CWD
    if "updated/" in path_str:
        idx = path_str.find("updated/")
        relative_part = path_str[idx:]
        return str(Path(relative_part).resolve())

    if not session_dir:
        return str(path.resolve())

    session_path = Path(session_dir).resolve()
    session_name = session_path.name

    # 3. 结合 Session Context / Combine with session context

    # 检测 Unix 风格绝对路径 (以 / 开头) / Detect Unix-style absolute paths (leading /)
    is_unix_abs = path_str.startswith("/")

    # 如果是绝对路径 (Windows带盘符 或 Unix/开头)
    # Absolute path (Windows drive letter or Unix leading /)
    if path.is_absolute() or (os.name == 'nt' and is_unix_abs):
        # Windows 特殊情况：以 / 开头但无盘符，视为相对路径
        # Windows special case: leading / with no drive letter → treat as relative
        if os.name == 'nt' and is_unix_abs and not path.drive:
            full_path = session_path / path_str.lstrip("/")
        else:
            full_path = path.resolve()

        # 检查是否在 session 目录内 / Check whether the path is inside the session directory
        try:
            # 判断 full_path 是否是 session_path 的子路径
            # True if full_path is session_path or a descendant
            if session_path in full_path.parents or full_path == session_path:
                # 检查嵌套 (例如 .../session_abc/session_abc/file.txt)
                # Nested session dirs, e.g. .../session_abc/session_abc/file.txt
                # 检查路径部分中是否有连续重复的 session_name
                # Consecutive duplicate session_name in path parts
                parts = full_path.parts
                for i in range(len(parts) - 1):
                    if parts[i] == session_name and parts[i + 1] == session_name:
                        # 发现嵌套，修正为 session_dir / filename
                        # Nested — rewrite as session_dir / filename
                        return str(session_path / full_path.name)
                return str(full_path)
        except Exception:
            pass

        # 绝对路径但不在 session_dir 下 -> 保持原样
        # Absolute path outside session_dir → keep as-is
        return str(full_path)

    else:
        # 相对路径处理 / Relative path handling
        parts = path.parts

        # 检查是否包含 session_name (避免重复) 或 output/ 前缀
        # Contains session_name (avoid duplication) or an output/ prefix
        if session_name in parts:
            return str(session_path / path.name)

        if parts and parts[0] == "output":
            return str(session_path / path.name)

        # 默认：拼接到 session_dir / Default: join onto session_dir
        return str(session_path / path)
