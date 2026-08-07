"""Stdio MCP server entry point for Hermes / OpenClaw / other hosts."""

from __future__ import annotations

import asyncio
import sys

from meeting_mcp.server import RESOURCE_TEMPLATES, TOOL_NAMES, MeetingMCPFacade, build_mcp_server


def main() -> None:
    if "--list" in sys.argv:
        facade = MeetingMCPFacade()
        print(f"tools={len(TOOL_NAMES)} resources={len(RESOURCE_TEMPLATES)}")
        print(f"active_session={facade._active_id}")
        return
    server = build_mcp_server()
    asyncio.run(server.run_stdio_async())


if __name__ == "__main__":
    main()
