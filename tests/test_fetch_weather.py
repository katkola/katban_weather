import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from entities.weather_data import WeatherData
from mock_data.weather_mock_data import MockWeatherGateway
from use_cases.fetch_weather import FetchWeatherUseCase


class TestFetchWeatherUseCase:
    def test_returns_weather_periods(self):
        gateway = MockWeatherGateway()
        use_case = FetchWeatherUseCase(gateway)
        periods = use_case.execute(40.7, -73.9, periods_count=3)

        assert len(periods) == 3
        assert all(isinstance(p, WeatherData) for p in periods)

    def test_now_period_uses_observation_temperature(self):
        gateway = MockWeatherGateway()
        gateway.set_observation(temp_c=25.0)
        use_case = FetchWeatherUseCase(gateway)
        periods = use_case.execute(40.7, -73.9)
        now = periods[0]

        assert now.temperature == 77
        assert now.period_name == 'NOW'

    def test_now_period_uses_hourly_wind_and_conditions(self):
        gateway = MockWeatherGateway()
        use_case = FetchWeatherUseCase(gateway)
        periods = use_case.execute(40.7, -73.9)
        now = periods[0]

        assert now.wind_speed == '5 mph'
        assert now.wind_direction == 'NE'
        assert now.short_forecast == 'Partly Cloudy'

    def test_now_period_uses_observation_humidity(self):
        gateway = MockWeatherGateway()
        gateway.set_observation(humidity=70)
        use_case = FetchWeatherUseCase(gateway)
        periods = use_case.execute(40.7, -73.9)
        now = periods[0]

        assert now.relative_humidity == 70

    def test_forecast_periods_have_names(self):
        gateway = MockWeatherGateway()
        use_case = FetchWeatherUseCase(gateway)
        periods = use_case.execute(40.7, -73.9, periods_count=3)
        names = [p.period_name for p in periods]
        assert 'TONIGHT' in names
        assert 'TUESDAY' in names

    def test_missing_observation_falls_back_to_hourly(self):
        gateway = MockWeatherGateway()
        gateway.stations_data = {'features': []}
        use_case = FetchWeatherUseCase(gateway)
        periods = use_case.execute(40.7, -73.9)

        assert len(periods) == 3
        now = periods[0]
        assert now.temperature == 72
        assert now.temperature_unit == 'F'

    def test_fewer_periods_when_requested(self):
        gateway = MockWeatherGateway()
        use_case = FetchWeatherUseCase(gateway)
        periods = use_case.execute(40.7, -73.9, periods_count=2)
        assert len(periods) == 2
