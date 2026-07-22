import io
import json
import sys
from collections.abc import Callable
from . import config

TOOLS = [
    {
        "name": "farewell_helper_verify",
        "description": "Verify persona + skill injection system",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "farewell_helper_sync",
        "description": "Sync 9Router combos + resolve opencode config template",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "farewell_helper_start",
        "description": "Session start: validate persona, show active project, ready check",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "farewell_helper_daily",
        "description": "Health check + sync combo + resolve config template",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _capture(fn: Callable[[], None]) -> str:
    buf = io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = buf
    try:
        fn()
        return json.dumps({"stdout": buf.getvalue(), "stderr": "", "exit_code": 0})
    except SystemExit:
        return json.dumps({"stdout": buf.getvalue(), "stderr": "", "exit_code": 0})
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def _run_tool(name: str) -> str:
    if name == "farewell_helper_verify":
        from .commands.state import verify
        return _capture(verify)
    if name == "farewell_helper_sync":
        from .commands import _cmd_sync
        return _capture(_cmd_sync)
    if name == "farewell_helper_start":
        from .commands import _cmd_start
        return _capture(_cmd_start)
    if name == "farewell_helper_daily":
        from .commands import _cmd_daily
        return _capture(_cmd_daily)
    return json.dumps({"error": f"Unknown tool: {name}"})


def _read() -> dict:
    line = sys.stdin.readline()
    if not line:
        return {}
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return {}


def _write(msg: dict):
    data = json.dumps(msg)
    sys.stdout.write(data + "\n")
    sys.stdout.flush()


def serve() -> None:
    while True:
        msg = _read()
        if not msg:
            break
        msg_id = msg.get("id")
        method = msg.get("method", "")
        params = msg.get("params", {})

        if method == "initialize":
            _write({
                "jsonrpc": "2.0", "id": msg_id,
                "result": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "farewell-helper", "version": "5.0.0"},
                },
            })
        elif method == "notifications/initialized":
            pass
        elif method == "tools/list":
            _write({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            tool_name = params.get("name", "")
            raw = _run_tool(tool_name)
            try:
                parsed = json.loads(raw)
                text = parsed.get("stdout", raw)
                if parsed.get("stderr"):
                    text += "\n" + parsed["stderr"]
                _write({
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {"content": [{"type": "text", "text": text}]},
                })
            except json.JSONDecodeError:
                _write({
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {"content": [{"type": "text", "text": raw}]},
                })
        else:
            _write({
                "jsonrpc": "2.0", "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            })


def main() -> None:
    if "--stdio" in sys.argv:
        serve()
    else:
        print("Farewell Helper MCP Server")
        print("Usage: py -m farewell_helper.mcp --stdio")
        print("\nAvailable tools:")
        for t in TOOLS:
            print(f"  {t['name']}: {t['description']}")


if __name__ == "__main__":
    main()
