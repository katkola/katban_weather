from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from entities.calendar_event import CalendarEvent
from use_cases.fetch_calendar import FetchCalendarUseCase


class MockCalendarGateway:
    def __init__(self, timezone_offset: str = "-05:00"):
        self.timezone_offset = timezone_offset

    def get_today_events(self, max_results: int = 10) -> List[Dict[str, Any]]:
        events = self._build_mock_events()
        return events[:max_results]

    def _build_mock_events(self) -> List[Dict[str, Any]]:
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tz = self.timezone_offset

        def dt(hour: int, minute: int) -> str:
            return f"{today.strftime('%Y-%m-%d')}T{hour:02d}:{minute:02d}:00{tz}"

        def date_only(offset_days: int = 0) -> str:
            return (today + timedelta(days=offset_days)).strftime('%Y-%m-%d')

        return [
            {
                'summary': 'Daily Standup',
                'start': {'dateTime': dt(9, 0)},
                'end': {'dateTime': dt(9, 30)},
                'location': 'Conference Room B',
                'eventType': 'default',
            },
            {
                'summary': 'Review Pull Requests',
                'start': {'dateTime': dt(11, 0)},
                'end': {'dateTime': dt(11, 45)},
                'eventType': 'task',
            },
            {
                'summary': 'Write release notes draft',
                'start': {'dateTime': dt(16, 0)},
                'end': {'dateTime': dt(16, 30)},
                'eventType': 'task',
            },
            {
                'summary': 'Yoga Class',
                'start': {'dateTime': dt(17, 0)},
                'end': {'dateTime': dt(18, 0)},
                'location': 'Wellness Center',
                'eventType': 'default',
            },
            {
                'summary': 'Q2 Project Milestone Due',
                'start': {'date': date_only(0)},
                'end': {'date': date_only(2)},
                'eventType': 'task',
            },
        ]


def fetch_mock_events(max_results: int = 10) -> List[CalendarEvent]:
    gateway = MockCalendarGateway()
    use_case = FetchCalendarUseCase(gateway)
    return use_case.execute(max_results)
