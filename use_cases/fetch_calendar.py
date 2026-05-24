from typing import List, Optional
from entities.calendar_event import CalendarEvent
from datetime import datetime

class FetchCalendarUseCase:
    def __init__(self, calendar_gateway):
        self.calendar_gateway = calendar_gateway
    
    def execute(self, max_results: int = 10) -> List[CalendarEvent]:
        """Fetch calendar events for today"""
        # Get raw events from the gateway
        raw_events = self.calendar_gateway.get_today_events(max_results)
        
        # Convert raw events to CalendarEvent entities
        events = []
        for raw_event in raw_events:
            # Parse the start and end times
            start_str = raw_event['start'].get('dateTime', raw_event['start'].get('date'))
            end_str = raw_event['end'].get('dateTime', raw_event['end'].get('date'))
            
            # Handle date-only (all-day) events vs date-time events
            if 'T' in start_str:
                # Date-time format
                start_time = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            else:
                # Date-only format (all-day event)
                start_time = datetime.fromisoformat(start_str)
                end_time = datetime.fromisoformat(end_str)
            
            event = CalendarEvent(
                summary=raw_event.get('summary', 'No Title'),
                start_time=start_time,
                end_time=end_time,
                location=raw_event.get('location'),
                description=raw_event.get('description')
            )
            events.append(event)
        
        return events