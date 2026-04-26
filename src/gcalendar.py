import os
from datetime import datetime, timezone, timedelta

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

_JST = timezone(timedelta(hours=9))
_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def get_today_events() -> list[dict]:
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        scopes=_SCOPES,
    )

    service = build("calendar", "v3", credentials=creds)

    now = datetime.now(_JST)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = now.replace(hour=23, minute=59, second=59, microsecond=0)

    result = service.events().list(
        calendarId="primary",
        timeMin=day_start.isoformat(),
        timeMax=day_end.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = []
    for item in result.get("items", []):
        summary = item.get("summary", "（無題）")
        start = item["start"]
        if "dateTime" in start:
            dt = datetime.fromisoformat(start["dateTime"]).astimezone(_JST)
            time_str = dt.strftime("%H:%M")
        else:
            time_str = "終日"
        events.append({"time": time_str, "summary": summary})

    return events
