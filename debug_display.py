#!/usr/bin/env python3
"""
Debug script to test the display with explicit flushing
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Debug application entry point"""
    print("Debug: Starting KanBan Weather Display...")
    sys.stdout.flush()
    
    try:
        # Import components
        print("Debug: Importing components...")
        sys.stdout.flush()
        from framework_drivers.weather_gateway import WeatherGateway
        from use_cases.fetch_weather import FetchWeatherUseCase
        from interface_adapters.weather_controller import WeatherController
        from utils.config_loader import ConfigLoader
        print("Debug: Components imported successfully")
        sys.stdout.flush()
        
        # Initialize configuration
        print("Debug: Initializing configuration...")
        sys.stdout.flush()
        config = ConfigLoader()
        print(f"Debug: Config loaded - Lat: {config.get_latitude()}, Lon: {config.get_longitude()}")
        sys.stdout.flush()
        
        # Initialize dependencies (dependency injection)
        print("Debug: Initializing weather gateway...")
        sys.stdout.flush()
        weather_gateway = WeatherGateway()
        print("Debug: Weather gateway initialized")
        sys.stdout.flush()
        
        print("Debug: Initializing use case...")
        sys.stdout.flush()
        fetch_weather_use_case = FetchWeatherUseCase(weather_gateway)
        print("Debug: Use case initialized")
        sys.stdout.flush()
        
        print("Debug: Initializing controller...")
        sys.stdout.flush()
        weather_controller = WeatherController(fetch_weather_use_case)
        print("Debug: Controller initialized")
        sys.stdout.flush()
        
        # Get coordinates from config
        latitude = config.get_latitude()
        longitude = config.get_longitude()
        print(f"Debug: Coordinates from config - Lat: {latitude}, Lon: {longitude}")
        sys.stdout.flush()
        
        # Test getting weather data
        print("Debug: Fetching weather data...")
        sys.stdout.flush()
        weather_data = weather_controller.get_weather(latitude, longitude)
        print(f"Debug: Weather data received - Temp: {weather_data.temperature}°{weather_data.temperature_unit}")
        sys.stdout.flush()
        
        print("Debug: Test completed successfully!")
        sys.stdout.flush()
        return 0
        
    except Exception as e:
        print(f"Debug: Error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        return 1

if __name__ == "__main__":
    sys.exit(main())