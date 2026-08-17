from nylas import Client

from server.config import (
    NYLAS_API_KEY,
    NYLAS_GRANT_ID,
)

client = Client(
    api_key=NYLAS_API_KEY
)

try:

    response = client.notetakers.create(
        NYLAS_GRANT_ID,
        {
            "meeting_link": "https://meet.google.com/rgs-uqyy-wpp"
        }
    )

    print(response)

except Exception as e:

    print(type(e))
    print(e)