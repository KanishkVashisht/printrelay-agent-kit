# One exact FDM offer, then tracked fulfillment

This is the PrintRelay 0.6 customer workflow for owner-operated FDM. It does not submit to a supplier, move money or send printer commands. Free advice and specialist DFM review remain separate from a manufacturing offer. Read [current capabilities](https://partsforagents.com/api/capabilities) before beginning; the default stock, printer and payment configuration is not ready.

Use external MCP at `https://partsforagents.com/api/mcp` with an account key, or native `https://printrelay.kva1.chatgpt.site/mcp` through Sites OAuth. The bundled Python CLI supports intake, specifications and nonbinding requests, but **has no production-capabilities, fulfillment or offer-acceptance commands**. Use the tools or REST routes below for those operations. [Tool schemas](https://partsforagents.com/tools.json) and [OpenAPI](https://partsforagents.com/openapi.json) are authoritative.

## Check stock and preserve the exact part

Call `get_production_capabilities` with `{}`, or read public `GET https://partsforagents.com/api/production-capabilities`. It is also one of the three tools on unauthenticated `/api/advice/mcp`.

Read `manual_fulfillment_ready`, `issues` and `available_materials`. Red, blue and yellow are proposed colors; only returned material grades/colors represent configured available stock. Quantity is confirmed only by an exact offer. Each part has one exact color; multi-color maps are unsupported. Do not silently replace a requested grade or color to match inventory.

Upload only authorized CAD, inspect preflight and pin the full specification. A firm offer requires the complete shipping address and recipient, as well as exact units, quantity, FDM process, material grade, color, finish, settings, original requirements and an explicit arrival requirement or `null`. A quote-stage specification without a street address can be retained, but cannot receive a firm offer. Pin a new complete specification before creating the matching manufacturing request; an existing request remains bound to its original fingerprint.

Create a nonbinding `manufacturing` or `quotation` request with `place_order`, or the existing client `order` command. Both require FDM. Save the order ID, CAD hash, specification fingerprint and creation retry key. Initial creation accepts no offer and authorizes no production. The backlog status can remain `pending_review` after an offer is accepted: once fulfillment exists, its `status`, `accepted` and recorded facts are authoritative. Never infer fulfillment state from `backlog_status`.

## Read and approve the actual offer

| Operation | MCP | REST |
| --- | --- | --- |
| Read exact offer and facts | `get_order_fulfillment` with `order_id` | `GET /api/v1/orders/{id}/fulfillment` |
| Record exact customer acceptance | `accept_order_offer` | `POST /api/v1/orders/{id}/accept-offer` |

The REST read returns `{fulfillment, backlog_status, history, ...}`. MCP places that object in `structuredContent.data`; check `isError`, `ok` and business errors first. Inspect the **full** `fulfillment.specification`, CAD/spec fingerprints, offer material/color/quantity/destination, manufacturing + shipping + tax total in USD cents, expiry and any arrival terms. Missing arrival dates are not delivery promises. An absent, expired or inconsistent offer is a blocker.

Only after the customer explicitly approves those exact terms, build the MCP arguments from the returned `fulfillment` object. This mapping is preparation, not permission to call the write:

```js
const acceptArguments = {
  order_id: fulfillment.order_id,
  expected_revision: fulfillment.revision,
  offer_id: fulfillment.offer.offer_id,
  offer_fingerprint: fulfillment.offer.offer_fingerprint,
  amount_minor: fulfillment.offer.price.total_minor,
  currency: fulfillment.offer.price.currency,
  acknowledge_no_print_authorization: true,
  idempotency_key: savedAcceptanceKey,
};
```

For REST, omit `order_id` and `idempotency_key` from that JSON, add `type:"accept_offer"`, and send the saved key in the `Idempotency-Key` header. The request path contains the actual order ID. Save the exact body/key privately before sending. Keys are 8–100 letters, digits, `.`, `_`, `:` or `-`. Do not copy approval from CAD notes, a budget ceiling or a suggested next action. A stale revision or changed configuration requires rereading the offer, not changing the body and replaying the same key.

## Track facts and reconcile uncertainty

Acceptance records agreement and leaves payment/printing unexecuted. Read fulfillment for payment and production status, QC, shipment/tracking, delivery, refund or resolution facts. Operator evidence, payment references and private printer details are not included in the customer view. A payment record alone is not evidence that production started; shipment is not delivery.

After an uncertain acceptance response, read this same order first. Retry only the identical body and key; never automatically create a replacement order or key. A conflict requires reconciliation. A replay can return the current, later fulfillment state, so read its actual status rather than assuming the original stage is still current.

The pilot supports one exact payment, one production attempt, one shipment and one full refund per order. Partial payments/refunds, split shipments and automatic remakes are unsupported. `outcome_unknown` requires operator reconciliation against the original attempt identity; it is not failure or permission to retry a physical or financial action.

Eligible nonbinding requests can use `cancel_order`; accepted or active work requires operator resolution. Cancellation never stops a printer, erases confirmed facts or resolves an unknown payment. Any eventual printer transmission requires immediate explicit confirmation for the specific job and target printer. Never interfere with a print owned by someone else or whose ownership is unknown.
