import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import date
from entities.calendar_event import CalendarEvent
from mock_data.calendar_mock_data import MockCalendarGateway
from use_cases.fetch_calendar import FetchCalendarUseCase


class TestFetchCalendarUseCase:
    def test_returns_calendar_events(self):
        use_case = FetchCalendarUseCase(MockCalendarGateway())
        events = use_case.execute(max_results=10)

        assert len(events) > 0
        assert all(isinstance(e, CalendarEvent) for e in events)

    def test_respects_max_results(self):
        use_case = FetchCalendarUseCase(MockCalendarGateway())
        events = use_case.execute(max_results=3)
        assert len(events) == 3

    def test_parses_all_day_events(self):
        use_case = FetchCalendarUseCase(MockCalendarGateway())
        events = use_case.execute(max_results=10)
        all_day = [e for e in events if e.is_all_day]
        assert len(all_day) >= 1
        for e in all_day:
            assert e.start_time.hour == 0
            assert e.start_time.minute == 0
            assert e.duration_minutes >= 1440

    def test_parses_timed_events(self):
        use_case = FetchCalendarUseCase(MockCalendarGateway())
        events = use_case.execute(max_results=10)
        timed = [e for e in events if not e.is_all_day]
        assert len(timed) >= 1
        for e in timed:
            assert e.duration_minutes > 0
            assert e.duration_minutes < 1440

    def test_detects_category_from_event_type(self):
        use_case = FetchCalendarUseCase(MockCalendarGateway())
        events = use_case.execute(max_results=10)
        tasks = [e for e in events if e.category == 'task']
        assert len(tasks) >= 1

    def test_events_have_summary(self):
        use_case = FetchCalendarUseCase(MockCalendarGateway())
        events = use_case.execute(max_results=10)
        for e in events:
            assert e.summary, "Every event should have a summary"

    def test_some_events_have_location(self):
        use_case = FetchCalendarUseCase(MockCalendarGateway())
        events = use_case.execute(max_results=10)
        with_location = [e for e in events if e.location]
        assert len(with_location) >= 1
