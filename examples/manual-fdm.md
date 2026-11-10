# One exact FDM offer, then tracked fulfillment

This is the partsforagents 0.10 customer workflow for nonbinding FDM requests and exact offers. It does not submit to a supplier, move money or send printer commands. Free advice and specialist DFM review remain separate from a manufacturing offer. Read [current capabilities](https://partsforagents.com/api/capabilities) before beginning; configured stock, compatibility, exact job capacity and payment readiness determine whether an offer can be issued.

Use external MCP at `https://partsforagents.com/api/mcp` with an account key, or native `https://printrelay.kva1.chatgpt.site/mcp` through Sites OAuth. The bundled Python CLI supports intake, specification JSON and nonbinding requests. It also supports public `production-capabilities`, owned `fulfillment ORDER_ID` and public `feedback`. **Use MCP/REST for multicolor mapping and offer acceptance**; the client has no dedicated commands for those writes. [Tool schemas](https://partsforagents.com/tools.json) and [OpenAPI](https://partsforagents.com/openapi.json) are authoritative.

## Check stock and preserve the exact part

Call `get_production_capabilities` with `{}`, or read public `GET https://partsforagents.com/api/production-capabilities`. It is one of three read tools on unauthenticated `/api/advice/mcp`; the fourth tool submits product feedback.

Read `manual_fulfillment_ready`, `issues` and `available_materials`. Request any current Bambu Lab model filament and its offered colors by exact product. Accepted intake families are PLA, PETG, ABS, ASA, PC, TPU, PET, PA, PA6, PA12, PPA and PPS; PA12 is retained for general intake/advice, not a claim of a verified Bambu retail SKU. Specify the exact grade, product and color identifier; blends and reinforcement variants stay within their base family. This is nonbinding intake, not a claim of stocked or compatible capacity. Every offer requires exact compatibility, stock and sourcing review. Firm production offers currently support verified PLA/PETG only. Support-only filaments are not model-material choices. No universal finished-part dimensional tolerance is promised; specify critical dimensions and allowed deviations for a job-specific offer.

Single-color parts use one exact named color. The current PLA/PETG multicolor contract uses an exact 3MF object-to-color map in one material family and grade. The request schema accepts 2–25 colors, but this is not a promise of available color capacity. Each offer requires verified capacity, exact grade/color stock and a reviewed map. No silent material, grade or color substitutions.

Upload only authorized CAD, inspect preflight and pin the full specification. A firm offer requires the complete shipping address and recipient, as well as exact units, quantity, FDM process, material grade, color, finish, settings, original requirements and an explicit arrival requirement or `null`. A quote-stage specification without a street address can be retained, but cannot receive a firm offer. Pin a new complete specification before creating the matching manufacturing request; an existing request remains bound to its original fingerprint.

Create a nonbinding `manufacturing` or `quotation` request with `place_order`, or the existing client `order` command. Both require FDM. Save the order ID, CAD hash, specification fingerprint and creation retry key. Initial creation accepts no offer and authorizes no production. The backlog status can remain `pending_review` after an offer is accepted: once fulfillment exists, its `status`, `accepted` and recorded facts are authoritative. Never infer fulfillment state from `backlog_status`.

## Submit the job now; receive payment instructions later

After pinning the exact specification, the REST/client request body is:

```json
{
  "request_id":"RETURNED_REQUEST_ID",
  "spec_fingerprint":"EXACT_RETURNED_SPEC_HASH",
  "order_type":"manufacturing",
  "acknowledge_nonbinding":true,
  "review_notes":"Review this exact FDM job and provide the complete offer before payment."
}
```

Replace placeholders only with actual returned identities. Send it using `order --json-file PRIVATE_FILE --idempotency-key SAVED_KEY`, or `POST /api/v1/orders` with the saved `Idempotency-Key` header. MCP `place_order` uses the same fields plus `idempotency_key`. Use `quotation` for an FDM quote request or `dfm_review` for free specialist advice. Do not include an idempotency key inside REST JSON.

A new manufacturing request returns `pending_review` with `payment_required_on_submission:false`, `payment_link:null` and `payment_link_status:"after_review_if_accepted"`. It is accepted for review without charging or booking capacity. A free DFM request reports `not_required`; cancelled requests report `not_applicable`. The operator is expected to provide a verified payment link later, after exact-offer acceptance and payment-account setup. There is no actual link, automatic link notification or guaranteed review turnaround currently implemented. Never create a payment URL or claim a pending request was paid.

Read `order-status ORDER_ID` to inspect the saved request; `fulfillment ORDER_ID` reads any issued offer and recorded facts. A missing fulfillment record before an offer is normal. For an uncertain submission, read owned orders before retrying; preserve the original body and key. Continue with the exact-offer checks below before customer acceptance.

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

Select objects from the actual uploaded 3MF, never from a guessed filename or render. Each of the 2–25 assignments uses an exact distinct named color and disjoint model-path/object-ID selectors; all bind the same CAD SHA. Color tokens are `red`, `blue`, `yellow` or `bambu:<manufacturer-color-id>`; the identifier is 1–48 ASCII letters, digits, `.`, `_` or `-`, starts with a letter or digit, and is canonicalized to lowercase. Match the token to the exact Bambu product and stock record; do not invent a match from a display swatch or assume a color token identifies the material grade. The server canonicalizes the plan and produces specification version 2 plus a color-plan fingerprint. Save both fingerprints. A changed object assignment or color requires a new specification and matching intent; do not reinterpret old orders. Without a color plan, existing single-color specifications retain version 1.

Before an offer, the operator inspects actual object existence, full color coverage and mapping against that exact file, and records review evidence. Each color needs its own stock allocation in the same grade and enough verified printer color capacity. A structurally valid map is not automatic geometry inspection, slicer validation or printability certification. This workflow does not support painted facets, layer-height color changes or mixed material grades. The kit's separate STL enclosure components remain single-color examples; they do not establish a multicolor 3MF mapping.

Multicolor is owner-manual only: `request_provider_comparison` rejects version 2 specifications with HTTP422 `multicolor_manual_only`, because legacy supplier readback cannot attest the object/color plan. Historical version 1 supplier records remain unchanged.

## Read production and shipping terms separately

New version3 ordinary in-stock offers dispatch within two business days after the first verified full card authorization, with capture only after actual physical carrier handoff. The integration is implemented; runtime checkout remains disabled pending tax registration/account readiness. Historical version1/2 offers retain their paid-first terms. Business days are Monday–Friday in America/Chicago; carrier-holiday exceptions must be disclosed in the exact offer. Read the returned `production_terms` and dated commitments rather than starting the clock at request creation, offer acceptance, invoice creation or an unverified payment claim. Stock sourcing and compatibility review must be complete before this schedule is offered. The two-business-day window is for production and dispatch, not arrival at the customer.

New version3 offers bind these production terms version2 plus immutable authorization and tax evidence:

```json
{
  "version": 2,
  "order_class": "ordinary_in_stock",
  "dispatch_within_business_days": 2,
  "clock_starts": "first_verified_full_authorization_observation",
  "timezone": "America/Chicago",
  "calendar": "monday_friday",
  "holiday_policy": "carrier_closures_disclosed_in_offer"
}
```

For new version3 offers with production terms version2, `production_clock.first_authorized_at` records the first verified full card authorization; an uncaptured hold is not collected payment. `production_clock.absolute_dispatch_deadline` is the explicit reviewed `offer.dispatch_by`, with `deadline_status:"explicit_reviewed_offer"`. Read those returned values rather than deriving a different deadline or resetting the clock on a later authorization. Historical version1/2 offers with production terms version1 retain the confirmed-payment clock and `absolute_dispatch_deadline:null` (`deadline_status:"relative_terms_only"`); do not rewrite their terms as authorization-based offers.

Origin is ZIP 60611; initial coverage is the contiguous US and DC. Supply recipient, street, city, two-letter state and ZIP. Alaska, Hawaii, territories and military destinations are outside this policy.

| Service in the offer | Customer shipping price | Meaning |
| --- | --- | --- |
| `ground` | USD 0 | Ground transit after dispatch; production time is separate. |
| `next_day` | USD 7.50 / 750 minor units | Next-day transit after dispatch, only after actual route verification; production time is separate. |

The operator verifies address/service suitability. Next-day needs actual route evidence before an offer. Shipping service does not override production terms or establish a guaranteed arrival date. A hard arrival requirement must have a specific supported commitment in the exact offer. Free ground is a customer price, not a claim that carrier/packaging costs are zero.

## Read the multicolor handling charge

Handling is USD 3 per additional distinct color per order: `300 × (distinct_colors − 1)` in cents. Single-color handling is zero; two colors add $3, three add $6 and five add $12. Count each distinct color once across the order, not once per object or copy. This is a setup and mapping-verification charge, not a claim about purge cost.

New multicolor offers expose it separately as `price.handling_minor`; a single-color offer may omit it or use zero. Manufacturing includes the reviewed slice's material, purge/support consumption and machine time; shipping and tax remain separate. The complete total is manufacturing + handling + shipping + tax. Check each line and the total before acceptance; do not add an undisclosed handling charge after the customer approves the offer. Historical offers without this field retain their original amount and fingerprint.

## Read and approve the actual offer

| Operation | MCP | REST |
| --- | --- | --- |
| Read exact offer and facts | `get_order_fulfillment` with `order_id` | `GET /api/v1/orders/{id}/fulfillment` |
| Record exact customer acceptance | `accept_order_offer` | `POST /api/v1/orders/{id}/accept-offer` |

The REST read returns `{fulfillment, backlog_status, history, ...}`. MCP places that object in `structuredContent.data`; check `isError`, `ok` and business errors first. Inspect the **full** `fulfillment.specification`, CAD/spec/color-plan fingerprints, exact material allocations, reviewed color map, quantity/destination, production and shipping terms, manufacturing + handling + shipping + tax total in USD cents, expiry and any arrival terms. New offers use version3; historical records remain readable/replayable and are never silently upgraded. Missing arrival dates are not delivery promises. An absent, expired or inconsistent offer is a blocker.

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

Acceptance records agreement and leaves payment/printing unexecuted. Automatic collection is disabled. Version3 payment policy: after you approve the exact full-price offer, a secure link will authorize a card hold. We charge only when your part ships. A hold can reduce your available card balance and expires on the issuer/network deadline; an expired hold requires fresh authorization, never an early charge merely to preserve it. The flow is implemented but runtime activation is pending; current request submission is free and returns no payment URL. An authorization is not a captured payment. Historical manual records retain their original meaning and must not be used to infer current payment readiness. An ordinary automatically captured invoice is not a substitute for authorization-only checkout. Read fulfillment for payment and production status, QC, shipment/tracking, delivery, refund or resolution facts. Operator evidence, payment references and private printer details are not included in the customer view. A payment record alone is not evidence that production started; shipment is not delivery.

After an uncertain acceptance response, read this same order first. Retry only the identical body and key; never automatically create a replacement order or key. A conflict requires reconciliation. A replay can return the current, later fulfillment state, so read its actual status rather than assuming the original stage is still current.

The pilot supports one exact payment, one production attempt, one shipment and one full refund per order. Partial payments/refunds, split shipments and automatic remakes are unsupported. `outcome_unknown` requires operator reconciliation against the original attempt identity; it is not failure or permission to retry a physical or financial action.

Eligible nonbinding requests can use `cancel_order`; accepted or active work requires operator resolution. Cancellation never stops a printer, erases confirmed facts or resolves an unknown payment. Any eventual printer transmission requires immediate explicit confirmation for the specific job and target printer. Never interfere with a print owned by someone else or whose ownership is unknown.

## Materials, colors, fit and payment guides

Request any current Bambu Lab model filament and its offered colors by exact product. Accepted intake families are PLA, PETG, ABS, ASA, PC, TPU, PET, PA, PA6, PA12, PPA and PPS; PA12 is retained for general intake/advice, not a claim of a verified Bambu retail SKU. Specify the exact grade, product and color identifier; blends and reinforcement variants stay within their base family. This is nonbinding intake, not a claim of stocked or compatible capacity. Every offer requires exact compatibility, stock and sourcing review. Firm production offers currently support verified PLA/PETG only. Support-only filaments are not model-material choices. No universal finished-part dimensional tolerance is promised; specify critical dimensions and allowed deviations for a job-specific offer.

Version3 payment policy: after you approve the exact full-price offer, a secure link will authorize a card hold. We charge only when your part ships. A hold can reduce your available card balance and expires on the issuer/network deadline; an expired hold requires fresh authorization, never an early charge merely to preserve it. The flow is implemented but runtime activation is pending; current request submission is free and returns no payment URL.

- [Bambu material request guide](https://partsforagents.com/guides/bambu-filament-materials)
- [Color and multicolor handoff](https://partsforagents.com/guides/colors-and-multicolor)
- [Dimensional tolerances and fit](https://partsforagents.com/guides/dimensional-tolerances-and-fit)
- [Payments and shipping](https://partsforagents.com/guides/payments-and-shipping)


## Authorization link and shipment charge

For an accepted version3 offer, use owned REST `GET /api/v1/orders/{id}/payment-link` to read runtime readiness and any existing operation. Only if enabled, `POST` the same URL with `expected_revision` and `offer_fingerprint` from authoritative fulfillment, plus a saved `Idempotency-Key`. This returns `{payment:...}`; follow only the returned hosted Checkout URL. Preserve exact body/key before sending. A timeout requires GET reconciliation before replay, never a new key to bypass an uncertain operation. The MCP tool set is unchanged; REST handles this step. API access does not authorize entering a card or making a financial commitment on behalf of a user.

Checkout authorizes the full reviewed USD total; a hold can reduce the cardholder’s available balance but is not collected revenue. Production requires a fresh, sufficient authorization and exact CAD/specification/customer/tax readback. Actual issuer/network expiry is authoritative; a cancelled or expired authorization may require a new customer-approved link after the old attempt is reconciled. Never capture early to keep a hold alive. The dispatch clock remains tied to the first verified authorization.

Only the private operator can record actual physical carrier handoff after inspection, then request capture of the exact shipment charge. A shipping label is not physical handoff. Payment and shipment outcomes must be reconciled before retries. The invoice uses the same Checkout payment; there is no second invoice-collection charge. No payment endpoint transmits a print. If readiness is disabled, submit the nonbinding request and wait for the reviewed offer; do not substitute a direct immediate-charge invoice.
