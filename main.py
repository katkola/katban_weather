#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("Starting KanBan Weather Display...")

    from utils.config_loader import ConfigLoader

    config = ConfigLoader()
    user_agent = config.get_user_agent()

    from framework_drivers.weather_gateway import WeatherGateway
    from use_cases.fetch_weather import FetchWeatherUseCase
    from interface_adapters.weather_controller import WeatherController

    weather_gateway = WeatherGateway(user_agent)
    fetch_weather_use_case = FetchWeatherUseCase(weather_gateway)
    weather_controller = WeatherController(fetch_weather_use_case)

    from use_cases.fetch_calendar import FetchCalendarUseCase
    from interface_adapters.calendar_controller import CalendarController
    from framework_drivers.ics_calendar_gateway import IcsCalendarGateway

    calendar_config = config.load_config().get('calendar', {})
    ics_urls = calendar_config.get('ics_urls', [])

    if ics_urls:
        calendar_gateway = IcsCalendarGateway(ics_urls)
    else:
        print("Calendar ICS URL not configured, using mock data.")
        from mock_data.calendar_mock_data import MockCalendarGateway
        calendar_gateway = MockCalendarGateway()

    fetch_calendar_use_case = FetchCalendarUseCase(calendar_gateway)
    calendar_controller = CalendarController(fetch_calendar_use_case)

    from framework_drivers.gui_display import WeatherAndCalendarDisplay

    app = WeatherAndCalendarDisplay(weather_controller, calendar_controller)
    app.run()


if __name__ == "__main__":
    main()
