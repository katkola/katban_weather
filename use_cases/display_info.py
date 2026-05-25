from typing import List, Optional, Any, Dict, Protocol
from entities.weather_data import WeatherData
from entities.calendar_event import CalendarEvent


class WeatherControllerProtocol(Protocol):
    def get_weather(self, latitude: float, longitude: float, periods_count: int = 3) -> List[WeatherData]: ...
    def get_alerts(self, latitude: float, longitude: float) -> List[Dict[str, Any]]: ...


class CalendarControllerProtocol(Protocol):
    def get_today_events(self, max_results: int = 10) -> List[CalendarEvent]: ...


class DisplayInfo:
    def __init__(self, weather_periods: List[WeatherData],
                 calendar_events: List[CalendarEvent],
                 alerts: Optional[List[Dict[str, Any]]] = None):
        self.weather_periods = weather_periods
        self.calendar_events = calendar_events
        self.alerts = alerts or []


class FetchDisplayInfoUseCase:
    def __init__(self, weather_controller: WeatherControllerProtocol,
                 calendar_controller: CalendarControllerProtocol):
        self.weather_controller = weather_controller
        self.calendar_controller = calendar_controller

    def execute(self, latitude: float, longitude: float,
                weather_periods: int = 3,
                calendar_max: int = 10) -> DisplayInfo:
        weather = self.weather_controller.get_weather(
            latitude, longitude, weather_periods)
        calendar = self.calendar_controller.get_today_events(calendar_max)
        alerts = self.weather_controller.get_alerts(latitude, longitude)
        return DisplayInfo(weather_periods=weather,
                           calendar_events=calendar,
                           alerts=alerts)
