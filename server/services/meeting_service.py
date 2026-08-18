import webbrowser
from datetime import datetime

from server.services.calendar_service import (
    CalendarService,
)

from server.services.notetaker_service import (
    NotetakerService,
)


class MeetingService:

    def __init__(self):

        self.calendar_service = (
            CalendarService()
        )

        self.notetaker_service = (
            NotetakerService()
        )

    def join_next_meeting(
        self,
    ):

        events = (
            self.calendar_service.list_events(
                limit=10
            )
        )

        if not events:

            return {
                "success": False,
                "message": (
                    "No meetings found."
                ),
            }

        now = int(
            datetime.now().timestamp()
        )

        future_events = []

        for event in events:

            # 'when' is a Nylas Timespan dataclass — access via attributes, not .get()
            when = event.get(
                "when",
            )

            if when is None:
                continue

            # Timespan exposes start_time as a plain attribute (int), not a dict key
            start_time = getattr(
                when,
                "start_time",
                None,
            )

            if (
                start_time is not None
                and start_time >= now
            ):

                future_events.append(
                    event
                )

        # Sort by start_time using attribute access (Timespan is a dataclass)
        future_events.sort(
            key=lambda e: getattr(
                e["when"],
                "start_time",
                0,
            )
        )

        for event in future_events:

            # 'conferencing' is a Nylas Details dataclass — not a plain dict
            conferencing = event.get(
                "conferencing"
            )

            if not conferencing:

                continue

            # conferencing.details is a Dict[str, Any] — use attribute access, then .get()
            details = getattr(
                conferencing,
                "details",
                None,
            )

            if not details:
                continue

            meeting_url = (
                details.get("url")
            )

            if meeting_url:

                # Open the meeting link directly in the default browser (Google Meet)
                webbrowser.open(meeting_url)

                # Also dispatch the Nylas notetaker bot to capture transcript/notes
                try:
                    result = (
                        self.notetaker_service.create_notetaker(
                            meeting_url
                        )
                    )
                    notetaker_id = result.get("id")
                    notetaker_status = result.get("status")
                except Exception as e:
                    notetaker_id = None
                    notetaker_status = f"Notetaker error: {e}"

                return {
                    "success": True,
                    "message": (
                        f"Opening meeting in browser: {event['title']}"
                    ),
                    "meeting_title": (
                        event["title"]
                    ),
                    "meeting_url": (
                        meeting_url
                    ),
                    "notetaker_id": notetaker_id,
                    "notetaker_status": notetaker_status,
                    "instructions": (
                        f"The meeting link has been opened in your browser. "
                        f"Notetaker bot is also joining. "
                        + (
                            f"Use get_notetaker_status('{notetaker_id}') to check progress. "
                            f"After the meeting, use get_meeting_transcript('{notetaker_id}') "
                            f"or get_meeting_summary('{notetaker_id}') to retrieve notes."
                            if notetaker_id
                            else ""
                        )
                    ),
                }

        return {
            "success": False,
            "message": (
                "No upcoming meeting with a join link was found."
            ),
        }