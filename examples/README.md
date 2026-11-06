# Preflight a known 20 mm model

`calibration-cube-20mm.stl` was generated from eight vertices and twelve outward-facing triangles. It is a closed cube from `[0, 0, 0]` to `[20, 20, 20]` in explicitly declared millimeters. Its enclosed mesh volume is 8,000 mm³. This is parser/test geometry, not a certified calibration standard or a functional part.

The JSON companion records its provenance and expected measurements. `calibration-cube-20mm.preflight.json` is the deterministic parser report for these bytes. No customer model or address is included.

## Optional intake test

The help command makes no network request. Uploading the fixture creates a private request in your PrintRelay account. Proceed only when you intend that action and have configured `PRINTRELAY_API_KEY` securely. Supply your actual authorized email and destination in the environment variables below; do not invent them or commit their values.

From the repository root, after setting `PRINTRELAY_CONTACT_EMAIL`, `PRINTRELAY_COUNTRY` and `PRINTRELAY_POSTAL_CODE`:

```sh
python3 skills/printrelay-hardware/scripts/printrelay.py upload \
  examples/calibration-cube-20mm.stl \
  --email "$PRINTRELAY_CONTACT_EMAIL" \
  --material PLA --quantity 1 --units mm \
  --country "$PRINTRELAY_COUNTRY" \
  --postal-code "$PRINTRELAY_POSTAL_CODE" \
  --notes "Owned noncritical calibration fixture; preflight only." \
  --idempotency-key "calibration-cube-20mm-preflight-v1" \
  --consent
```

Keep the returned request ID locally. Reuse the same idempotency key when retrying the same uncertain upload; use a new key for changed files or requirements. The client checks that the service's CAD hash matches the uploaded bytes.

Use the client's `preflight` command with that request ID, or MCP's `get_cad_preflight` tool. If you save the actual ID privately in `PRINTRELAY_REQUEST_ID`:

```sh
python3 skills/printrelay-hardware/scripts/printrelay.py preflight "$PRINTRELAY_REQUEST_ID"
```
 The expected dimensions are `[20, 20, 20]` mm, triangle count 12 and enclosed mesh volume 8,000 mm³. Stop if the recorded units, dimensions or hash differ. The preflight report must retain its non-certification statement even when topology checks pass.

Stop after preflight for this exercise. Do not request supplier comparison merely to test the parser. File upload to PrintRelay does not grant permission to share it with suppliers or place an order.

## Handoff from an agent CAD workflow

For a real enclosure, generate and export the part with your usual CAD tools, inspect the source model locally, then substitute that file only when its owner permits upload. Preserve the exact model revision, units and requirements. Read the live specification schema rather than copying the calibration defaults into a production job.

The [CadQuery project's MCP server](https://github.com/CadQuery/cadquery-contrib/blob/master/mcp-server/README.md) supports CAD inspection and export. It is an independent project; this example does not imply endorsement or partnership. A full enclosure example is future work, not included in this fixture kit.
