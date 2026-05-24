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
    from framework_drivers.gui_display import WeatherAndCalendarDisplay as WeatherDisplay
    
    # Initialize dependencies (dependency injection)
    try:
        from utils.config_loader import ConfigLoader
        config = ConfigLoader()
        weather_gateway = WeatherGateway(config.get_user_agent())
    except ImportError:
        # Fallback if config loader is not available
        weather_gateway = WeatherGateway()
    
    fetch_weather_use_case = FetchWeatherUseCase(weather_gateway)
    weather_controller = WeatherController(fetch_weather_use_case)
    
    # Create and run the display
    app = WeatherDisplay(weather_controller)
    app.run()

if __name__ == "__main__":
    main()