from collections.abc import Callable

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .._json import dump_json_capped
from ..api_client import BvoipClient, BvoipError
from ._common import NO_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], BvoipClient | None]) -> None:

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def bvoip_get_call_logs(extra_params: dict[str, str] | None = None) -> str:
        """List call detail records (start/end time, direction, extension,
        queue/ring group, talk time, recording link, linked CRM ticket, etc).

        No required parameters. The vendor's full filter set (e.g. date
        range) is only documented in 1Stream's partner-gated Postman
        collection; pass any such filters via extra_params if known.

        Args:
            extra_params: Optional raw query-string parameters to forward,
                for filters not covered above.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.get("/GetCallLogs", params=extra_params)
            return dump_json_capped(result)
        except BvoipError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def bvoip_get_phone_statuses(extra_params: dict[str, str] | None = None) -> str:
        """List current extension/queue phone statuses (registration state,
        logged-in/available state, agents assigned/available/connected for
        queues, current custom status, etc).

        No required parameters.

        Args:
            extra_params: Optional raw query-string parameters to forward,
                for filters not covered above.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.get("/GetPhoneStatuses", params=extra_params)
            return dump_json_capped(result)
        except BvoipError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def bvoip_get_calls_by_hour(extra_params: dict[str, str] | None = None) -> str:
        """Get call volume (inbound/outbound/total/unanswered) broken down
        by hour of day for the reporting period.

        No required parameters. The vendor's period/date-range filters are
        only documented in 1Stream's partner-gated Postman collection; pass
        any such filters via extra_params if known.

        Args:
            extra_params: Optional raw query-string parameters to forward,
                for filters not covered above.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.get("/GetCallsByHour", params=extra_params)
            return dump_json_capped(result)
        except BvoipError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def bvoip_get_calls_leaderboard(extra_params: dict[str, str] | None = None) -> str:
        """Get aggregate call counts (inbound/outbound/total/unanswered)
        for the reporting period.

        No required parameters. The vendor's period/date-range filters are
        only documented in 1Stream's partner-gated Postman collection; pass
        any such filters via extra_params if known.

        Args:
            extra_params: Optional raw query-string parameters to forward,
                for filters not covered above.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.get("/GetCallsLeaderBoard", params=extra_params)
            return dump_json_capped(result)
        except BvoipError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def bvoip_get_calls_by_extension(extra_params: dict[str, str] | None = None) -> str:
        """Get per-extension call stats (inbound/outbound/total counts,
        average and total talk time) for the reporting period.

        No required parameters. The vendor's period/date-range filters are
        only documented in 1Stream's partner-gated Postman collection; pass
        any such filters via extra_params if known.

        Args:
            extra_params: Optional raw query-string parameters to forward,
                for filters not covered above.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.get("/GetCallsByExtension", params=extra_params)
            return dump_json_capped(result)
        except BvoipError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def bvoip_get_client_crm_user_extension_mappings(
        extra_params: dict[str, str] | None = None,
    ) -> str:
        """List mappings between 1Stream users/extensions and the linked
        CRM (e.g. ConnectWise) member accounts — extension, CRM member ID
        and username, security role, license plan, etc.

        No required parameters.

        Args:
            extra_params: Optional raw query-string parameters to forward,
                for filters not covered above.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.get(
                "/GetClientCRMUserExtensionMappings", params=extra_params
            )
            return dump_json_capped(result)
        except BvoipError as e:
            return e.to_envelope()
