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

    # Optional calendar controller (Google packages may not be installed)
    calendar_controller = None
    try:
        from framework_drivers.calendar_gateway import CalendarGateway
        from use_cases.fetch_calendar import FetchCalendarUseCase
        from interface_adapters.calendar_controller import CalendarController
        calendar_gateway = CalendarGateway()
        fetch_calendar_use_case = FetchCalendarUseCase(calendar_gateway)
        calendar_controller = CalendarController(fetch_calendar_use_case)
    except ImportError:
        pass

    from framework_drivers.gui_display import WeatherAndCalendarDisplay

    # Create and run the display
    app = WeatherAndCalendarDisplay(weather_controller, calendar_controller)
    app.run()


if __name__ == "__main__":
    main()
