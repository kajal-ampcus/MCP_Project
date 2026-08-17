from server.mcp_server import mcp

from server.dependencies import (
    notetaker_service
)


@mcp.tool()
def join_meeting(
    meeting_url: str,
):
    """
    Join a Zoom, Google Meet, or Teams meeting.
    """

    return notetaker_service.create_notetaker(
        meeting_url
    )