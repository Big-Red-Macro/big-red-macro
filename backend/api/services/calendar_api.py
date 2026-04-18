import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "mock_client_id")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "mock_client_secret")

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
    # Google auto-adds openid/profile scopes. We must relax oauthlib strict matching.
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
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
        return [
            {"start": "11:30", "end": "13:00", "duration_minutes": 90},
            {"start": "17:00", "end": "19:30", "duration_minutes": 150}
        ]
    
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
            busy_blocks.append((start_dt, end_dt))
        
        busy_blocks.sort(key=lambda x: x[0])
        merged_busy = []
        for b in busy_blocks:
            if not merged_busy:
                merged_busy.append(b)
            else:
                last_b = merged_busy[-1]
                if b[0] <= last_b[1]:
                    merged_busy[-1] = (last_b[0], max(last_b[1], b[1]))
                else:
                    merged_busy.append(b)
        
        gaps = []
        current_time = start_of_day
        for b in merged_busy:
            if b[0] > current_time:
                gap_duration = (b[0] - current_time).total_seconds() / 60
                if gap_duration >= 45: 
                    gaps.append({
                        "start": current_time.strftime("%H:%M"),
                        "end": b[0].strftime("%H:%M"),
                        "duration_minutes": gap_duration
                    })
            current_time = max(current_time, b[1])
        
        if current_time < end_of_day:
            gap_duration = (end_of_day - current_time).total_seconds() / 60
            if gap_duration >= 45:
                gaps.append({
                    "start": current_time.strftime("%H:%M"),
                    "end": end_of_day.strftime("%H:%M"),
                    "duration_minutes": gap_duration
                })
                
        return gaps

    except Exception as e:
        logger.error(f"Failed to fetch calendar events: {e}")
        return []
