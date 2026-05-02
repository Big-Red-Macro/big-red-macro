import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/calendar.readonly',
]

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "mock_client_id")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "mock_client_secret")

DEFAULT_FREE_TIME_BLOCKS = [
    {"start": "08:00", "end": "10:00", "duration_minutes": 120, "source": "fallback", "predicted_area": "Central"},
    {"start": "12:00", "end": "14:00", "duration_minutes": 120, "source": "fallback", "predicted_area": "Central"},
    {"start": "17:30", "end": "20:00", "duration_minutes": 150, "source": "fallback", "predicted_area": "West"},
]

AREA_KEYWORDS = {
    "North": [
        "north", "rpcc", "robert purcell", "morrison hall", "appel", "balch",
        "risley", "donlon", "ckb", "toni morrison hall", "high rise",
    ],
    "West": [
        "west", "becker", "bethe", "keeton", "rose", "cook house",
        "alice cook", "noyes", "willard straight",
    ],
    "Central": [
        "central", "statler", "uris", "olin", "gates", "duffield", "rhodes",
        "klarman", "goldwin smith", "rockefeller", "baker lab", "malott",
        "kennedy", "mann", "cornell health", "sage", "barton", "teagle",
        "okenshields", "trillium", "engineering quad", "arts quad",
    ],
}


def infer_campus_area(text: str) -> str:
    normalized = (text or "").lower()
    for area, keywords in AREA_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return area
    return ""


def event_location_text(event: dict) -> str:
    return " ".join(
        str(value)
        for value in [event.get("location"), event.get("summary")]
        if value
    )


def predicted_area(previous_event: dict = None, next_event: dict = None) -> str:
    # Prefer the event right before the meal break: that is where the user likely starts.
    for event in [previous_event, next_event]:
        area = infer_campus_area(event_location_text(event or {}))
        if area:
            return area
    return "Central"

def get_client_config():
    return {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "project_id": "big-red-macro",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": GOOGLE_CLIENT_SECRET,
        }
    }

def get_authorization_url(redirect_uri: str):
    try:
        flow = Flow.from_client_config(
            get_client_config(),
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return authorization_url, state, getattr(flow, 'code_verifier', None)
    except Exception as e:
        logger.error(f"Failed to generate Google auth URL: {e}")
        return None, None, None

def exchange_code(code: str, redirect_uri: str, code_verifier: str = None) -> dict:
    try:
        flow = Flow.from_client_config(
            get_client_config(),
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        kwargs = {}
        if code_verifier:
            kwargs['code_verifier'] = code_verifier
        flow.fetch_token(code=code, **kwargs)
        credentials = flow.credentials
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
    except Exception as e:
        logger.error(f"Failed to exchange Google OAuth code: {e}")
        return {}

def get_free_time_blocks(token_dict: dict, day_date: datetime.date = None):
    """
    Fetch events for the given day and return free blocks of time.
    """
    if not token_dict:
        # Mock gap data if no token provides
        return DEFAULT_FREE_TIME_BLOCKS
    
    try:
        creds = Credentials(**token_dict)
        service = build('calendar', 'v3', credentials=creds)

        if day_date is None:
            day_date = datetime.date.today()
        
        # We look for events between 7 AM and 9 PM local time. (We might need to customize this)
        start_of_day = datetime.datetime.combine(day_date, datetime.time(7, 0)).astimezone()
        end_of_day = datetime.datetime.combine(day_date, datetime.time(21, 0)).astimezone()

        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_of_day.isoformat(),
            timeMax=end_of_day.isoformat(),
            maxResults=100,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        busy_blocks = []
        for e in events:
            if e.get("transparency", "opaque") == "transparent":
                continue # Free event weee
            
            start = e['start'].get('dateTime')
            end = e['end'].get('dateTime')
            if not start or not end:
                # all day event, skip
                continue
            
            start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
            busy_blocks.append({
                "start": start_dt,
                "end": end_dt,
                "summary": e.get("summary", ""),
                "location": e.get("location", ""),
            })
        
        busy_blocks.sort(key=lambda x: x["start"])
        merged_busy = []
        for b in busy_blocks:
            if not merged_busy:
                merged_busy.append(b)
            else:
                last_b = merged_busy[-1]
                if b["start"] <= last_b["end"]:
                    merged_busy[-1] = {
                        **last_b,
                        "end": max(last_b["end"], b["end"]),
                        "summary": last_b.get("summary") or b.get("summary", ""),
                        "location": last_b.get("location") or b.get("location", ""),
                    }
                else:
                    merged_busy.append(b)
        
        gaps = []
        current_time = start_of_day
        previous_event = None
        for b in merged_busy:
            if b["start"] > current_time:
                gap_duration = (b["start"] - current_time).total_seconds() / 60
                if gap_duration >= 45: 
                    gaps.append({
                        "start": current_time.strftime("%H:%M"),
                        "end": b["start"].strftime("%H:%M"),
                        "duration_minutes": gap_duration,
                        "previous_event": previous_event.get("summary", "") if previous_event else "",
                        "previous_location": previous_event.get("location", "") if previous_event else "",
                        "next_event": b.get("summary", ""),
                        "next_location": b.get("location", ""),
                        "predicted_area": predicted_area(previous_event, b),
                    })
            current_time = max(current_time, b["end"])
            previous_event = b
        
        if current_time < end_of_day:
            gap_duration = (end_of_day - current_time).total_seconds() / 60
            if gap_duration >= 45:
                gaps.append({
                    "start": current_time.strftime("%H:%M"),
                    "end": end_of_day.strftime("%H:%M"),
                    "duration_minutes": gap_duration,
                    "previous_event": previous_event.get("summary", "") if previous_event else "",
                    "previous_location": previous_event.get("location", "") if previous_event else "",
                    "next_event": "",
                    "next_location": "",
                    "predicted_area": predicted_area(previous_event, None),
                })
                
        return gaps

    except Exception as e:
        logger.error(f"Failed to fetch calendar events: {e}")
        return DEFAULT_FREE_TIME_BLOCKS
