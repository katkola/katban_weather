from typing import List, Optional
from entities.calendar_event import CalendarEvent
from datetime import datetime


class FetchCalendarUseCase:
    def __init__(self, calendar_gateway):
        self.calendar_gateway = calendar_gateway

    def execute(self, max_results: int = 10) -> List[CalendarEvent]:
        """Fetch calendar events for today"""
        raw_events = self.calendar_gateway.get_today_events(max_results)

        events = []
        for raw_event in raw_events:
            start_str = raw_event['start'].get(
                'dateTime', raw_event['start'].get('date'))
            end_str = raw_event['end'].get(
                'dateTime', raw_event['end'].get('date'))

            if 'T' in start_str:
                start_time = datetime.fromisoformat(
                    start_str.replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(
                    end_str.replace('Z', '+00:00'))
            else:
                start_time = datetime.fromisoformat(start_str)
                end_time = datetime.fromisoformat(end_str)

            event_type = raw_event.get('eventType', 'default')
            category = 'event' if event_type == 'default' else event_type

            event = CalendarEvent(
                summary=raw_event.get('summary', 'No Title'),
                start_time=start_time,
                end_time=end_time,
                location=raw_event.get('location'),
                description=raw_event.get('description'),
                category=category,
                source=raw_event.get('calendar_name'),
            )
            events.append(event)

        return events
