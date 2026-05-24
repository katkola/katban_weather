import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, timedelta
from entities.calendar_event import CalendarEvent
from entities.weather_data import WeatherData


class TestCalendarEvent:
    def test_creation(self):
        start = datetime(2025, 6, 1, 10, 0, 0)
        end = datetime(2025, 6, 1, 11, 0, 0)
        e = CalendarEvent("Meeting", start, end, location="Room A", description="Discuss", category="event")

        assert e.summary == "Meeting"
        assert e.start_time == start
        assert e.end_time == end
        assert e.location == "Room A"
        assert e.description == "Discuss"
        assert e.category == "event"
        assert e.duration_minutes == 60
        assert not e.is_all_day

    def test_all_day_detection(self):
        start = datetime(2025, 6, 1, 0, 0, 0)
        end = datetime(2025, 6, 2, 0, 0, 0)
        e = CalendarEvent("All Day", start, end)
        assert e.is_all_day
        assert e.duration_minutes == 1440
        assert e.category == "event"

    def test_task_category(self):
        start = datetime(2025, 6, 1, 14, 0, 0)
        end = datetime(2025, 6, 1, 15, 0, 0)
        e = CalendarEvent("Task", start, end, category="task")
        assert e.category == "task"
        assert not e.is_all_day

    def test_multi_day_not_all_day(self):
        start = datetime(2025, 6, 1, 10, 0, 0)
        end = datetime(2025, 6, 3, 10, 0, 0)
        e = CalendarEvent("Multi-day", start, end)
        assert not e.is_all_day
        assert e.duration_minutes == 2880

    def test_to_dict(self):
        start = datetime(2025, 6, 1, 10, 0, 0)
        end = datetime(2025, 6, 1, 11, 0, 0)
        e = CalendarEvent("Test", start, end, location="Room", description="Desc", category="task")
        d = e.to_dict()
        assert d["summary"] == "Test"
        assert d["start_time"] == "2025-06-01T10:00:00"
        assert d["end_time"] == "2025-06-01T11:00:00"
        assert d["location"] == "Room"
        assert d["description"] == "Desc"
        assert d["category"] == "task"

    def test_default_category(self):
        start = datetime(2025, 6, 1, 0, 0, 0)
        end = datetime(2025, 6, 1, 1, 0, 0)
        e = CalendarEvent("Default", start, end)
        assert e.category == "event"

    def test_empty_location_description(self):
        start = datetime(2025, 6, 1, 0, 0, 0)
        end = datetime(2025, 6, 1, 1, 0, 0)
        e = CalendarEvent("Minimal", start, end)
        assert e.location is None
        assert e.description is None


class TestWeatherData:
    def test_creation(self):
        w = WeatherData(72, "F", "5 mph", "NE", "Sunny", "Sunny all day", 45, "2025-06-01T12:00:00Z", "NOW")
        assert w.temperature == 72
        assert w.temperature_unit == "F"
        assert w.wind_speed == "5 mph"
        assert w.wind_direction == "NE"
        assert w.short_forecast == "Sunny"
        assert w.detailed_forecast == "Sunny all day"
        assert w.relative_humidity == 45
        assert w.timestamp == "2025-06-01T12:00:00Z"
        assert w.period_name == "NOW"

    def test_default_period_name(self):
        w = WeatherData(72, "F", "5 mph", "NE", "Sunny", "Sunny", 45)
        assert w.period_name is None

    def test_to_dict(self):
        w = WeatherData(72, "F", "5 mph", "NE", "Sunny", "Sunny all day", 45, "2025-06-01T12:00:00Z", "NOW")
        d = w.to_dict()
        assert d["temperature"] == 72
        assert d["temperature_unit"] == "F"
        assert d["wind_speed"] == "5 mph"
        assert d["short_forecast"] == "Sunny"
        assert d["period_name"] == "NOW"
        assert d["timestamp"] == "2025-06-01T12:00:00Z"
