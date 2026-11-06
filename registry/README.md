# Unpublished registry draft

`server.draft.json` is remote-only metadata for the external API-key endpoint. It is not a registry submission or an acceptance claim. The service's native OAuth endpoint is a separate route.

Before publishing, verify the deployed external MCP handshake and actual authenticated tool call, current schema, description/version and ownership of the GitHub namespace. Authenticate through the official publisher and review the complete record before publication. Never replace the secret placeholder with an actual key in a public file.

The `repository` property is omitted because this kit contains client/skill source, not the hosted MCP server source. Use the public website for setup and beta status.

Official references: [remote server metadata](https://modelcontextprotocol.io/registry/remote-servers), [publisher authentication](https://modelcontextprotocol.io/registry/authentication), [schema](https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json).
