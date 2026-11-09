# First run: inspect, connect, then hand off

Start without an account: inspect the committed CAD locally and read public service readiness. Authenticated intake is a separate, optional step. Current fulfillment is owner-operated FDM; successful setup is not a firm offer, payment or manufactured part.

## Get the files

Installing the Agent Skill gives your agent its instructions and Python client. The tutorials and CAD examples live in the full repository, which you obtain separately:

```sh
git clone https://github.com/KanishkVashisht/printrelay-agent-kit.git
cd printrelay-agent-kit
python3 --version
python3 skills/printrelay-hardware/scripts/printrelay.py --help
```

No Python dependency installation is needed. The first-run path was checked with Python 3.14.8 on macOS; other host combinations are not implied to be tested. Run the remaining commands from this repository root. If you already have a checkout, use it; do not overwrite local CAD revisions to follow this example.

## Check the local example and public service

```sh
# Local geometry only; no account, network or Blender needed.
python3 examples/enclosure/verify.py --check

# Two public reads; no key, account, upload or private request.
python3 skills/printrelay-hardware/scripts/printrelay.py capabilities
python3 skills/printrelay-hardware/scripts/printrelay.py example
```

The local verifier should exit successfully with the committed base dimensions `[60,40,22]` mm and lid dimensions `[60,40,6]` mm. The public example is a separate 20 mm cube: its report should show `[20,20,20]` mm, 12 triangles, 8,000 mm³ mesh volume and `certifies_printability: false`. The report's `file_sha256` must match the SHA-256 of `examples/calibration-cube-20mm.stl`. [The enclosure walkthrough](enclosure/README.md) explains what these checks do and do not measure.

Read the returned capability **statuses**, not just the HTTP success:

| Capability | Meaning for the next step |
| --- | --- |
| `cad_intake` / `owned_cad_preflight` | Account access is still required even when the public contract says `available`. |
| `manual_fdm_fulfillment` | `requires_setup` or `not_verified` means no ready operator offer. Even `ready_for_operator_offer` requires an exact offer for this job. |
| `/api/production-capabilities` | Read `available_materials` for configured grades/colors; proposed red/blue/yellow is not stock. Quantity is confirmed only by an offer. |
| `supplier_quote_collection` / `supplier_worker_readiness` | Federated supplier execution is `deferred`; `not_verified` establishes no supplier pricing. |
| `payment` / `purchase` / `print_transmission` | The beta reports these as `disabled`. Do not tell the owner a part was bought or printed. |

If a command fails, stop at that stage. Do not upload CAD to troubleshoot a public-read failure. Public MCP at `https://partsforagents.com/api/advice/mcp` exposes 3 read-only tools plus `submit_agent_feedback`, a public write. The client `production-capabilities` command and `GET https://partsforagents.com/api/production-capabilities` need no key.

## Connect an account only when needed

If you already have the native partsforagents OAuth connection, use its read-only status and owned-list tools. To use an external agent or this Python client, follow the [skill's key-bootstrap procedure](../skills/printrelay-hardware/SKILL.md#connect-a-named-external-agent-without-exposing-its-secret): generate/save the secret in that runtime and register only its digest through the native connection. The owner must authorize that agent's full-account access, including offer acceptance only with explicit approval of each exact offer. Alternatively, create a key through the signed-in [service console](https://partsforagents.com/docs#keys).

Once the key is registered, configure **one** source for this client:

- `PRINTRELAY_API_KEY_FILE`: absolute path to the private mode0600 key file; keep `scripts/bootstrap_key.py` beside `scripts/printrelay.py`. The helper uses POSIX ownership and permissions, as on macOS/Linux.
- `PRINTRELAY_API_KEY`: injected by your runtime's secret mechanism. Do not put the secret into a prompt, command argument, issue or repository file.

Then run:

```sh
python3 skills/printrelay-hardware/scripts/printrelay.py list
```

This reads your owned requests; an empty successful result is fine. Keep the response private. A 401 or missing-key error means setup is incomplete. Do not generate multiple keys to resolve an uncertain registration: use the helper's documented `--resume` procedure.

External MCP uses `https://partsforagents.com/api/mcp` with the same account key in an Authorization Bearer header through the host's secret mechanism (21 workflow tools). Native `https://printrelay.kva1.chatgpt.site/mcp` uses the separate Sites OAuth connection (24 tools, including native-only key management). The Python client calls `partsforagents.com`. It supports `production-capabilities` and `fulfillment ORDER_ID` reads; use MCP/REST for exact offer acceptance and multicolor mapping. If neither connection nor signed-in console is available, retain the successful local/public check and stop here; no account creation or authenticated success is implied.

## Choose one bounded handoff

- **Smallest service exercise:** [upload the owned cube and read its preflight](README.md). This intentionally creates one private intake record, requires authorized contact/destination details, and stops before supplier comparison.
- **Useful CAD-agent exercise:** [inspect the enclosure, upload its two components and pin two exact specifications](enclosure/README.md#optional-agent-handoff-upload--preflight--exact-spec). Review the example choices before using them. Regenerating CAD is optional; committed exports are already included.

Give your agent this task after reviewing the files:

> Read the partsforagents skill and current capabilities. Use the enclosure example as a noncritical fit-check prototype. Inspect its existing geometry locally first. Tell me which account, destination or manufacturing details are still missing. After I authorize intake and supply those details, preserve the exact files and units, read preflight and pin the two specifications. Stop before sharing files with suppliers or ordering. Report blockers as blockers.

Keep request IDs, CAD hashes, specification fingerprints and retry keys privately. Changed CAD or immutable intake fields need a new request. Changed manufacturing choices can receive a new specification fingerprint on the existing request, as supported by the live schema. A timeout retry reuses the same saved key and payload. For an owner-fulfilled FDM request after the exercise, read the [offer and tracking workflow](manual-fdm.md). A complete shipping specification must be pinned before a firm offer; a changed spec needs a new matching nonbinding request. Review actual stocked grade and one exact color per part. Do not submit to deferred supplier workflows merely to test setup.

## Submit a real job when ready

The examples above are optional local exercises, not required customer activity. For an actual authorized job, upload its CAD, inspect preflight and pin its exact FDM specification. Call `place_order` with the returned `request_id`, `spec_fingerprint`, `order_type:"manufacturing"`, `acknowledge_nonbinding:true` and a saved idempotency key. The REST equivalent is `POST /api/v1/orders`; the Python helper accepts the same body from a private JSON file:

```sh
python3 skills/printrelay-hardware/scripts/printrelay.py order \
  --json-file /private/path/job.json --idempotency-key SAVED_UNIQUE_KEY
```

Submit now; the payment link comes later after review and exact-offer acceptance. The request records `pending_review`, requires no payment and books no capacity. `payment_required_on_submission:false`, `payment_link:null` and `payment_link_status:"after_review_if_accepted"` describe the current manufacturing flow. Stripe setup is pending and no automatic link delivery is implemented; there is no promised review/payment-link turnaround. Free specialist requests use `dfm_review` and need no payment.

Read `order-status ORDER_ID` for review status and `fulfillment ORDER_ID` for any exact offer and fulfillment facts. A missing fulfillment record before an offer is normal. Once an offer exists, `get_order_fulfillment` is authoritative: the backlog can still say `pending_review` after acceptance, so inspect fulfillment status, acceptance and recorded facts. Never infer successful payment or printing from a backlog request. Follow [manual FDM](manual-fdm.md) to inspect the exact price, obtain customer approval, accept and track the job. The native tool name remains `place_order` for compatibility, but submitting it is a nonbinding request.

## Report useful setup feedback

For a reproducible public client problem, report your OS, Python/client version, exact command with private values replaced, exit code, error code and the last successful stage. Distinguish local geometry, public reads, authentication, intake, an issued offer, acceptance and recorded fulfillment facts. Do not post keys, raw account-list output, customer CAD, shipping addresses or private request/quote IDs. An internal fixture test is technical validation, not a customer or manufacturing result.


Send a concise non-sensitive report with public MCP `submit_agent_feedback` or `POST /api/feedback`. For the client, save this object privately, then use the saved retry key:

```json
{"category":"docs","message":"The setup instructions should explain the last successful step more clearly.","consent":true,"agent_name":"CAD assistant","context_path":"/docs"}
```

```sh
python3 skills/printrelay-hardware/scripts/printrelay.py feedback \
  --json-file /private/path/feedback.json --idempotency-key SAVED_FEEDBACK_KEY
```

No account key is sent. Omit empty optional fields. The response is a private receipt, not a public post or support promise. There is no public lookup; replay exactly the same body/key after uncertainty. Do not submit example feedback merely to test the live endpoint: local tests cover the helper without creating production records.
