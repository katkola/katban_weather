import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mock_data.calendar_mock_data import MockCalendarGateway
from mock_data.weather_mock_data import MockWeatherGateway
from use_cases.fetch_calendar import FetchCalendarUseCase
from use_cases.fetch_weather import FetchWeatherUseCase


class TestMockCalendarGateway:
    def test_mock_gateway_returns_google_api_style_dicts(self):
        gateway = MockCalendarGateway()
        events = gateway.get_today_events(max_results=10)

        assert len(events) > 0
        for e in events:
            assert 'summary' in e
            assert 'start' in e
            assert 'end' in e
            start = e['start']
            assert 'dateTime' in start or 'date' in start
            end = e['end']
            assert 'dateTime' in end or 'date' in end

    def test_mock_events_are_parseable_by_use_case(self):
        gateway = MockCalendarGateway()
        use_case = FetchCalendarUseCase(gateway)
        events = use_case.execute(max_results=10)

        assert len(events) == 10

    def test_respects_max_results(self):
        gateway = MockCalendarGateway()
        events = gateway.get_today_events(max_results=3)
        assert len(events) == 3

    def test_has_mix_of_event_types(self):
        gateway = MockCalendarGateway()
        use_case = FetchCalendarUseCase(gateway)
        events = use_case.execute(max_results=10)

        tasks = [e for e in events if e.category == 'task']
        regular = [e for e in events if e.category == 'event']
        all_day = [e for e in events if e.is_all_day]
        timed = [e for e in events if not e.is_all_day]

        assert len(tasks) >= 1
        assert len(regular) >= 1
        assert len(all_day) >= 1
        assert len(timed) >= 1


class TestMockWeatherGateway:
    def test_gateway_returns_points(self):
        gw = MockWeatherGateway()
        pts = gw.get_points(40.7, -73.9)
        assert 'properties' in pts
        assert 'forecast' in pts['properties']
        assert 'forecastHourly' in pts['properties']

    def test_gateway_returns_forecast(self):
        gw = MockWeatherGateway()
        forecast = gw.get_forecast('https://mock/forecast')
        assert 'properties' in forecast
        assert 'periods' in forecast['properties']
        assert len(forecast['properties']['periods']) >= 2

    def test_gateway_returns_hourly(self):
        gw = MockWeatherGateway()
        hourly = gw.get_hourly_forecast('https://mock/hourly')
        assert 'properties' in hourly
        assert len(hourly['properties']['periods']) >= 1
        p = hourly['properties']['periods'][0]
        assert 'windSpeed' in p
        assert 'shortForecast' in p

    def test_gateway_returns_observation(self):
        gw = MockWeatherGateway()
        obs = gw.get_latest_observation('KJFK')
        assert 'properties' in obs
        assert 'temperature' in obs['properties']
        assert 'value' in obs['properties']['temperature']

    def test_mock_is_parseable_by_use_case(self):
        gw = MockWeatherGateway()
        use_case = FetchWeatherUseCase(gw)
        periods = use_case.execute(40.7, -73.9, periods_count=3)

        assert len(periods) == 3
        for p in periods:
            assert p.temperature is not None
            assert p.short_forecast is not None

    def test_alerts_default_to_empty(self):
        gw = MockWeatherGateway()
        alerts = gw.get_active_alerts(40.7, -73.9)
        assert alerts == {'features': []}

    def test_can_set_mock_alerts(self):
        gw = MockWeatherGateway()
        gw.set_alerts([
            {'properties': {'event': 'Storm Warning', 'headline': 'Storm', 'severity': 'Severe'}},
        ])
        result = gw.get_active_alerts(40.7, -73.9)
        assert len(result['features']) == 1
        assert result['features'][0]['properties']['event'] == 'Storm Warning'

    def test_alerts_flow_through_use_case(self):
        gw = MockWeatherGateway()
        gw.set_alerts([
            {'properties': {'event': 'Flood Watch', 'headline': 'Watch', 'severity': 'Moderate'}},
        ])
        use_case = FetchWeatherUseCase(gw)
        alerts = use_case.get_alerts(40.7, -73.9)
        assert len(alerts) == 1
        assert alerts[0]['properties']['event'] == 'Flood Watch'
