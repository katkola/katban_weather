import sys
import os

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_weather_data_creation():
    """Test that we can create a WeatherData object"""
    from entities.weather_data import WeatherData

    weather = WeatherData(
        temperature=72,
        temperature_unit="F",
        wind_speed="5 mph",
        wind_direction="NE",
        short_forecast="Partly Cloudy",
        detailed_forecast="Partly cloudy with a chance of rain",
        relative_humidity=65,
        timestamp="2023-01-01T12:00:00Z"
    )

    assert weather.temperature == 72
    assert weather.temperature_unit == "F"
    assert weather.wind_speed == "5 mph"
    assert weather.wind_direction == "NE"
    assert weather.short_forecast == "Partly Cloudy"
    assert weather.detailed_forecast == "Partly cloudy with a chance of rain"
    assert weather.relative_humidity == 65
    assert weather.timestamp == "2023-01-01T12:00:00Z"

    print("✓ WeatherData creation test passed")


def test_weather_data_to_dict():
    """Test that WeatherData.to_dict() works correctly"""
    from entities.weather_data import WeatherData

    weather = WeatherData(
        temperature=72,
        temperature_unit="F",
        wind_speed="5 mph",
        wind_direction="NE",
        short_forecast="Partly Cloudy",
        detailed_forecast="Partly cloudy with a chance of rain",
        relative_humidity=65,
        timestamp="2023-01-01T12:00:00Z"
    )

    result = weather.to_dict()

    expected = {
        "temperature": 72,
        "temperature_unit": "F",
        "wind_speed": "5 mph",
        "wind_direction": "NE",
        "short_forecast": "Partly Cloudy",
        "detailed_forecast": "Partly cloudy with a chance of rain",
        "relative_humidity": 65,
        "timestamp": "2023-01-01T12:00:00Z",
        "period_name": None
    }

    assert result == expected
    print("✓ WeatherData.to_dict() test passed")


if __name__ == "__main__":
    test_weather_data_creation()
    test_weather_data_to_dict()
    print("All tests passed!")
