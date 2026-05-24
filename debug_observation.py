#!/usr/bin/env python3
"""Quick script to inspect observation data structure from weather.gov"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from framework_drivers.weather_gateway import WeatherGateway
from utils.config_loader import ConfigLoader

config = ConfigLoader()
gw = WeatherGateway(config.get_user_agent())

lat, lon = config.get_latitude(), config.get_longitude()
points = gw.get_points(lat, lon)

obs_stations_url = points['properties']['observationStations']
print(f"Observation stations URL: {obs_stations_url}")

stations_data = gw.session.get(obs_stations_url).json()
features = stations_data['features']
print(f"Number of stations: {len(features)}")

# Get first station ID
first_station = features[0]['properties']['stationIdentifier']
print(f"First station: {first_station}")

# Get latest observation
obs_url = f"https://api.weather.gov/stations/{first_station}/observations/latest"
obs_data = gw.session.get(obs_url).json()
props = obs_data['properties']
print(f"\nObservation keys: {list(props.keys())}")
print(f"Timestamp: {props.get('timestamp')}")
print(f"Text description: {props.get('textDescription')}")

temp = props.get('temperature', {})
print(f"\nTemperature: {temp.get('value')} {temp.get('unitCode')}")

humidity = props.get('relativeHumidity', {})
print(f"Humidity: {humidity.get('value')} {humidity.get('unitCode')}")

wind_speed = props.get('windSpeed', {})
print(f"Wind speed: {wind_speed.get('value')} {wind_speed.get('unitCode')}")

wind_dir = props.get('windDirection', {})
print(f"Wind direction: {wind_dir.get('value')} {wind_dir.get('unitCode')}")

dewpoint = props.get('dewpoint', {})
print(f"Dewpoint: {dewpoint.get('value')} {dewpoint.get('unitCode')}")

# Check if there's a short forecast-like field
print(f"\nAll props with values:")
for k, v in props.items():
    if isinstance(v, dict) and 'value' in v:
        print(f"  {k}: {v}")
