from use_cases.fetch_weather import FetchWeatherUseCase


class WeatherController:
    def __init__(self, fetch_weather_use_case: FetchWeatherUseCase):
        self.fetch_weather_use_case = fetch_weather_use_case

    def get_weather(self, latitude, longitude, periods_count=3):
        """Get weather data for the specified coordinates"""
        return self.fetch_weather_use_case.execute(latitude, longitude, periods_count)
