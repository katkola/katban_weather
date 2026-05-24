#!/usr/bin/env python3
"""
Simple console-based display for testing weather functionality
"""

import sys
import os
import time
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main application entry point for console display"""
    print("Starting KanBan Weather Display (Console Version)...")
    import sys
    sys.stdout.flush()

    # Import components
    from framework_drivers.weather_gateway import WeatherGateway
    from use_cases.fetch_weather import FetchWeatherUseCase
    from interface_adapters.weather_controller import WeatherController
    from utils.config_loader import ConfigLoader

    # Initialize configuration
    config = ConfigLoader()

    # Initialize dependencies (dependency injection)
    weather_gateway = WeatherGateway()
    fetch_weather_use_case = FetchWeatherUseCase(weather_gateway)
    weather_controller = WeatherController(fetch_weather_use_case)

    # Get coordinates from config
    latitude = config.get_latitude()
    longitude = config.get_longitude()

    # Override update interval for faster testing (5 seconds instead of 30)
    update_interval = 5  # seconds

    try:
        while True:
            try:
                # Clear screen (works on most terminals)
                print("\033[2J\033[H", end="")

                print("=" * 50)
                print("KanBan Weather Display")
                print("=" * 50)
                print(
                    f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print()

                # Get weather data for multiple periods (now, tonight, tomorrow)
                weather_data_list = weather_controller.get_weather(
                    latitude, longitude, periods_count=3)

                # Display weather information for each period
                for i, weather_data in enumerate(weather_data_list):
                    if i > 0:
                        print()  # Add spacing between periods

                    # Use the period name from the API
                    period_name = weather_data.period_name or f'PERIOD {i+1}'
                    print(f"{period_name}:")
                    print(
                        f"  Temperature: {weather_data.temperature}°{weather_data.temperature_unit}")
                    print(f"  Conditions: {weather_data.short_forecast}")
                    print(f"  Humidity: {weather_data.relative_humidity}%")
                    print(
                        f"  Wind: {weather_data.wind_speed} {weather_data.wind_direction}")
                    if weather_data.detailed_forecast:
                        print(f"  Forecast: {weather_data.detailed_forecast}")

                print()
                print("Press Ctrl+C to exit")
                print("=" * 50)
                sys.stdout.flush()

                # Wait for configured interval before next update
                time.sleep(update_interval)

            except Exception as e:
                print(f"Error fetching weather data: {e}")
                print("Retrying in 30 seconds...")
                sys.stdout.flush()
                time.sleep(30)

    except KeyboardInterrupt:
        print("\nShutting down weather display...")
        return 0


if __name__ == "__main__":
    sys.exit(main())
