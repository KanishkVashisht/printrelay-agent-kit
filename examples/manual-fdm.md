# One exact FDM offer, then tracked fulfillment

This is the PrintRelay 0.7 customer workflow for owner-operated FDM. It does not submit to a supplier, move money or send printer commands. Free advice and specialist DFM review remain separate from a manufacturing offer. Read [current capabilities](https://partsforagents.com/api/capabilities) before beginning; the default stock, printer and payment configuration is not ready.

Use external MCP at `https://partsforagents.com/api/mcp` with an account key, or native `https://printrelay.kva1.chatgpt.site/mcp` through Sites OAuth. The bundled Python CLI supports intake, specification JSON and nonbinding requests. It has no dedicated color-plan workflow or production-capabilities, fulfillment or offer-acceptance commands. **Use MCP/REST for the new multicolor mapping and offer/tracking workflow**; do not invent CLI flags. Scripts are unchanged. [Tool schemas](https://partsforagents.com/tools.json) and [OpenAPI](https://partsforagents.com/openapi.json) are authoritative.

## Check stock and preserve the exact part

Call `get_production_capabilities` with `{}`, or read public `GET https://partsforagents.com/api/production-capabilities`. It is also one of the three tools on unauthenticated `/api/advice/mcp`.

Read `manual_fulfillment_ready`, `issues` and `available_materials`. The owner has specified X2D and PLA/PETG, but this does not verify printer capability, stock or payment readiness. Only returned material grades/colors represent configured available stock; quantity is confirmed by an exact offer. Single-color parts use one exact red, blue or yellow. Multicolor permits two or three of those colors in the same family and exact grade, using object-mapped 3MF only. Do not substitute a grade/color to match inventory or interpret multicolor schema support as configured printer readiness.

Upload only authorized CAD, inspect preflight and pin the full specification. A firm offer requires the complete shipping address and recipient, as well as exact units, quantity, FDM process, material grade, color, finish, settings, original requirements and an explicit arrival requirement or `null`. A quote-stage specification without a street address can be retained, but cannot receive a firm offer. Pin a new complete specification before creating the matching manufacturing request; an existing request remains bound to its original fingerprint.

Create a nonbinding `manufacturing` or `quotation` request with `place_order`, or the existing client `order` command. Both require FDM. Save the order ID, CAD hash, specification fingerprint and creation retry key. Initial creation accepts no offer and authorizes no production. The backlog status can remain `pending_review` after an offer is accepted: once fulfillment exists, its `status`, `accepted` and recorded facts are authoritative. Never infer fulfillment state from `backlog_status`.

## Preserve a multicolor object map

For multicolor, use `set_manufacturing_specification` or `PUT /api/v1/requests/{id}/specification`. Supply the complete normal manufacturing inputs plus `color:"multicolor"` and `color_plan`. The following is the **color_plan object only**, not a complete request; its hash and selectors are placeholders for actual evidence:

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

Select objects from the actual uploaded 3MF, never from a guessed filename or render. Each assignment uses a distinct color and disjoint model-path/object-ID selectors; all bind the same CAD SHA. The server canonicalizes the plan and produces specification version 2 plus a color-plan fingerprint. Save both fingerprints. A changed object assignment or color requires a new specification and matching intent; do not reinterpret old orders. Without a color plan, existing single-color specifications retain version 1.

Before an offer, the operator inspects actual object existence, full color coverage and mapping against that exact file, and records review evidence. Each color needs its own stock allocation in the same grade and enough verified printer color capacity. A structurally valid map is not automatic geometry inspection, slicer validation or printability certification. This workflow does not support painted facets, layer-height color changes or mixed material grades. The kit's separate STL enclosure components remain single-color examples; they do not establish a multicolor 3MF mapping.

Multicolor is owner-manual only: `request_provider_comparison` rejects version 2 specifications with HTTP422 `multicolor_manual_only`, because legacy supplier readback cannot attest the object/color plan. Historical version 1 supplier records remain unchanged.

## Choose shipping without inventing an arrival date

Origin is ZIP 60611; initial coverage is the contiguous US and DC. Supply recipient, street, city, two-letter state and ZIP. Alaska, Hawaii, territories and military destinations are outside this policy.

| Service in the offer | Customer shipping price | Meaning |
| --- | --- | --- |
| `ground` | USD 0 | Ground transit after dispatch; production time is separate. |
| `next_day` | USD 7.50 / 750 minor units | Next-day transit after dispatch, only after actual route verification; production time is separate. |

The operator verifies address/service suitability. Next-day needs actual route evidence before an offer. Neither service establishes a manufacturing lead time or guaranteed arrival date. A hard arrival requirement must have a specific supported commitment in the exact offer. Free ground is a customer price, not a claim that carrier/packaging costs are zero.

## Read and approve the actual offer

| Operation | MCP | REST |
| --- | --- | --- |
| Read exact offer and facts | `get_order_fulfillment` with `order_id` | `GET /api/v1/orders/{id}/fulfillment` |
| Record exact customer acceptance | `accept_order_offer` | `POST /api/v1/orders/{id}/accept-offer` |

The REST read returns `{fulfillment, backlog_status, history, ...}`. MCP places that object in `structuredContent.data`; check `isError`, `ok` and business errors first. Inspect the **full** `fulfillment.specification`, CAD/spec/color-plan fingerprints, exact material allocations, reviewed color map, quantity/destination, selected shipping terms, manufacturing + shipping + tax total in USD cents, expiry and any arrival terms. New offers use version 2; historical version 1 records remain readable/replayable and are never silently upgraded. Missing arrival dates are not delivery promises. An absent, expired or inconsistent offer is a blocker.

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

Acceptance records agreement and leaves payment/printing unexecuted. Once the operator has verified Stripe account readiness, a separately prepared hosted invoice may collect the exact accepted full USD amount. No ready Stripe account or automatic payment integration is implied. The operator reconciles the underlying successful payment, not an invoice status alone; invoice and processing fees belong in operator economics, not an invented customer price. Read fulfillment for payment and production status, QC, shipment/tracking, delivery, refund or resolution facts. Operator evidence, payment references and private printer details are not included in the customer view. A payment record alone is not evidence that production started; shipment is not delivery.

After an uncertain acceptance response, read this same order first. Retry only the identical body and key; never automatically create a replacement order or key. A conflict requires reconciliation. A replay can return the current, later fulfillment state, so read its actual status rather than assuming the original stage is still current.

The pilot supports one exact payment, one production attempt, one shipment and one full refund per order. Partial payments/refunds, split shipments and automatic remakes are unsupported. `outcome_unknown` requires operator reconciliation against the original attempt identity; it is not failure or permission to retry a physical or financial action.

Eligible nonbinding requests can use `cancel_order`; accepted or active work requires operator resolution. Cancellation never stops a printer, erases confirmed facts or resolves an unknown payment. Any eventual printer transmission requires immediate explicit confirmation for the specific job and target printer. Never interfere with a print owned by someone else or whose ownership is unknown.
