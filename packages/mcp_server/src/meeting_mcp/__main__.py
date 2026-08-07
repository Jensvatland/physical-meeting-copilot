"""Entry point placeholder for MCP stdio server (Phase 7 transport wiring)."""

from __future__ import annotations

from meeting_mcp.server import RESOURCE_TEMPLATES, TOOL_NAMES, MeetingMCPFacade


def main() -> None:
    facade = MeetingMCPFacade()
    print("Physical Meeting Copilot MCP façade ready (stdio transport TBD in Phase 7).")
    print(f"tools={len(TOOL_NAMES)} resources={len(RESOURCE_TEMPLATES)}")
    print(f"active_session={facade._active_id}")


if __name__ == "__main__":
    main()
