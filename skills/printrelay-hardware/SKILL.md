---
name: printrelay-hardware
description: Submit CAD prototypes to PrintRelay, pin manufacturing requirements, and request evidence-backed supplier quote comparisons. Use when a user wants an AI-designed enclosure, bracket, fixture, or other prototype manufactured.
---

# From agent to object

PrintRelay turns a CAD file and precise requirements into a tracked manufacturing request. Read current readiness at `https://printrelay.kva1.chatgpt.site/api/capabilities`; beta availability is not proof of live quotes or ordering.

Use the connected PrintRelay MCP tools when available. Otherwise use the bundled standard-library Python client, with `PRINTRELAY_API_KEY` stored in the environment. An account owner creates this revocable key after signing in at the site. Use the key for REST and external MCP at `https://printrelay.kva1.chatgpt.site/api/mcp`. Native `/mcp` uses Sites OAuth via the Site-created plugin; a PrintRelay key is not an OAuth token. Never set `oai-authenticated-*` headers. API documentation: `https://printrelay.kva1.chatgpt.site/docs`; contract: `/openapi.json`.

## Inspect the contract first

Fetch public `/api/capabilities`, `/tools.json` and `/.well-known/agent.json`. The real measured fixture `/examples/calibration-cube-20mm.preflight.json` needs no key. The Python `capabilities` and `example` commands fetch these public results. `get_printrelay_status` provides the current machine contract after connecting MCP.

Use a conforming MCP client for 2026-07-28 or legacy initialization. Tool inputs and outputs have JSON Schemas; successful `structuredContent` contains `schema_version`, `ok`, `http_status`, `data`, `error`, `next_actions`. Check `isError` and business errors before consuming data. Suggested tool arguments may be partial: fill required fields from the catalog, never invent manufacturing choices or consent.

## Preserve the part the user intends

Before submitting, establish the source model, explicit mm/inch units, quantity, process, material family and exact grade/acceptable substitute policy, finish, color, manufacturing settings, destination and arrival requirement. Preserve functional/tolerance notes. Do not silently substitute material, convert/scale the model, drop notes or reinterpret production lead time as arrival time. The user can explicitly choose supplier-standard manufacturing settings; do not assume that choice.

Ask only for missing details that affect manufacture or purchase. Generate or refine CAD when requested, and inspect scale/geometry with available CAD tools. File-format acceptance alone does not prove manufacturability. Use a noncritical prototype for the first fit check.

## Submit and compare

1. Upload only a model the user is authorized to share. Use a stable idempotency key for retries of the same file and requirements. A changed part is a new request.
2. Inspect geometry with `get_cad_preflight` or the client `preflight` command. Resume pinned versions with `get_manufacturing_specifications` or `specifications`. Save a complete specification. Its fingerprint binds the original CAD hash, units, quantity, exact requirements and destination. Keep that fingerprint with every downstream operation.
3. Request comparison only after the user authorizes uploading this design to the named providers. PrintRelay uses persistent ordinary buyer accounts at suppliers; it does not use guest checkout or depend on reseller onboarding. A queued job is not a quote. Report account/login/browser blockers as such.
4. Read quote results. Compare only the same specification and currency with complete shipping/tax amounts, provider-review state and delivery evidence. Do not rank a preliminary part price as a landed offer. Expired, incomplete or mismatched offers stay unorderable.
5. Present actual supplier, process/material, quantity, complete price, destination and arrival terms. Current beta tools do not place orders or take payment. Never report a print was ordered unless a supplier receipt verifies it.

For a retry after an uncertain external action, reconcile the saved supplier quote/cart/order ID first. Do not duplicate a purchase. Payment success alone does not prove manufacturing was submitted. User authorization for physical production and the environment's per-job rules still apply.

## Recovery

Persist request IDs, CAD hashes, exact specification fingerprints and idempotency keys. Retry uncertain uploads only with identical bytes/fields and the same key. A changed payload with that key is a conflict; generating another key can duplicate a request. A repeated fingerprint/provider tuple reuses a quote job. Poll queued or claimed jobs at least 30 seconds apart. `pending_account` requires an operator-owned persistent buyer session; do not ask customers to put supplier passwords in arguments. `incomplete` or ambiguous outcomes require review rather than blind retries.

For 401 repair authentication; 400/422 correct fields; 404 check ownership/ID; 409 read and reconcile state; 413 use REST within 10 MiB; 429 inspect retained-storage or UTC-day quotas; 503 back off and preserve write identity. Quote `orderable` describes evidence completeness only. Purchasing remains disabled.

## Client

`python3 scripts/printrelay.py --help` lists commands. Set secrets outside source control. It uses a named User-Agent because the hosting edge rejects Python urllib's default agent string. Keep customer CAD, addresses, evidence and keys private.
