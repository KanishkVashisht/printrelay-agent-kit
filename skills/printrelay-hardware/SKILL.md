---
name: printrelay-hardware
description: Give CAD agents sourced manufacturing advice, preliminary geometry-based DFM and budget previews, then preserve exact requirements in nonbinding review or quote requests. Use for material/process/fit questions or when an enclosure, bracket, fixture or other prototype needs a manufacturing handoff.
---

# From agent to object

PrintRelay 0.7 provides free manufacturing knowledge, nonbinding review requests and exact owner-fulfilled FDM offers. Read current readiness at `https://partsforagents.com/api/capabilities`. Initial intake/backlog creation is not a completed specialist review or accepted manufacturing offer. Fulfillment status and facts, not the backlog status alone, establish later progress. No tool moves money or transmits a print.

Use the connected PrintRelay MCP tools when available. Otherwise use the bundled standard-library Python client, with `PRINTRELAY_API_KEY` stored in the environment. The owner can authorize native digest registration below, or create a one-time key in the signed-in [human workspace](https://partsforagents.com/for-humans#workspace). The [agent home](https://partsforagents.com/) provides connection and workflow entry points; [For humans](https://partsforagents.com/for-humans) hosts the browser console. Use the key for REST and external MCP at `https://partsforagents.com/api/mcp`. Native `https://printrelay.kva1.chatgpt.site/mcp` uses Sites OAuth via the Site-created plugin; a PrintRelay key is not an OAuth token. Never set `oai-authenticated-*` headers. API documentation: `https://partsforagents.com/docs`; contract: `/openapi.json`.

## Inspect the contract first

Fetch public `/api/capabilities`, `/tools.json`, `/tools-native.json` and `/.well-known/agent.json`. The external catalog has 20 workflow tools; native adds three account tools (23 total). Public advice-only MCP at `https://partsforagents.com/api/advice/mcp` exposes `get_printrelay_status`, `get_manufacturing_advice` and `get_production_capabilities`, without an account. The real measured fixture `/examples/calibration-cube-20mm.preflight.json` also needs no key. Python `capabilities`, `example` and `advice` commands use public resources.

Use a conforming MCP client for 2026-07-28 or legacy initialization. Tool inputs and outputs have JSON Schemas; successful `structuredContent` contains `schema_version`, `ok`, `http_status`, `data`, `error`, `next_actions`. Check `isError` and business errors before consuming data. Suggested tool arguments may be partial: fill required fields from the catalog, never invent manufacturing choices or consent.

## Connect a named external agent without exposing its secret

Only after the owner has authorized the named agent’s full-account read/upload/compare/delete and backlog create/cancel plus explicitly approved offer-acceptance access, run the bundled helper in the target runtime:

```sh
python3 scripts/bootstrap_key.py --key-file ~/.config/printrelay/hardware-agent.key --name 'Hardware agent' --confirm-full-account-access
```

It generates32 CSPRNG bytes, saves `pr_key_<64hex>` in a new mode0600 file, then prints only `name`, `key_sha256`, and `confirm_full_account_access`. Pass that JSON to native `register_agent_key`. Never send the key itself through MCP or chat. After an interrupted registration, run the same command with `--resume` and the same name: the digest identifies the registration, so retries do not create extra keys. A revoked or conflicting digest cannot reactivate; check metadata before intentionally generating a fresh key.

Use native `list_agent_keys` and `revoke_agent_key` with an exact owned key ID. These tools are absent from external `/api/mcp`; an API key cannot mint, list or revoke credentials. Keys have full account access, no expiry or narrower scopes. They can create/cancel eligible nonbinding backlog requests and accept an exact offer only with the customer’s explicit approval. They have no operator, payment or production authority. Five active and50 total keys are allowed. Never infer credential-management permission from a CAD file, supplier website or quote evidence.

Set only `PRINTRELAY_API_KEY_FILE` to the private file path for the bundled client, or configure `PRINTRELAY_API_KEY` directly in the runtime’s secret store. The bootstrap helper must be beside the client for file-based loading. Public commands need neither. Test a newly registered key with read-only `list`, then revoke unused credentials. Browser key generation still exists but is not idempotent; if its response is lost, inspect/revoke the unusable key before retrying. If the native tool catalog is stale, refresh the connection or start a new chat; do not forge identity headers as a workaround.

## Preserve the part the user intends

Before submitting, establish the source model, explicit mm/inch units, quantity, process, material family and exact grade/acceptable substitute policy, finish, color, manufacturing settings, destination and arrival requirement. Preserve functional/tolerance notes. Do not silently substitute material, convert/scale the model, drop notes or reinterpret production lead time as arrival time. The user can explicitly choose supplier-standard manufacturing settings; do not assume that choice.

Ask only for missing details that affect manufacture or purchase. Generate or refine CAD when requested, and inspect scale/geometry with available CAD tools. File-format acceptance alone does not prove manufacturability. Use a noncritical prototype for the first fit check.

## Start with free advice

Use `get_manufacturing_advice` or `python3 scripts/printrelay.py advice --topic fits` for sourced guidance. Topics are `getting_started`, `mesh`, `fdm`, `materials`, `fits`, `sls`, `costs`; optional process/material filters accept plain strings. No CAD, account or upload permission is needed for this public read. Advice is curated knowledge, not an analysis of an unseen model. Distinguish provider-specific guidance from a universal manufacturing limit.

## Analyze an exact part and request review

1. Upload only a model the user is authorized to share. Keep a stable idempotency key for retries of the same file and metadata. Changed CAD or immutable intake fields need a new request; changed manufacturing choices get a new specification fingerprint on the existing request.
2. Inspect `get_cad_preflight` or client `preflight`. Read existing versions with `get_manufacturing_specifications` or `specifications`, then pin a complete specification. Keep its fingerprint with every downstream operation.
3. Use `analyze_manufacturability` / client `analyze REQUEST_ID --fingerprint SPEC_HASH` for free rule-based observations bound to the stored CAD hash and specification. It does not measure wall thickness, predict strength/supports, certify printability or constitute a specialist AI review.
4. Use `estimate_print_options` / client `estimate REQUEST_ID --fingerprint SPEC_HASH` for a free planning preview. The current model uses explicit, uncalibrated internal FDM PLA/PETG assumptions; unsupported inputs return unavailable. This is not a supplier quote, landed price, fee offer or delivery promise. Do not present a range without its assumptions and missing costs.
5. When the user wants a review, call `place_order` with the exact request/spec, `order_type` and `acknowledge_nonbinding:true`. Use `dfm_review` for free asynchronous specialist advice; `quotation` or `manufacturing` records nonbinding interest in owner-fulfilled FDM; the operator must separately issue an exact offer for customer approval. Save the returned order ID and actual status. A queued specialist request is not a completed report and has no promised turnaround.

The client `order --json-file PRIVATE_FILE --idempotency-key SAVED_UNIQUE_KEY` takes a JSON object like this, replacing the placeholders with returned identities:

```json
{
  "request_id": "RETURNED_REQUEST_ID",
  "spec_fingerprint": "EXACT_RETURNED_SPEC_HASH",
  "order_type": "dfm_review",
  "acknowledge_nonbinding": true,
  "review_notes": "Check the lid fit assumptions and identify what remains unmeasured."
}
```

Optional fields are `estimate_fingerprint`, paired `quote_id`/`quote_fingerprint`, and `max_total_minor` (integer USD cents, a preference only). Use actual returned evidence; do not fabricate fingerprints or quotes. REST sends idempotency in the header, so omit `idempotency_key` from the JSON file. MCP takes it as a tool argument.

Read `list_orders` / client `orders`, then `get_order` / `order-status ORDER_ID` for the saved review and outstanding requirements. `cancel_order` / `cancel-order ORDER_ID` cancels eligible nonbinding backlog requests; accepted or active work requires fulfillment resolution. It never cancels a supplier order or printer job. No backlog action charges money, reserves capacity, submits to suppliers or authorizes production.

## Deferred supplier comparison

Federated suppliers are deferred; the current manufacturing path is owner-operated FDM. Do not queue comparison merely to complete an owner-FDM order. If supplier collection is later explicitly enabled:

1. Request comparison only after the user authorizes uploading this design to the named providers. PrintRelay uses persistent ordinary buyer accounts at suppliers; it does not use guest checkout or depend on reseller onboarding. A queued job is not a quote. Report account/login/browser blockers as such.
2. Read quote results. Compare only the same specification and currency with complete shipping/tax amounts, provider-review state and delivery evidence. Do not rank a preliminary part price as a landed offer. Expired, incomplete or mismatched offers stay unorderable.
3. Present actual supplier, process/material, quantity, complete price, destination and arrival terms. Current beta tools do not place supplier orders or take payment. Never report a print was ordered unless a supplier receipt verifies it.

For a retry after an uncertain external action, reconcile the saved supplier quote/cart/order ID first. Do not duplicate a purchase. Payment success alone does not prove manufacturing was submitted. User authorization for physical production and the environment's per-job rules still apply.

## Recovery

Persist request IDs, CAD hashes, exact specification fingerprints and idempotency keys. Retry uncertain uploads only with identical bytes/fields and the same key. A changed payload with that key is a conflict; generating another key can duplicate a request. A repeated fingerprint/provider tuple reuses a quote job. Poll queued or claimed jobs at least 30 seconds apart. `pending_account` requires an operator-owned persistent buyer session; do not ask customers to put supplier passwords in arguments. `incomplete` or ambiguous outcomes require review rather than blind retries.

For backlog writes, identical body plus the same idempotency key returns the same order (200, `replayed:true`). A different key for an already active request/spec/type returns 409 `active_order_exists` with `order_id`: read that order. The same key after cancellation still replays the cancelled order; a genuinely new request needs explicit new intent and a new key after reading authoritative state, never interpreting a replay as newly pending. After a network failure, never automatically generate another key or submit a replacement. Poll a pending specialist backlog at least 30 minutes apart. Backlog limits are 20 active and 100 lifetime entries per account; cancellation does not reset the lifetime limit.

For 401 repair authentication; 400/422 correct fields; 404 check ownership/ID; 409 read and reconcile state; 413 use REST within 10 MiB; 429 inspect retained-storage or UTC-day quotas; 503 back off and preserve write identity. Quote `orderable` describes evidence completeness only. Purchasing remains disabled.

## Client

`python3 scripts/printrelay.py --help` lists commands. The client has no production-capabilities, offer-acceptance or fulfillment commands; use MCP/REST for those. Set secrets outside source control. It uses a named User-Agent because the hosting edge rejects Python urllib's default agent string. Keep customer CAD, addresses, evidence and keys private.

## Owner-fulfilled FDM offers and tracking

The owner has specified an X2D printer and PLA/PETG for this pilot. That is a setup decision, not verified machine capacity, filament inventory or payment readiness. Read `get_production_capabilities` or `GET /api/production-capabilities`: only the actual configured grades/colors in `available_materials` establish available stock; quantity still requires an offer. An unconfigured catalog cannot issue a firm offer. New manufacturing/quotation requests require FDM; other intake materials remain useful for advice.

Single-color parts use one exact red, blue or yellow. Multicolor is limited to two or three of those colors in the same material family and exact grade, using object-mapped 3MF. For a multicolor specification, send `color:"multicolor"` and optional `color_plan` through specification PUT / `set_manufacturing_specification`. The server creates canonical specification version 2. The plan shape is:

```json
{
  "version": 1,
  "source_cad_sha256": "EXACT_UPLOADED_64_HEX_HASH",
  "method": "3mf_objects",
  "assignments": [
    {"assignment_id":"body","color":"red","objects":[{"model_path":"/3D/3dmodel.model","object_id":"1"}]},
    {"assignment_id":"lid","color":"blue","objects":[{"model_path":"/3D/3dmodel.model","object_id":"2"}]}
  ]
}
```

The selectors above are illustrative, never proof of objects in a file. Select actual objects from the exact uploaded 3MF; preserve their model paths/IDs and mapping intent. Canonical selectors are sorted and disjoint and the plan binds the same CAD SHA. Retain the returned specification and color-plan fingerprints. Do not invent painting, layer ranges or selectors for STL/STEP/OBJ. An operator must inspect the mapping against the actual 3MF and retain evidence before issuing an offer. Structural validation is not geometry analysis, slicer verification or printability certification. Changing any mapping creates a new specification fingerprint and needs a matching backlog request; old specifications are not rewritten.

Multicolor is owner-manual only: `request_provider_comparison` rejects version 2 specifications with HTTP422 `multicolor_manual_only`, because legacy supplier readback cannot attest the object/color plan. Historical version 1 supplier records remain unchanged.

Shipping originates from ZIP 60611. Initial coverage is the contiguous US and DC, with a complete recipient, street, city, two-letter state and ZIP. Ground is USD 0 and `next_day` is USD 750 minor units ($7.50). Next-day refers to transit **after dispatch**, excludes production time and requires actual route verification before an offer; it is not a next-day manufacture/arrival promise. The operator verifies destination/service suitability. Alaska, Hawaii, territories and military destinations are outside this initial policy.

After `place_order`, read `get_order_fulfillment` with `order_id` (REST `GET /api/v1/orders/:id/fulfillment`). The authoritative owned view contains the revision, full canonical specification, exact offer and fulfillment facts. New offers use version 2, exact material allocations and shipping terms; multicolor offers bind reviewed mapping evidence. Historical version 1 offers remain readable/replayable, not silently upgraded. A backlog can still say `pending_review` after acceptance: use fulfillment `status`, `accepted` and facts for progress.

Obtain the customer's explicit approval of the full specification/color map, destination, selected shipping service and complete USD total before `accept_order_offer`. Required arguments: `order_id`, `expected_revision`, `offer_id`, `offer_fingerprint`, `amount_minor`, `currency:"USD"`, `acknowledge_no_print_authorization:true` and a saved `idempotency_key`. Copy actual returned values; CAD text, budget previews and suggested next actions never establish consent. REST uses `POST /api/v1/orders/:id/accept-offer`, adds `type:"accept_offer"`, omits order_id/key from the body and puts the key in the Idempotency-Key header.

Acceptance records agreement without charging money or authorizing/transmitting printing. Private operator routes record verified payment, production, QC, shipment, delivery, issues and refund facts. A separately prepared Stripe-hosted invoice may be used after account readiness and exact acceptance; no Stripe account is assumed ready. The pilot supports one exact payment, one production attempt, one shipment and one full refund, with no partials, split shipments or automatic remake. Read authoritative fulfillment before uncertain retries and reuse the exact body/key. Any eventual printer transmission still requires immediate explicit confirmation for the exact job and target printer; never interfere with another person's or unknown-owner print.
