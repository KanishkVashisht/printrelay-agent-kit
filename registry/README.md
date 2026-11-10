# MCP Registry publication

Version **0.10.0** was published on 2026-11-10 UTC through the official GitHub-authenticated registry API. The [exact-version registry record](https://registry.modelcontextprotocol.io/v0.1/servers/io.github.KanishkVashisht%2Fprintrelay/versions/0.10.0) returned HTTP 200, matched every field in `server.json`, and was verified as active and latest. `server.draft.json` is the retained original preparation file, not a separate listing.

The published 0.10.0 record keeps the same `io.github.KanishkVashisht/printrelay` namespace, partsforagents title and custom-domain external API-key MCP endpoint. It describes free manufacturing/DFM advice plus nonbinding exact-CAD FDM job intake and tracking. Requests are nonbinding. A reviewed full-price offer comes first; customer acceptance is required before the later payment-authorization step. Payment execution is currently disabled. Native Sites OAuth uses a separate route. Listing metadata does not imply endorsement, installation, successful onboarding, a supplier quote or a customer order.

## Updating the record

The manual **MCP Registry** GitHub Actions workflow uses short-lived GitHub OIDC with `id-token: write` and `contents: read`; it does not require a stored personal GitHub token. Its default `verify` action validates the manifest, authenticates through OIDC and compares the public record without publishing. Its `publish` action requires a new version that is not already present and verifies the resulting record.

Before an update, confirm the deployed endpoint and authentication contract, edit the version and accurate capabilities in `server.json`, and commit the reviewed metadata before using an authorized official publishing route. Never add an actual API key to public metadata. An uncertain publish outcome must be reconciled by reading that exact version before retrying.

The `repository` property is omitted because this kit contains client/skill source, not the hosted MCP server source. Use the public website for setup and beta status.

Official references: [remote metadata](https://modelcontextprotocol.io/registry/remote-servers), [publisher authentication](https://modelcontextprotocol.io/registry/authentication), [GitHub OIDC publication](https://modelcontextprotocol.io/registry/github-actions), [schema](https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json).

## Publication history

Version **0.3.0** was initially published on 2026-11-06. Its [historical registry record](https://registry.modelcontextprotocol.io/v0.1/servers/io.github.KanishkVashisht%2Fprintrelay/versions/0.3.0) contains the earlier host and wording.

The reviewed 0.8.0 publication was attempted once on 2026-11-09 ([run 42698150606](https://github.com/KanishkVashisht/printrelay-agent-kit/actions/runs/42698150606)). GitHub reported: “The job was not started because your account is locked due to a billing issue.” No workflow steps ran. A subsequent exact-version read returned 404 for 0.8.0; at that time, 0.3.0 was the last verified published version. That failed workflow did not publish 0.8.0. The later 0.10.0 API publication and exact-version readback supersede that historical publication status.
