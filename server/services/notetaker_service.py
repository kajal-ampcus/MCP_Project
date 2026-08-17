from nylas import Client

from server.config import (
    NYLAS_API_KEY,
    NYLAS_GRANT_ID,
)


class NotetakerService:

    def __init__(self):

        self.client = Client(
            api_key=NYLAS_API_KEY
        )

        self.grant_id = NYLAS_GRANT_ID

    def create_notetaker(
        self,
        meeting_url,
    ):

        return self.client.notetakers.create(
            self.grant_id,
            {
                "meeting_link": meeting_url
            }
        )