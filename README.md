# bvoip-mcp

MCP server for **Bvoip / 1Stream** — exposes the 1Stream `ClientAccess.svc` REST
API's call-reporting, phone-status and CRM-extension-mapping endpoints as MCP
tools.

> Naming note: MSPbots' own integration is registered as "Bvoip"
> (`subjectCode=BVOIP`); the underlying vendor platform/API is "1Stream"
> (`portal.1stream.com`). This MCP covers exactly the 6 GET endpoints
> MSPbots itself has configured for this integration — see **Known Gaps**
> below for why the scope stops there.

<div align="center">

## MSPbots Connector

**The MCP Gateway built for MSPs: visible, controlled, and your data stays where it belongs.**

[**Get started at connect.mspbots.ai →**](https://connect.mspbots.ai)

</div>

---

MSPbots Connector gives your AI clients one MCP URL to reach your entire MSP stack (RMM, PSA, documentation, security, finance), and gives you control over who can call which tool and a record of everything that was called.

**Hosted service: [connect.mspbots.ai](https://connect.mspbots.ai)** · Free to use.

### Why Connector

![MSPbots Connector](https://stgoss.mspbots.ai/files/mcp/mspbots-mcp.png)

| | |
|---|---|
| **Visible** | Every tool call is logged: who, which vendor, when. Usage dashboard, CSV export, SIEM streaming. |
| **Controlled** | Role-based, per-tool allowlist. Deny by default. |
| **Protected** | Credentials encrypted per record. AI clients never see your vendor passwords or tokens. |
| **MSP-native** | Built for the MSP stack only: RMM, PSA, documentation, security, finance. |

### Quick start

1. **Sign up** at [connect.mspbots.ai](https://connect.mspbots.ai).
2. **Connect your vendors.** Pick from 150+ connectors and authorize each one on the vendor's own page, or bring your own API keys. No extra vendor accounts needed.
3. **Set access.** Create roles and decide which tools each role may call. Nothing is allowed until you allow it.
4. **Add your MCP URL to your AI client.** Copy the URL from your Connector dashboard into Claude, ChatGPT, Cursor, VS Code, Gemini, Codex, or any MCP-capable client.
5. **Ask your AI to do real work**, and watch every call appear in the audit log.

### Features

**Unified gateway**
- One MCP URL for all your AI clients
- 150+ connectors across the MSP stack
- Custom MCP servers supported, free
- Authorization happens on each vendor's own page; the AI never sees passwords or tokens
- Bring your own credentials: use the vendor API keys you already have
- Multiple accounts per app; connect once, reuse across AI clients
- Tool search: finds the right action for the task
- One sign-in; vendor credentials are injected behind the scenes and OAuth tokens refresh automatically

**Visibility**
- Audit log for every tool call (who, which vendor, when)
- Usage dashboard: call volume, top vendors, error rate, per-user activity
- Export audit logs to CSV, or stream to Loki, Graylog, or LogScale (SIEM)
- Optional recording of tool arguments and result summaries (off by default, enabled per organization)

**Control**
- Per-role, per-tool allowlist, deny by default
- owner / admin / member roles
- SCIM provisioning with Entra ID, Okta, JumpCloud, and Google Workspace

**Security**
- Credentials encrypted one record at a time (AES-256-GCM, per-record key)
- AI clients authenticate with OAuth 2.1 + PKCE
- Vendor responses are scanned for prompt-injection patterns and returned as structured data. This is one layer of defense, not a guarantee against every attack.
- Static egress IP for customer firewall and API allowlisting

### Pricing

**Free.**

Links: [connect.mspbots.ai](https://connect.mspbots.ai) · [mspbots.ai](https://mspbots.ai)

---

## Overview

- Stateless HTTP service. No credentials are ever persisted — each request
  supplies its own API key via a header, and it is used only for the
  lifetime of that single request.
- Supports concurrent requests; per-request credential isolation is done
  via Python `contextvars`, not a global/shared client instance.
- Entry points: `POST /mcp` (MCP protocol) and `GET /health` (health check).
- Default port: `8080` (configurable via `MCP_HTTP_PORT`).

## Authentication

1Stream authenticates with a single static **API key**, created in the
1Stream portal (see "Creating API Keys in 1Stream" at
[docs.1stream.com](https://docs.1stream.com/apis/1stream-api)). 1Stream's own
integration convention sends this key as the raw value of the
`Authorization` header — **no `Bearer ` prefix** — and this server forwards
it exactly that way.

### HEADER Authentication Parameters

| Header | Type | Required | Default | Allowed values | Description | Example |
|---|---|---|---|---|---|---|
| `X-Bvoip-Api-Key` | string | Yes | None | None | 1Stream static API Key, forwarded as-is as the upstream `Authorization` request header (without the `Bearer ` prefix) | `a1b2c3d4e5f6...` |

Missing the header returns `401`:
```json
{
  "error": "Missing credentials",
  "message": "This server requires the X-Bvoip-Api-Key header",
  "required_headers": ["X-Bvoip-Api-Key"],
  "optional_headers": []
}
```

## Environment Variables

| Variable | Type | Required | Default | Description |
|---|---|---|---|---|
| `MCP_HTTP_PORT` | int | No | `8080` | HTTP listen port |
| `MCP_HTTP_HOST` | string | No | `0.0.0.0` | HTTP listen address |
| `BVOIP_BASE_URL` | string | No | `https://portal.1stream.com/api/ClientAccess.svc` | 1Stream ClientAccess base URL |

## MCP Endpoint

- `POST /mcp` — MCP protocol (streamable HTTP transport)
- `GET /health` — health check, returns `{"status": "ok", "service": "bvoip-mcp", "transport": "http"}`

## Tool List

All 6 tools are plain `GET` calls against `ClientAccess.svc` with **no
required parameters** — this matches exactly how MSPbots itself calls this
integration today. Each tool accepts an optional `extra_params` pass-through
dict for any additional query-string filters (e.g. a date range), since
1Stream's full filter reference is only published in their partner-gated
Postman collection (see **Known Gaps**).

| Tool | Description | Parameters |
|---|---|---|
| `bvoip_get_call_logs` | List call detail records (start/end time, direction, extension, queue/ring group, call duration, recording link, associated CRM ticket, etc.) | `extra_params: dict[str,str] \| None` |
| `bvoip_get_phone_statuses` | List current extension/queue statuses (registration status, login/availability status, queue agent assigned/available/on-call counts, custom statuses, etc.) | `extra_params: dict[str,str] \| None` |
| `bvoip_get_calls_by_hour` | Call volume by hour (inbound/outbound/total/unanswered) | `extra_params: dict[str,str] \| None` |
| `bvoip_get_calls_leaderboard` | Total call volume within the period (inbound/outbound/total/unanswered) | `extra_params: dict[str,str] \| None` |
| `bvoip_get_calls_by_extension` | Call statistics by extension (inbound/outbound/total, average and total call duration) | `extra_params: dict[str,str] \| None` |
| `bvoip_get_client_crm_user_extension_mappings` | List mappings between 1Stream users/extensions and associated CRM (e.g. ConnectWise) member accounts (extension, CRM member ID/username, role, plan, etc.) | `extra_params: dict[str,str] \| None` |

## Test Example

```bash
# Health check
curl -s http://localhost:8080/health

# Call a tool via the MCP protocol (streamable HTTP) — requires an
# initialize handshake first per the MCP spec; abbreviated example below
# shows the tool-call request body only:
curl -s -X POST http://localhost:8080/mcp \
  -H "X-Bvoip-Api-Key: <your-1stream-api-key>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: <session-id-from-initialize>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "bvoip_get_phone_statuses",
      "arguments": {}
    }
  }'
```

Expected: `200` with the phone-status list on a valid key; `401`/`403`
(surfaced by the tool as `Error: Bvoip API error 401/403: ...`) on an
invalid or revoked key.

## API Reference

- Overview: https://docs.1stream.com/apis/1stream-api
- Full REST/Postman API reference: **partner-gated** — 1Stream states "please
  reach out to our team at partners@bvoip.com to request the documentation,
  or if you're an active partner you can find it at Partners > Resources >
  Automation and APIs." No public Swagger/OpenAPI spec exists.
- A public `API Fields.xlsx` (linked from the overview page above) documents
  the response fields for the endpoints below, with no auth/parameter detail.

## Known Gaps

- **Scope is exactly MSPbots' 6 configured endpoints, not the vendor's full
  API surface** — unlike every other vendor tackled in this MCP program,
  1Stream's REST API documentation is fully partner-gated. There is no
  public reference beyond this overview page and the fields spreadsheet, so
  there was no larger public spec to weigh a broader scope against.
- The fields spreadsheet documents one additional endpoint,
  `GetCallSegmentLogs` (call-leg-level detail), that MSPbots does **not**
  currently call — intentionally left out of this server for the same
  reason; can be added on request if a use case emerges.
- Response field names/types below are sourced from the public `API
  Fields.xlsx`, not a formal schema — treat them as documentation, not a
  contract. Request-side filter parameters (e.g. date range) are not
  publicly documented at all; `extra_params` is provided so a caller who
  has partner-level API access can still pass them through.
