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

            when = event.get(
                "when",
                {}
            )

            start_time = when.get(
                "start_time"
            )

            if (
                start_time
                and start_time >= now
            ):

                future_events.append(
                    event
                )

        future_events.sort(
            key=lambda event:
            event["when"][
                "start_time"
            ]
        )

        for event in future_events:

            conferencing = event.get(
                "conferencing"
            )

            if not conferencing:

                continue

            details = (
                conferencing.get(
                    "details",
                    {}
                )
            )

            meeting_url = (
                details.get("url")
            )

            if meeting_url:

                result = (
                    self.notetaker_service.create_notetaker(
                        meeting_url
                    )
                )

                return {
                    "success": True,
                    "meeting": (
                        event["title"]
                    ),
                    "meeting_url": (
                        meeting_url
                    ),
                    "notetaker": str(
                        result
                    ),
                }

        return {
            "success": False,
            "message": (
                "No meeting link found."
            ),
        }