"""
SentinelPay AI — Root Model Context Protocol (MCP) Server Entrypoint.
Usage with Claude Desktop, Cursor, or Gemini CLI:
  python mcp_server.py
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_path))

from app.mcp.server import run_stdio_server
import asyncio

if __name__ == "__main__":
    asyncio.run(run_stdio_server())
