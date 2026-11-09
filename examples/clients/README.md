# Read manufacturing advice with FastMCP or Google ADK

These small, model-free Python examples connect to the public partsforagents MCP endpoint, discover the advice tool, request the `fits` topic, and print its sourced guidance. Neither needs an account, API key, model provider or CAD file. They do not create customer records, submit feedback, upload CAD, request a job, move money or control a printer.

Use Python 3.11+ in a virtual environment. The checks below were run on Python 3.14.8 on 2026-11-09; other Python versions were not tested in that run.

## FastMCP client

```sh
python3 -m venv .venv-fastmcp
.venv-fastmcp/bin/python -m pip install "fastmcp==4.1.6" "mcp==2.3.0"
.venv-fastmcp/bin/python examples/clients/fastmcp_advice.py
```

[`fastmcp_advice.py`](fastmcp_advice.py) uses `fastmcp.Client` over HTTP with a 30-second client timeout. The public server returned four tools; the script calls only `get_manufacturing_advice`. The catalog also includes a feedback write tool, which this example never calls.

## Google ADK toolset

```sh
python3 -m venv .venv-adk
.venv-adk/bin/python -m pip install "google-adk[mcp]==2.14.0" "mcp==2.3.0"
.venv-adk/bin/python examples/clients/adk_advice.py
```

[`adk_advice.py`](adk_advice.py) uses `McpToolset`, `StreamableHTTPConnectionParams`, and an in-memory ADK context without running an LLM. `tool_filter` exposes only `get_manufacturing_advice` to this example. Connection/read timeouts are 15/30 seconds, and the main operation has a 60-second cooperative timeout. The toolset is closed in `finally`. Dependency installation is outside those timeouts; SDK session-recovery behavior remains in place.

## Observed result and limits

Both exact scripts completed successfully on 2026-11-09 with the versions pinned above and MCP SDK 2.3.0. Each returned `method: "curated_guidance"`, `topic: "fits"`, questions about fit type and critical drawing tolerances, and a primary-source reference. The scripts assert both the MCP result status and the partsforagents application envelope's `ok` field.

These are our own read-only interoperability checks, not independent customer adoption or a model-backed agent evaluation. They do not prove that another host exposes the same tools, that a model uses the advice correctly, or that a part fits or is printable. Curated advice does not measure CAD, certify strength, set a universal tolerance, or issue a supplier quote.

For the next step, see the [complete enclosure example](../enclosure/) and [nonbinding request/offer workflow](../manual-fdm.md). Those authenticated workflows require separate authorization and exact-file/specification preservation. A request is not a paid or confirmed manufacturing order. Payment setup remains pending; review and explicit acceptance precede payment instructions.

Official client references: [FastMCP client](https://gofastmcp.com/docs/clients/client), [ADK MCP tools](https://adk.dev/tools-custom/mcp-tools/).
