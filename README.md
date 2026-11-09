# Parts for Agents — agent kit

**Everything you need to make your vibe CAD a reality.** Give your CAD or coding agent a manufacturing handoff: expert-agent DFM advice, 3D printing delivered to your user's home, MCP tools to submit and track jobs, and a reviewed offer followed by payment instructions.

**Submit your FDM job request now; the payment link comes later, after review and your acceptance of the exact offer.** Submission is nonbinding and requires no payment. It does not reserve printer capacity or start a print. Payment-account setup is pending: there is no instant checkout or automatic payment-link delivery today. The order response explicitly reports `payment_required_on_submission:false` and `payment_link:null`.

[Agent home](https://partsforagents.com/) · [For humans](https://partsforagents.com/for-humans) · [API guide](https://partsforagents.com/docs) · [OpenAPI](https://partsforagents.com/openapi.json) · [Current capabilities](https://partsforagents.com/api/capabilities)

## What your agent can do

- **Get useful advice for free.** Read sourced material, fit and process guidance without an account. Analyze measured geometry against the exact uploaded specification, or request a free asynchronous specialist-agent DFM review. Preliminary checks do not certify printability or measure unseen walls, strength or support needs; a queued review is not a finished report.
- **Submit an FDM job.** Upload authorized CAD, preserve its hash, units, material, quantity, colors and destination, then create a tracked `manufacturing` request. The current offer is owner-operated PLA/PETG FDM; exact stock and machine configuration govern each offer. Supplier federation is deferred.
- **Track the exact offer and fulfillment.** Inspect the complete price and specification, obtain customer approval, then track recorded payment, production, shipment and delivery facts through MCP or REST.
- **Pay after review.** An operator-provided payment link is planned after the exact offer is accepted and payment-account setup is complete. No API endpoint currently moves money or transmits a print. There is no promised review or payment-link turnaround.

Start with the [first-run walkthrough](examples/quickstart.md), then follow the [FDM offer and tracking workflow](examples/manual-fdm.md). Free planning estimates disclose uncalibrated assumptions and missing costs; they are not firm prices or delivery promises.

## Install the skill

```sh
npx skills add KanishkVashisht/printrelay-agent-kit
```

Review the skill and select your agent/client. Installation does not create an account or authorize a CAD upload. You can also copy the complete [`skills/printrelay-hardware`](skills/printrelay-hardware) directory, including both Python scripts, into your agent's supported skill directory. A service-hosted copy is available at [SKILL.md](https://partsforagents.com/skills/printrelay-hardware/SKILL.md). The skill and protocol retain the `printrelay` identifiers for compatibility.

The skill installation does not include repository examples. Obtain those separately if needed:

```sh
git clone https://github.com/KanishkVashisht/printrelay-agent-kit.git
cd printrelay-agent-kit
python3 skills/printrelay-hardware/scripts/printrelay.py advice --topic fits
python3 skills/printrelay-hardware/scripts/printrelay.py production-capabilities
```

The client and geometry checks use Python 3's standard library. Blender is needed only to regenerate or render the parametric enclosure. Public advice and capability reads need no account, upload or key.

## Connect MCP or REST

| Route | Authentication | Tools |
| --- | --- | --- |
| `https://partsforagents.com/api/advice/mcp` | None | 4 public tools: service status, manufacturing advice, production capabilities and feedback submission. |
| `https://partsforagents.com/api/mcp` | Account-scoped API key in an Authorization Bearer header | 21 workflow tools for clients supporting Streamable HTTP and custom headers. |
| `https://printrelay.kva1.chatgpt.site/mcp` | Native Sites OAuth connection | 24 tools, including native-only key registration, list and revocation. |

Check the [tool schemas](https://partsforagents.com/tools.json) and [docs](https://partsforagents.com/docs) for the live contract. The native OAuth URL intentionally uses the original host; an API key is not an OAuth credential. Public feedback is a write, while the other three public MCP tools are reads.

For REST or the Python client, register a key generated and saved inside the named agent runtime using the [digest-only bootstrap](skills/printrelay-hardware/SKILL.md#connect-a-named-external-agent-without-exposing-its-secret), or create one in the signed-in [human console](https://partsforagents.com/for-humans#workspace). Use your secret store or `PRINTRELAY_API_KEY_FILE` pointing to its private mode0600 file. Never paste a key into chat, an issue or source code. Confirm account access with read-only `list` before uploading.

## Submit now, review price, pay later

After authorized intake and a pinned specification, call `place_order` with `order_type:"manufacturing"`, the exact `request_id` and `spec_fingerprint`, `acknowledge_nonbinding:true` and a saved idempotency key. REST uses `POST /api/v1/orders`; the Python equivalent is:

```sh
python3 skills/printrelay-hardware/scripts/printrelay.py order \
  --json-file /private/path/job.json --idempotency-key SAVED_UNIQUE_KEY
```

[The walkthrough](examples/manual-fdm.md) supplies the payload and exact acceptance mapping. Use `dfm_review` for free specialist advice or `quotation` for a reviewed FDM quotation request. Save the returned order ID privately. A pending request has no final price, confirmed capacity or production start. Read `order-status ORDER_ID` for review/payment-link state and `fulfillment ORDER_ID` for any issued offer and fulfillment facts. A missing fulfillment record before an offer is normal. Once an offer exists, `get_order_fulfillment` is authoritative: the backlog can still say `pending_review` after acceptance, so inspect fulfillment status, acceptance and recorded facts.

Before accepting an offer, verify the CAD/specification fingerprints, all manufacturing choices, complete destination, manufacturing + handling + shipping + tax total, expiry and delivery terms. Accept only the exact customer-approved offer. The operator will provide verified payment instructions later; the current API's `payment_link:null` is not a checkout URL, and there are no payment-link notifications or webhooks promised. Reconcile uncertain writes by reading the saved order and reusing the identical payload/key.

Ordinary in-stock offers target dispatch within two business days **after confirmed payment**, Monday–Friday in America/Chicago; actual terms and holiday exceptions belong in the offer. Ground shipping is free to the contiguous US/DC; verified next-day transit is $7.50 **after dispatch**. An arrival commitment is separate. Multicolor uses an operator-reviewed 3MF object map, one exact material grade, configured machine capacity and exact stock. Handling adds $3 per additional distinct color; manufacturing separately covers reviewed material, purge/support and machine costs. See the [full workflow](examples/manual-fdm.md) for limits and shipping details.

## Give the product feedback

Use public MCP `submit_agent_feedback` or REST `POST /api/feedback` without an account. Send a category, a concise non-sensitive message and `consent:true`; optionally identify your agent and the same-site pathname. Save the retry key and exact body:

```json
{"category":"docs","message":"The quickstart should explain how to read a pending job.","consent":true,"agent_name":"CAD assistant","context_path":"/docs"}
```

```sh
python3 skills/printrelay-hardware/scripts/printrelay.py feedback \
  --json-file /private/path/feedback.json --idempotency-key SAVED_FEEDBACK_KEY
```

The private receipt is not an order or a support guarantee. Do not include credentials, CAD, shipping addresses, payment information or private IDs. There is no public feedback lookup: after uncertainty, replay the identical body and key, never generate a new key automatically. [Skill details](skills/printrelay-hardware/SKILL.md#send-non-sensitive-product-feedback) cover fields and limits.

## Build a useful CAD handoff

[Will the lid fit?](knowledge/first-prototype-handoff.md) explains clearances, tolerance and what to preserve before manufacturing. The [parametric enclosure walkthrough](examples/enclosure/README.md) includes editable Blender source, separate STL exports and measured geometry evidence for a 60 × 40 mm tray and lid. The [20 mm calibration cube](examples/README.md) is a smaller owned test fixture. These examples and our tests are technical demonstrations, not customer adoption or completed prints.

![Original enclosure model rendered in Blender as an exploded assembly.](examples/enclosure/enclosure-preview.png)

Run local checks with `python3 -m unittest discover -s tests -v` and `python3 examples/enclosure/verify.py --check`. Public [registry metadata](registry/README.md) is tracked separately from source releases; a listing does not establish successful integration or fulfillment.
