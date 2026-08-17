import requests

from server.config import (
    NYLAS_API_KEY,
    NYLAS_GRANT_ID,
)


class NotetakerService:

    def __init__(self):
        self.api_key = NYLAS_API_KEY
        self.grant_id = NYLAS_GRANT_ID
        self.base_url = "https://api.us.nylas.com"

    def create_notetaker(
        self,
        meeting_url: str,
    ) -> dict:
        """
        Send a Nylas Notetaker bot to the given meeting URL.

        The Nylas Python SDK v6 has a bug where notetakers.create(grant_id, body)
        concatenates grant_id directly onto the hostname string instead of the
        URL path, producing host='api.us.nylas.com<grant_id>' and a DNS failure.
        We call the REST API directly with requests to avoid this entirely.
        """
        url = (
            f"{self.base_url}"
            f"/v3/grants/{self.grant_id}/notetakers"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "meeting_link": meeting_url,
        }

        try:
            resp = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            # Nylas wraps the result in a "data" key
            return data.get("data", data)

        except requests.HTTPError as exc:
            try:
                error_body = exc.response.json()
                msg = (
                    error_body.get("message")
                    or error_body.get("error")
                    or exc.response.text
                )
            except Exception:
                msg = exc.response.text

            raise RuntimeError(
                f"Nylas API error {exc.response.status_code}: {msg}"
            ) from exc

        except requests.RequestException as exc:
            raise RuntimeError(
                f"Network error contacting Nylas: {exc}"
            ) from exc