"""Google Calendar integration service"""
import os
from datetime import datetime
from typing import List, Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from models.chat import CalendarEvent

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class CalendarService:
    def __init__(self):
        self.client_config = {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uris": [GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

    def get_authorization_url(self) -> str:
        """Get Google OAuth authorization URL"""
        flow = Flow.from_client_config(
            self.client_config,
            scopes=SCOPES,
            redirect_uri=GOOGLE_REDIRECT_URI
        )

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )

        return authorization_url

    def exchange_code_for_token(self, code: str) -> Credentials:
        """Exchange authorization code for access token"""
        flow = Flow.from_client_config(
            self.client_config,
            scopes=SCOPES,
            redirect_uri=GOOGLE_REDIRECT_URI
        )

        flow.fetch_token(code=code)
        return flow.credentials

    async def sync_calendar_events(
        self,
        user_id: int,
        credentials: Credentials,
        db: Session,
        max_results: int = 50
    ) -> List[CalendarEvent]:
        """Sync events from Google Calendar"""
        service = build('calendar', 'v3', credentials=credentials)

        # Get upcoming events
        now = datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        synced_events = []

        for event in events:
            google_event_id = event['id']

            # Check if event already exists
            existing_event = db.query(CalendarEvent).filter(
                CalendarEvent.google_event_id == google_event_id
            ).first()

            # Parse dates
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            is_all_day = 'date' in event['start']

            if 'T' in start:
                start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(end.replace('Z', '+00:00'))
            else:
                start_time = datetime.fromisoformat(start)
                end_time = datetime.fromisoformat(end)

            event_data = {
                'user_id': user_id,
                'google_event_id': google_event_id,
                'title': event.get('summary', 'Sem título'),
                'description': event.get('description', ''),
                'location': event.get('location', ''),
                'start_time': start_time,
                'end_time': end_time,
                'is_all_day': is_all_day,
                'synced_at': datetime.utcnow()
            }

            if existing_event:
                # Update existing event
                for key, value in event_data.items():
                    setattr(existing_event, key, value)
                db.commit()
                db.refresh(existing_event)
                synced_events.append(existing_event)
            else:
                # Create new event
                calendar_event = CalendarEvent(**event_data)
                db.add(calendar_event)
                db.commit()
                db.refresh(calendar_event)
                synced_events.append(calendar_event)

        return synced_events

    async def get_user_events(
        self,
        user_id: int,
        db: Session,
        limit: int = 20
    ) -> List[CalendarEvent]:
        """Get user's calendar events from database"""
        return db.query(CalendarEvent).filter(
            CalendarEvent.user_id == user_id,
            CalendarEvent.start_time >= datetime.utcnow()
        ).order_by(CalendarEvent.start_time).limit(limit).all()
