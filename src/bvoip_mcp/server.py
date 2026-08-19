import contextvars
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from .api_client import BvoipClient
from .config import Settings

# Per-request credential isolation via contextvars.
# GatewayTokenMiddleware sets this before the MCP handler runs.
# Python asyncio copies context per task, so concurrent SSE connections are isolated.
_gateway_creds_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "bvoip_gateway_creds", default=None
)


def get_client_from_context(settings: Settings) -> BvoipClient | None:
    """Resolve the active BvoipClient for the current request context."""
    api_key = _gateway_creds_var.get()
    if not api_key:
        return None
    return BvoipClient(api_key, settings.bvoip_base_url)


class GatewayTokenMiddleware:
    """ASGI middleware.

    Reads X-Bvoip-Api-Key (required) from request headers and stores it in
    the contextvar. Returns 401 if the header is missing on /mcp requests.
    """

    def __init__(self, app: ASGIApp, settings: Settings):
        self.app = app
        self.settings = settings

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if not path.startswith("/mcp"):
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        api_key = request.headers.get("x-bvoip-api-key")
        if not api_key:
            response = JSONResponse(
                {
                    "error": "Missing credentials",
                    "message": "This server requires the X-Bvoip-Api-Key header",
                    "required_headers": ["X-Bvoip-Api-Key"],
                    "optional_headers": [],
                },
                status_code=401,
            )
            await response(scope, receive, send)
            return

        ctx_token = _gateway_creds_var.set(api_key)
        try:
            await self.app(scope, receive, send)
        finally:
            _gateway_creds_var.reset(ctx_token)


def create_mcp_server(settings: Settings) -> FastMCP:
    """Build the FastMCP server instance and register all Bvoip tools."""
    # DNS-rebinding protection is a browser-oriented safeguard that rejects
    # non-localhost Host headers with 421. Disable it so the server works
    # correctly behind a reverse proxy or docker network.
    mcp = FastMCP(
        name="bvoip-mcp",
        instructions=(
            "Bvoip (vendor platform: 1Stream) is a VoIP/PBX phone system MSPs use "
            "for their own or clients' call handling — extensions, queues/ring "
            "groups, and call routing. This server exposes 1Stream's call-reporting "
            "and status API as read-only tools: call detail records "
            "(bvoip_get_call_logs), live extension/queue phone status "
            "(bvoip_get_phone_statuses), call-volume breakdowns by hour "
            "(bvoip_get_calls_by_hour), by extension "
            "(bvoip_get_calls_by_extension), and aggregate totals "
            "(bvoip_get_calls_leaderboard), plus CRM extension-to-user mappings "
            "(bvoip_get_client_crm_user_extension_mappings, e.g. linking a "
            "ConnectWise member to their phone extension). Typical use: pull "
            "call logs or volume stats for a reporting period, check who is "
            "online/available right now, or resolve which CRM user owns an "
            "extension seen in a call record. All 6 tools are read-only queries "
            "with no required parameters; pass extra_params for additional "
            "vendor-specific filters (e.g. a date range) when known."
        ),
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )

    client_factory: Callable[[], BvoipClient | None] = lambda: get_client_from_context(settings)

    from .tools import reports

    reports.register(mcp, client_factory)

    return mcp
