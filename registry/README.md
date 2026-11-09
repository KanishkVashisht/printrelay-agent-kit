# MCP Registry publication

PrintRelay version **0.3.0** was published on 2026-11-06 and verified as active in the [official registry record](https://registry.modelcontextprotocol.io/v0.1/servers/io.github.KanishkVashisht%2Fprintrelay/versions/0.3.0). `server.json` now prepares version **0.8.0** for a future registry update; that update has not been published. The active verified record remains **0.3.0**. `server.draft.json` is the retained original preparation file, not a separate listing.

The prepared 0.8.0 record uses the Parts for Agents title and custom-domain external API-key MCP endpoint. The active 0.3.0 record still uses the earlier host and wording; this file does not claim an update was published. The record points to the external API-key MCP endpoint. Native Sites OAuth uses a separate route. Listing metadata does not imply endorsement, installation, successful onboarding, a supplier quote or a customer order.

## Updating the record

The manual **MCP Registry** GitHub Actions workflow uses short-lived GitHub OIDC with `id-token: write` and `contents: read`; it does not require a stored personal GitHub token. Its default `verify` action validates the manifest, authenticates through OIDC and compares the public record without publishing. Its `publish` action requires a new version that is not already present and verifies the resulting record.

Before an update, confirm the deployed endpoint and authentication contract, edit the version and accurate capabilities in `server.json`, commit the reviewed metadata, then run the workflow's `publish` action. Never add an actual API key to public metadata. An uncertain publish outcome must be reconciled by reading that exact version before retrying.

The `repository` property is omitted because this kit contains client/skill source, not the hosted MCP server source. Use the public website for setup and beta status.

Official references: [remote metadata](https://modelcontextprotocol.io/registry/remote-servers), [publisher authentication](https://modelcontextprotocol.io/registry/authentication), [GitHub OIDC publication](https://modelcontextprotocol.io/registry/github-actions), [schema](https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json).

The last observed workflow attempt (2026-11-06, run 42278444964) did not start because GitHub reported an account billing lock. Its annotation was read again on 2026-11-09; no newer attempt has established whether that condition persists. Validate the deployed contract first, then attempt one authorized publication and reconcile its exact version. Do not treat a prepared manifest or failed workflow as publication.
