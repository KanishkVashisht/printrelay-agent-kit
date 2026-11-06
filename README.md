# PrintRelay agent kit

**CAD preflight and exact-spec quote requests for agents.** Give a coding or CAD agent a repeatable handoff from an exported model to a tracked manufacturing request.

This repository contains an Agent Skill, a Python standard-library client and an owned 20 mm test model. PrintRelay's beta can retain CAD, inspect STL geometry, pin manufacturing requirements and queue supplier quote work. A pending job is not a price. The beta does not collect payment or place orders, and geometry checks do not certify printability.

[Service and sign-in](https://printrelay.kva1.chatgpt.site) · [API guide](https://printrelay.kva1.chatgpt.site/docs) · [OpenAPI](https://printrelay.kva1.chatgpt.site/openapi.json) · [Current capabilities](https://printrelay.kva1.chatgpt.site/api/capabilities)

## Install the skill

```sh
npx skills add KanishkVashisht/printrelay-agent-kit
```

Review the skill and choose the agent/client you want to configure. This is the owner/repository install syntax documented by the [skills CLI](https://www.skills.sh/docs/cli). Client support and permission prompts vary. Installing the skill does not create a PrintRelay account or authorize uploading a design.

You can also copy [`skills/printrelay-hardware`](skills/printrelay-hardware) into your agent's supported skill directory. Keep `SKILL.md` and `scripts/printrelay.py` together. A direct service-hosted copy is available at [SKILL.md](https://printrelay.kva1.chatgpt.site/skills/printrelay-hardware/SKILL.md).

## Start with a bounded task

> I have an STL for an electronics enclosure. Inspect its reported dimensions, preserve the explicit units and manufacturing requirements, and prepare a tracked quote request. Tell me what is missing and whether quotes are actually available. Do not order anything.

Use the agent's existing CAD tools to design or revise the part. This kit supplies the manufacturing handoff. Begin with a noncritical prototype, such as an enclosure fit check or desktop sensor mount.

## Inspect before creating an account

From a repository checkout, these read-only client commands need no API key and create no request:

```sh
python3 skills/printrelay-hardware/scripts/printrelay.py capabilities
python3 skills/printrelay-hardware/scripts/printrelay.py example
```

They read the service's current contract and a published measurement of the owned fixture. They do not quote your model or demonstrate supplier fulfillment. If the public route is unavailable, stop and check the deployment status in the API guide before uploading anything.

## Connect your account

Sign in at the service and create an account-scoped API key. Store it in the `PRINTRELAY_API_KEY` environment variable using your environment's secret mechanism. Do not paste a key into an issue, commit, prompt or example file.

| Route | Authentication | Purpose |
| --- | --- | --- |
| Python client / REST | Account-scoped API key | Upload authorized CAD, read requests and preflight, retain specifications and request quote work. |
| `https://printrelay.kva1.chatgpt.site/api/mcp` | `Authorization: Bearer` followed by the same API key | External MCP clients that support Streamable HTTP and custom authentication headers. |
| Native PrintRelay app / `/mcp` | Sites OAuth through the native integration | Separate native installation route; the REST API key is not its OAuth credential. |

Check [capabilities](https://printrelay.kva1.chatgpt.site/api/capabilities) and [docs](https://printrelay.kva1.chatgpt.site/docs) before configuring a client. Production compatibility varies by host; a reachable endpoint is not proof of a completed authenticated workflow. The client uses a named User-Agent because the service edge rejects Python urllib's default agent string.

## Try the owned fixture

From a checkout of this repository:

```sh
python3 skills/printrelay-hardware/scripts/printrelay.py --help
```

Follow the [calibration workflow](examples/README.md). It explains the expected 20 × 20 × 20 mm dimensions, upload consent and a preflight-only stopping point. Keep request IDs and responses private. No supplier upload, purchase or print is required to try the fixture workflow.

For your own model, establish explicit mm/inch units, quantity, destination, process, exact material/allowed substitution policy, finish, color and manufacturing settings. Preserve functional notes. Accept supplier defaults only when that is the owner's explicit choice.

When quotes become available, compare only offers for the same specification and currency with complete shipping/tax, expiry, review status and delivery evidence. A production lead time is not a delivery promise. Named-provider file sharing requires the design owner's permission; PrintRelay uses persistent ordinary buyer accounts rather than guest checkout.

## Contents and scope

- `skills/printrelay-hardware/`: installable instructions and client; no third-party Python dependencies.
- `examples/`: generated calibration geometry and expected measurements, with no customer data.
- `registry/server.draft.json`: an unpublished MCP Registry metadata draft. Its presence does not mean registry acceptance or listing.

The MIT license covers this repository's original code, documentation and generated fixture. It does not license the hosted service, third-party software, supplier content or user-uploaded designs. Report reproducible client issues without keys, addresses or private CAD. Follow the service's [privacy information](https://printrelay.kva1.chatgpt.site/privacy) for uploaded data.
