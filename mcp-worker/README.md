# Location Potential MCP Worker

Read-only MCP server for the published Location Potential dataset. Tools: `list_cities`, `list_concepts`, `get_city_zones`, `rank_zones`, `explain_zone`, `compare_zones`.

Every returned quantitative field retains an `evidence_label` of `OBSERVED`, `AREA CONTEXT` or `MODELLED`. Coordinates are shortlist anchors, never premises availability.

## Deploy

1. Create/sign in to Cloudflare.
2. `cd mcp-worker && npm install`
3. `npx wrangler login`
4. `npm run deploy`
5. Use the returned `/mcp` URL as the remote MCP endpoint.

No secrets, payments or write actions. Upstream public JSON is cached for one hour.
