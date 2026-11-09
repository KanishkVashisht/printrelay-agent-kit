# PrintRelay agent kit

**Free manufacturing advice, exact FDM offers and tracked handoffs for agents.** Give a coding or CAD agent a repeatable path from an exported model to a reviewed specification and, when configured, an owner-fulfilled FDM offer.

This repository contains an Agent Skill, a Python standard-library client, an editable two-part enclosure workflow and an owned 20 mm test model. PrintRelay 0.7.1 provides free sourced advice, bounded preliminary DFM, an explicitly uncalibrated budget preview and free asynchronous specialist review. Manufacturing is an owner-operated FDM pilot: exact offers, customer acceptance and recorded payment/production/shipping facts are supported. The owner has specified X2D and reports red, blue and yellow PLA/PETG; exact grades, usable quantities, machine capability and payment readiness still require verification. Other Bambu PLA/PETG products and named colors can be sourced after compatibility and availability review. Multicolor supports 2–25 distinct named colors in one exact material grade, using an operator-reviewed object map in the uploaded 3MF and capped by the actual configured printer. Bambu's 25-color hardware maximum requires the maximum AMS setup; it is not a claim about installed accessories or available stock. No endpoint moves money or transmits a print, and federated suppliers are deferred. Geometry checks do not certify printability.

[Agent home](https://partsforagents.com/) · [For humans](https://partsforagents.com/for-humans) · [API guide](https://partsforagents.com/docs) · [OpenAPI](https://partsforagents.com/openapi.json) · [Current capabilities](https://partsforagents.com/api/capabilities)

**Start here:** [first-run walkthrough](examples/quickstart.md). Inspect public readiness, then choose a bounded intake or review task. For an actual operator offer, use the [manual FDM offer and tracking workflow](examples/manual-fdm.md).

**Free manufacturing guide:** [Will the lid fit?](knowledge/first-prototype-handoff.md) works through clearance versus tolerance, material/orientation questions and the information a CAD agent should preserve before requesting manufacture. Use it with any CAD tool or service; no account is needed.

## Install the skill

```sh
npx skills add KanishkVashisht/printrelay-agent-kit
```

Review the skill and choose the agent/client you want to configure. This is the owner/repository install syntax documented by the [skills CLI](https://www.skills.sh/docs/cli). Client support and permission prompts vary. Installing the skill does not create a PrintRelay account or authorize uploading a design.

You can also copy the entire [`skills/printrelay-hardware`](skills/printrelay-hardware) directory into your agent's supported skill directory. Keep `SKILL.md`, `scripts/printrelay.py` and `scripts/bootstrap_key.py`; the client needs the helper for key-file authentication. A direct service-hosted copy is available at [SKILL.md](https://partsforagents.com/skills/printrelay-hardware/SKILL.md).

Skill installation does **not** install the repository's example models or tutorials. To run the examples, obtain a checkout separately:

```sh
git clone https://github.com/KanishkVashisht/printrelay-agent-kit.git
cd printrelay-agent-kit
```

The client and committed geometry checks use Python 3's standard library; no Python packages are needed. The first-run path was checked with Python 3.14.8 on macOS. Blender is needed only to regenerate or render the parametric enclosure.

## Start with a bounded task

> I have an STL for an electronics enclosure. Inspect its reported dimensions, preserve the explicit units and manufacturing requirements, and prepare a tracked quote request. Tell me what is missing and whether quotes are actually available. Do not order anything.

Use the agent's existing CAD tools to design or revise the part. This kit supplies the manufacturing handoff. Begin with a noncritical prototype, such as an enclosure fit check or desktop sensor mount.

## Inspect before creating an account

From a repository checkout, these read-only client commands need no API key and create no request:

```sh
python3 skills/printrelay-hardware/scripts/printrelay.py capabilities
python3 skills/printrelay-hardware/scripts/printrelay.py example
python3 skills/printrelay-hardware/scripts/printrelay.py advice --topic fits
```

They read the current contract, a published measurement of the owned fixture and sourced manufacturing guidance. They do not quote your model or demonstrate supplier fulfillment. If the public route is unavailable, stop and check the deployment status in the API guide before uploading anything.

## Connect your account

Use the native PrintRelay OAuth connection to register a key generated and saved inside the named agent’s runtime, or create a key in the signed-in [human console](https://partsforagents.com/for-humans#workspace). Native registration receives only its SHA-256 digest. The [skill](skills/printrelay-hardware/SKILL.md#connect-a-named-external-agent-without-exposing-its-secret) includes the local bootstrap and retry procedure. Store the credential through your secret mechanism, or set `PRINTRELAY_API_KEY_FILE` to its private mode0600 file. Do not paste a key into an issue, commit, prompt or example file.

| Route | Authentication | Purpose |
| --- | --- | --- |
| `https://partsforagents.com/api/advice/mcp` | None | 3 public tools: service status, sourced advice and production capabilities. |
| Python client / REST | Account-scoped API key | Intake, exact-spec analysis and nonbinding requests. Use MCP/REST for multicolor mapping, production capabilities, offer acceptance and fulfillment; the unchanged CLI has no dedicated commands for these workflows. |
| `https://partsforagents.com/api/mcp` | `Authorization: Bearer` followed by the same API key | 20 workflow tools for external MCP clients supporting Streamable HTTP and custom headers. |
| `https://printrelay.kva1.chatgpt.site/mcp` | Sites OAuth through the native integration | 23 tools: the workflow tools plus native-only key registration/list/revoke. The REST API key is not an OAuth credential. |

Check [capabilities](https://partsforagents.com/api/capabilities), [workflow tool schemas](https://partsforagents.com/tools.json) and [docs](https://partsforagents.com/docs) before configuring a client. Production compatibility varies by host; a reachable endpoint is not proof of a completed authenticated workflow. The bundled Python client currently uses the original `printrelay.kva1.chatgpt.site` host and a named User-Agent; its existing commands are unchanged. New MCP/REST examples use `partsforagents.com`.

## Request a review without ordering a print

After authorized intake and a pinned specification, the [skill workflow](skills/printrelay-hardware/SKILL.md#analyze-an-exact-part-and-request-review) uses `analyze` and `estimate` with the exact specification fingerprint. `order` records a nonbinding `pending_review` request with an explicit acknowledgement and saved idempotency key. `dfm_review` is free asynchronous specialist advice; new `quotation` and `manufacturing` requests require FDM and can later receive an operator-issued offer. Read `order-status` for an actual report. A budget preview is not a firm price, and submitting a request authorizes no payment or printing. `cancel-order` handles eligible nonbinding requests; accepted or active work requires fulfillment resolution and never stops a printer.

## Read, approve and track one exact FDM offer

Use `get_production_capabilities` first. `available_materials` identifies actual configured grades/colors; an empty list or `manual_fulfillment_ready:false` is a setup blocker. Stock does not guarantee that a particular job fits or that its full quantity is available. For multicolor, preserve actual 3MF object selectors, CAD SHA and color-plan/specification fingerprints; the operator must inspect the map before issuing an offer. Read `get_order_fulfillment` for the full canonical specification/color plan, exact allocations, destination, shipping terms, complete USD price and current revision. Only after the customer explicitly approves those exact terms, call `accept_order_offer` with the returned identity, fingerprint, amount and a saved retry key.

The production offer targets dispatch within two business days after confirmed payment, counted Monday–Friday in America/Chicago, with carrier-holiday exceptions disclosed in the exact offer. Shipping starts at ZIP 60611 with contiguous-US/DC coverage: ground is free; next-day is $7.50 for transit after dispatch, subject to actual route verification. This is not a two-day arrival promise. Exact production and shipping terms belong in the offer.

Multicolor handling is $3 per additional distinct color per order: two colors add $3; three add $6. The separate manufacturing price includes the reviewed slice's material, purge/support consumption and machine time. Read `price.handling_minor` and the complete accepted total; a handling fee is not a substitute for actual production costing.

Acceptance records agreement; it does not charge or authorize printing. Continue reading fulfillment for actual payment, production, QC, shipment, delivery or resolution facts. A separately prepared Stripe-hosted invoice can follow exact acceptance once payment-account readiness is verified; account eligibility is not assumed. The pilot supports one exact payment, one production attempt, one shipment and one full refund, without partials, split shipments or automatic remakes. [The workflow](examples/manual-fdm.md) gives the exact MCP/REST mapping and retry rules.

## Build a real CAD handoff

Start with the [parametric enclosure walkthrough](examples/enclosure/README.md): a 60 × 40 mm tray and lift-off lid, explicit clearances, a cable notch, editable Blender source, separate STL exports and measured geometry evidence. The example takes an agent from local CAD through preflight to two pinned specifications, stopping before any supplier upload or order. Its standalone verifier needs only Python's standard library; regenerating the model uses Blender.

![Original enclosure model, rendered in Blender as an exploded assembly.](examples/enclosure/enclosure-preview.png)

## Try the smaller owned fixture

From a checkout of this repository:

```sh
python3 skills/printrelay-hardware/scripts/printrelay.py --help
```

Follow the [calibration workflow](examples/README.md). It explains the expected 20 × 20 × 20 mm dimensions, upload consent and a preflight-only stopping point. Keep request IDs and responses private. No supplier upload, purchase or print is required to try the fixture workflow.

For your own model, establish explicit mm/inch units, quantity, destination, process, exact material/allowed substitution policy, finish, color and manufacturing settings. Preserve functional notes. Accept supplier defaults only when that is the owner's explicit choice.

Federated supplier execution is deferred. If separately reactivated, supplier comparisons must preserve the same specification and currency, complete shipping/tax, expiry, review status and delivery evidence. Named-provider file sharing requires the design owner's permission and persistent ordinary buyer accounts. A production lead time is never an arrival promise.

## Contents and scope

- `skills/printrelay-hardware/`: installable instructions and client; no third-party Python dependencies.
- `examples/enclosure/`: original parametric enclosure, exported components, reproducible checks and a CAD-agent handoff walkthrough.
- `examples/`: calibration geometry, expected measurements and the manual FDM offer/tracking guide, with no customer data.
- `registry/server.json`: prepared v0.5.0 update; the active listing remains the [verified MCP Registry v0.3.0 listing](https://registry.modelcontextprotocol.io/v0.1/servers/io.github.KanishkVashisht%2Fprintrelay/versions/0.3.0). See `registry/README.md` for scope and verification.

The MIT license covers this repository's original code, documentation and generated fixture. It does not license the hosted service, third-party software, supplier content or user-uploaded designs. Report reproducible client issues without keys, addresses or private CAD. Follow the service's [privacy information](https://partsforagents.com/privacy) for uploaded data.
