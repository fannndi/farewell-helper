import json
import sys
import subprocess
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

_CMD_MAP = {
    "farewell_helper_verify": ["verify"],
    "farewell_helper_sync": ["sync"],
    "farewell_helper_start": ["start"],
    "farewell_helper_daily": ["daily"],
}


def _run_tool(name: str) -> str:
    args = _CMD_MAP.get(name)
    if not args:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        r = subprocess.run(
            [sys.executable, "-m", "farewell_helper"] + args,
            capture_output=True, text=True, timeout=60,
            cwd=str(config.ROOT_DIR),
        )
        return json.dumps({"stdout": r.stdout, "stderr": r.stderr, "exit_code": r.returncode})
    except Exception as e:
        return json.dumps({"error": str(e)})


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


def serve():
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


def main():
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
