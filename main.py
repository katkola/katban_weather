#!/usr/bin/env python3
"""
Main entry point for the weather display application.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main application entry point"""
    print("Starting KanBan Weather Display...")

    # Import components
    from framework_drivers.weather_gateway import WeatherGateway
    from use_cases.fetch_weather import FetchWeatherUseCase
    from interface_adapters.weather_controller import WeatherController

    # Initialize dependencies (dependency injection)
    try:
        from utils.config_loader import ConfigLoader
        config = ConfigLoader()
        user_agent = config.get_user_agent()
    except ImportError:
        user_agent = None

    weather_gateway = WeatherGateway(user_agent)
    fetch_weather_use_case = FetchWeatherUseCase(weather_gateway)
    weather_controller = WeatherController(fetch_weather_use_case)

    # Calendar controller (falls back to mock data if unavailable)
    from use_cases.fetch_calendar import FetchCalendarUseCase
    from interface_adapters.calendar_controller import CalendarController
    calendar_config = config.load_config().get('calendar', {})
    ics_url = calendar_config.get('ics_url', '')
    if ics_url:
        from framework_drivers.ics_calendar_gateway import IcsCalendarGateway
        calendar_gateway = IcsCalendarGateway(ics_url)
    else:
        try:
            from framework_drivers.calendar_gateway import CalendarGateway
            calendar_gateway = CalendarGateway()
        except (ImportError, FileNotFoundError):
            print("Calendar credentials not found, using mock data.")
            from mock_data.calendar_mock_data import MockCalendarGateway
            calendar_gateway = MockCalendarGateway()
    fetch_calendar_use_case = FetchCalendarUseCase(calendar_gateway)
    calendar_controller = CalendarController(fetch_calendar_use_case)

    from framework_drivers.gui_display import WeatherAndCalendarDisplay

    # Create and run the display
    app = WeatherAndCalendarDisplay(weather_controller, calendar_controller)
    app.run()


if __name__ == "__main__":
    main()
