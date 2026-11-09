import asyncio
import json
from fastmcp import Client

async def main():
    async with Client("https://partsforagents.com/api/advice/mcp", timeout=30) as client:
        tools = await client.list_tools()
        assert "get_manufacturing_advice" in {t.name for t in tools}
        result = await client.call_tool("get_manufacturing_advice", {"topic": "fits"})
        assert result.is_error is False
        envelope = result.structured_content
        assert envelope["ok"] is True
        print(json.dumps(envelope["data"], indent=2))

asyncio.run(main())
