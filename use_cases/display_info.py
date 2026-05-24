from typing import List, Optional
from entities.weather_data import WeatherData
from entities.calendar_event import CalendarEvent
from interface_adapters.weather_controller import WeatherController
from interface_adapters.calendar_controller import CalendarController


class DisplayInfo:
    def __init__(self, weather_periods: List[WeatherData],
                 calendar_events: List[CalendarEvent]):
        self.weather_periods = weather_periods
        self.calendar_events = calendar_events


class FetchDisplayInfoUseCase:
    def __init__(self, weather_controller: WeatherController,
                 calendar_controller: CalendarController):
        self.weather_controller = weather_controller
        self.calendar_controller = calendar_controller

    def execute(self, latitude: float, longitude: float,
                weather_periods: int = 3,
                calendar_max: int = 10) -> DisplayInfo:
        weather = self.weather_controller.get_weather(
            latitude, longitude, weather_periods)
        calendar = self.calendar_controller.get_today_events(calendar_max)
        return DisplayInfo(weather_periods=weather, calendar_events=calendar)
