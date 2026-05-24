#!/usr/bin/env python3
"""
Debug script to examine the actual data structure from weather.gov API
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_weather_data():
    """Debug the weather data structure to see what's available for humidity"""
    from framework_drivers.weather_gateway import WeatherGateway
    from use_cases.fetch_weather import FetchWeatherUseCase
    from interface_adapters.weather_controller import WeatherController
    from utils.config_loader import ConfigLoader
    
    # Initialize components
    config = ConfigLoader()
    weather_gateway = WeatherGateway()
    fetch_weather_use_case = FetchWeatherUseCase(weather_gateway)
    weather_controller = WeatherController(fetch_weather_use_case)
    
    # Get coordinates from config
    latitude = config.get_latitude()
    longitude = config.get_longitude()
    
    print(f"Fetching weather data for coordinates: {latitude}, {longitude}")
    
    try:
        # Get points data to determine grid coordinates
        points_data = weather_gateway.get_points(latitude, longitude)
        print("\n=== POINTS DATA ===")
        print(f"Points data keys: {list(points_data.keys())}")
        print(f"Properties keys: {list(points_data['properties'].keys())}")
        
        # Extract forecast URL from points data
        forecast_url = points_data['properties']['forecast']
        print(f"\nForecast URL: {forecast_url}")
        
        # Get forecast data
        forecast_data = weather_gateway.get_forecast(forecast_url)
        print("\n=== FORECAST DATA ===")
        print(f"Forecast data keys: {list(forecast_data.keys())}")
        print(f"Forecast properties keys: {list(forecast_data['properties'].keys())}")
        
        # Look at the periods
        periods = forecast_data['properties']['periods']
        print(f"\nNumber of periods: {len(periods)}")
        
        # Examine first few periods
        for i, period in enumerate(periods[:3]):
            print(f"\n--- Period {i} ---")
            print(f"Period keys: {list(period.keys())}")
            if 'relativeHumidity' in period:
                print(f"Relative humidity: {period['relativeHumidity']}")
                if isinstance(period['relativeHumidity'], dict):
                    print(f"Relative humidity value: {period['relativeHumidity'].get('value')}")
                    print(f"Relative humidity unit: {period['relativeHumidity'].get('unitCode')}")
            else:
                print("No relativeHumidity field in period")
                
            # Show some other fields for context
            print(f"Temperature: {period.get('temperature')} {period.get('temperatureUnit')}")
            print(f"Short forecast: {period.get('shortForecast')}")
            
        # Also check hourly forecast for more detailed current conditions
        hourly_url = points_data['properties']['forecastHourly']
        print(f"\n\n=== HOURLY FORECAST URL ===")
        print(f"Hourly URL: {hourly_url}")
        
        hourly_data = weather_gateway.get_hourly_forecast(hourly_url)
        print(f"Hourly data keys: {list(hourly_data.keys())}")
        print(f"Hourly properties keys: {list(hourly_data['properties'].keys())}")
        
        hourly_periods = hourly_data['properties']['periods']
        print(f"\nNumber of hourly periods: {len(hourly_periods)}")
        
        # Examine first few hourly periods
        for i, period in enumerate(hourly_periods[:3]):
            print(f"\n--- Hourly Period {i} ---")
            print(f"Period keys: {list(period.keys())}")
            if 'relativeHumidity' in period:
                print(f"Relative humidity: {period['relativeHumidity']}")
                if isinstance(period['relativeHumidity'], dict):
                    print(f"Relative humidity value: {period['relativeHumidity'].get('value')}")
                    print(f"Relative humidity unit: {period['relativeHumidity'].get('unitCode')}")
            else:
                print("No relativeHumidity field in hourly period")
                
            # Show some other fields for context
            print(f"Temperature: {period.get('temperature')} {period.get('temperatureUnit')}")
            print(f"Start time: {period.get('startTime')}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_weather_data()