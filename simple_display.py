#!/usr/bin/env python3
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("Starting KanBan Weather Display (Console Version)...")
    sys.stdout.flush()

    from utils.config_loader import ConfigLoader
    from framework_drivers.weather_gateway import WeatherGateway
    from use_cases.fetch_weather import FetchWeatherUseCase
    from interface_adapters.weather_controller import WeatherController
    from use_cases.fetch_calendar import FetchCalendarUseCase
    from interface_adapters.calendar_controller import CalendarController
    from use_cases.display_info import FetchDisplayInfoUseCase
    from interface_adapters.view_presenter import ViewPresenter

    config = ConfigLoader()
    latitude = config.get_latitude()
    longitude = config.get_longitude()

    weather_gateway = WeatherGateway()
    fetch_weather_use_case = FetchWeatherUseCase(weather_gateway)
    weather_controller = WeatherController(fetch_weather_use_case)

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
    display_use_case = FetchDisplayInfoUseCase(weather_controller, calendar_controller)
    presenter = ViewPresenter()

    update_interval = 5

    try:
        while True:
            try:
                print("\033[2J\033[H", end="")

                info = display_use_case.execute(latitude, longitude)
                weather_vm = presenter.present_weather(info)
                calendar_vm = presenter.present_calendar(info)

                print("=" * 50)
                print("KanBan Weather Display")
                print("=" * 50)
                print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print()

                cw = weather_vm['current']
                print(f"{cw['condition']}")
                print(cw['art'])
                print()
                print(f"  {cw['temp_text']}")
                print(f"  {cw['humidity']}")
                print(f"  {cw['wind']}")
                print()

                for p in weather_vm['hourly']:
                    print(f"  {p['name']}: {p['temp']}  {p['condition']}")

                alerts = weather_vm.get('alerts', [])
                if alerts:
                    print()
                    print("⚠  ALERTS")
                    print("-" * 50)
                    for a in alerts:
                        print(f"  {a['event']}: {a['headline']}")
                    print()

                print()
                print("=" * 50)
                print("Today's Schedule")
                print("=" * 50)
                print()

                for section in calendar_vm['sections']:
                    print(f"  [{section['title']}]")
                    for item in section['items']:
                        src = item.get('source')
                        src_str = f"  [{src}]" if src else ""
                        loc = item.get('location')
                        loc_str = f"  📍 {loc}" if loc else ""
                        print(f"    {item['time']:>10}  {item['title']}{src_str}{loc_str}")
                    print()

                print("Press Ctrl+C to exit")
                print("=" * 50)
                sys.stdout.flush()

                time.sleep(update_interval)

            except Exception as e:
                print(f"Error fetching data: {e}")
                print("Retrying in 30 seconds...")
                sys.stdout.flush()
                time.sleep(30)

    except KeyboardInterrupt:
        print("\nShutting down weather display...")
        return 0


if __name__ == "__main__":
    sys.exit(main())
