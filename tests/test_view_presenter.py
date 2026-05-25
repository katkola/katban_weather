import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from entities.weather_data import WeatherData
from entities.calendar_event import CalendarEvent
from use_cases.display_info import DisplayInfo
from interface_adapters.view_presenter import ViewPresenter


def make_info(weather=None, calendar=None, alerts=None):
    if weather is None:
        weather = [
            WeatherData(72, "F", "5 mph", "NE", "Partly Cloudy", "Cloudy", 45, "2025-06-01T12:00:00Z", "NOW"),
            WeatherData(55, "F", "10 mph", "N", "Clear", "Clear night", 50, "2025-06-01T18:00:00Z", "TONIGHT"),
        ]
    if calendar is None:
        calendar = [
            CalendarEvent("Standup", datetime(2025, 6, 1, 9, 0), datetime(2025, 6, 1, 9, 30), location="Room B", category="event"),
            CalendarEvent("All Day Event", datetime(2025, 6, 1, 0, 0), datetime(2025, 6, 2, 0, 0), category="event"),
            CalendarEvent("Review PRs", datetime(2025, 6, 1, 11, 0), datetime(2025, 6, 1, 11, 30), category="task"),
        ]
    if alerts is None:
        alerts = [
            {'properties': {'event': 'Heat Advisory', 'headline': 'Heat Advisory until 8 PM', 'severity': 'Moderate'}},
        ]
    return DisplayInfo(weather_periods=weather, calendar_events=calendar, alerts=alerts)


class TestPresentWeather:
    def test_current_weather_has_all_fields(self):
        vm = ViewPresenter().present_weather(make_info())
        cw = vm['current']

        assert cw['temp_text'] == '72°F'
        assert cw['condition'] == 'Partly Cloudy'
        assert cw['art'] != ''
        assert cw['humidity'] == 'Humidity: 45%'
        assert cw['wind'] == 'Wind: 5 mph NE'

    def test_hourly_includes_three_periods(self):
        vm = ViewPresenter().present_weather(make_info())
        assert len(vm['hourly']) == 2
        assert vm['hourly'][0]['name'] == 'NOW'
        assert vm['hourly'][1]['name'] == 'TONIGHT'

    def test_hourly_has_formatted_fields(self):
        vm = ViewPresenter().present_weather(make_info())
        period = vm['hourly'][0]

        assert '72°F' in period['temp']
        assert 'Humidity:' in period['humidity']
        assert 'Wind:' in period['wind']
        assert 'Partly Cloudy' in period['condition']

    def test_empty_weather_returns_placeholders(self):
        vm = ViewPresenter().present_weather(make_info(weather=[]))
        assert vm['current']['temp_text'] == '--°'
        assert vm['current']['condition'] == '--'
        assert vm['hourly'] == []


class TestPresentCalendar:
    def test_splits_into_sections(self):
        vm = ViewPresenter().present_calendar(make_info())
        sections = vm['sections']
        assert len(sections) >= 1

    def test_all_day_section_first(self):
        vm = ViewPresenter().present_calendar(make_info())
        assert vm['sections'][0]['title'] == 'ALL DAY'
        assert vm['sections'][0]['color'] == '#6ab04c'

    def test_events_section_contains_timed_events(self):
        vm = ViewPresenter().present_calendar(make_info())
        events = next(s for s in vm['sections'] if s['title'] == 'EVENTS')
        assert len(events['items']) >= 1
        assert events['items'][0]['time'] == '09:00 AM'
        assert events['items'][0]['title'] == 'Standup'
        assert events['items'][0]['location'] == 'Room B'

    def test_tasks_section_contains_tasks(self):
        vm = ViewPresenter().present_calendar(make_info())
        tasks = next(s for s in vm['sections'] if s['title'] == 'TASKS')
        assert len(tasks['items']) >= 1
        assert tasks['items'][0]['title'] == 'Review PRs'

    def test_all_day_items_show_all_day_text(self):
        vm = ViewPresenter().present_calendar(make_info())
        all_day = vm['sections'][0]
        for item in all_day['items']:
            assert item['time'] == 'All Day'

    def test_empty_calendar_returns_no_sections(self):
        vm = ViewPresenter().present_calendar(make_info(calendar=[]))
        assert vm['sections'] == []

    def test_item_without_location(self):
        cal = [
            CalendarEvent("No Loc", datetime(2025, 6, 1, 14, 0), datetime(2025, 6, 1, 15, 0), category="event"),
        ]
        vm = ViewPresenter().present_calendar(make_info(calendar=cal))
        item = vm['sections'][0]['items'][0]
        assert item['location'] is None


class TestPresentAlerts:
    def test_alerts_included_in_weather_view_model(self):
        vm = ViewPresenter().present_weather(make_info())
        assert 'alerts' in vm
        assert len(vm['alerts']) == 1

    def test_alert_has_event_headline_severity(self):
        vm = ViewPresenter().present_weather(make_info())
        a = vm['alerts'][0]
        assert a['event'] == 'Heat Advisory'
        assert a['headline'] == 'Heat Advisory until 8 PM'
        assert a['severity'] == 'Moderate'

    def test_empty_alerts_returns_empty_list(self):
        vm = ViewPresenter().present_weather(make_info(alerts=[]))
        assert vm['alerts'] == []

    def test_none_alerts_returns_empty_list(self):
        info = DisplayInfo(weather_periods=make_info().weather_periods, calendar_events=make_info().calendar_events, alerts=None)
        vm = ViewPresenter().present_weather(info)
        assert vm['alerts'] == []

    def test_multiple_alerts(self):
        alerts = [
            {'properties': {'event': 'Flood Watch', 'headline': 'Flood Watch', 'severity': 'Severe'}},
            {'properties': {'event': 'Wind Advisory', 'headline': 'Wind Advisory', 'severity': 'Minor'}},
        ]
        vm = ViewPresenter().present_weather(make_info(alerts=alerts))
        assert len(vm['alerts']) == 2

    def test_alert_missing_fields_uses_defaults(self):
        alerts = [{'properties': {}}]
        vm = ViewPresenter().present_weather(make_info(alerts=alerts))
        a = vm['alerts'][0]
        assert a['event'] == 'Alert'
        assert a['severity'] == 'Unknown'
