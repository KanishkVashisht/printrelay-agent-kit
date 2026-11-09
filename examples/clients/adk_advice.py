import asyncio
import json
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

async def main():
    sessions = InMemorySessionService()
    session = await sessions.create_session(app_name="cad_advice_demo", user_id="local_demo")
    context = ToolContext(InvocationContext(
        invocation_id="read_advice", agent=BaseAgent(name="cad_advice_demo"),
        session=session, session_service=sessions,
    ))
    toolset = McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="https://partsforagents.com/api/advice/mcp",
            timeout=15, sse_read_timeout=30,
        ),
        tool_filter=["get_manufacturing_advice"],
    )
    try:
        async with asyncio.timeout(60):
            tools = await toolset.get_tools()
            assert [tool.name for tool in tools] == ["get_manufacturing_advice"]
            result = await tools[0].run_async(args={"topic": "fits"}, tool_context=context)
            assert result["isError"] is False
            envelope = result["structuredContent"]
            assert envelope["ok"] is True
            print(json.dumps(envelope["data"], indent=2))
    finally:
        await toolset.close()

asyncio.run(main())
