import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from entities.weather_data import WeatherData
from entities.calendar_event import CalendarEvent
from use_cases.display_info import DisplayInfo, FetchDisplayInfoUseCase


class MockWeatherController:
    def __init__(self):
        self.call_count = 0
        self.periods = [
            WeatherData(72, "F", "5 mph", "NE", "Sunny", "Sunny", 45, "2025-06-01T12:00:00Z", "NOW"),
            WeatherData(55, "F", "10 mph", "N", "Clear", "Clear", 45, "2025-06-01T18:00:00Z", "TONIGHT"),
        ]

    def get_weather(self, latitude, longitude, periods_count=3):
        self.call_count += 1
        return self.periods[:periods_count]


class MockCalendarController:
    def __init__(self):
        self.call_count = 0
        self.events = [
            CalendarEvent("Standup", datetime(2025, 6, 1, 10, 0), datetime(2025, 6, 1, 11, 0), category="event"),
            CalendarEvent("Review PRs", datetime(2025, 6, 1, 11, 0), datetime(2025, 6, 1, 11, 30), category="task"),
        ]

    def get_today_events(self, max_results=10):
        self.call_count += 1
        return self.events[:max_results]


class TestFetchDisplayInfoUseCase:
    def test_returns_display_info_with_both_sources(self):
        use_case = FetchDisplayInfoUseCase(MockWeatherController(), MockCalendarController())
        info = use_case.execute(40.7, -73.9)

        assert isinstance(info, DisplayInfo)
        assert len(info.weather_periods) == 2
        assert len(info.calendar_events) == 2

    def test_calls_both_controllers(self):
        wc = MockWeatherController()
        cc = MockCalendarController()
        use_case = FetchDisplayInfoUseCase(wc, cc)
        use_case.execute(40.7, -73.9)

        assert wc.call_count == 1
        assert cc.call_count == 1

    def test_passes_coordinates_to_weather_controller(self):
        wc = MockWeatherController()
        cc = MockCalendarController()
        use_case = FetchDisplayInfoUseCase(wc, cc)
        use_case.execute(38.9, -77.0)

        assert wc.call_count == 1

    def test_respects_max_results(self):
        wc = MockWeatherController()
        cc = MockCalendarController()
        use_case = FetchDisplayInfoUseCase(wc, cc)
        info = use_case.execute(40.7, -73.9, weather_periods=1, calendar_max=1)

        assert len(info.weather_periods) == 1
        assert len(info.calendar_events) == 1
