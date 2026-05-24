from entities.weather_data import WeatherData

def _c_to_f(celsius):
    if celsius is None:
        return None
    return round((celsius * 9 / 5) + 32)

def _kmh_to_mph(kmh):
    if kmh is None:
        return None
    return round(kmh * 0.621371)

def _degrees_to_cardinal(degrees):
    if degrees is None:
        return None
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    index = round(degrees / 22.5) % 16
    return dirs[index]

def _observation_weather_data(observation):
    """Build a WeatherData from a live station observation"""
    props = observation.get('properties', {})

    temp_c = props.get('temperature', {}).get('value')
    rel_hum = props.get('relativeHumidity', {}).get('value')
    wind_kmh = props.get('windSpeed', {}).get('value')
    wind_deg = props.get('windDirection', {}).get('value')
    timestamp = props.get('timestamp')

    short = props.get('textDescription') or 'Unknown'
    detailed = None  # observations don't carry a detailed forecast

    wind_speed_str = f"{_kmh_to_mph(wind_kmh)} mph" if wind_kmh is not None else None

    return WeatherData(
        temperature=_c_to_f(temp_c),
        temperature_unit='F',
        wind_speed=wind_speed_str,
        wind_direction=_degrees_to_cardinal(wind_deg),
        short_forecast=short,
        detailed_forecast=detailed,
        relative_humidity=round(rel_hum) if rel_hum is not None else None,
        timestamp=timestamp,
        period_name='NOW'
    )

class FetchWeatherUseCase:
    def __init__(self, weather_gateway):
        self.weather_gateway = weather_gateway

    def execute(self, latitude, longitude, periods_count=3):
        points_data = self.weather_gateway.get_points(latitude, longitude)

        forecast_url = points_data['properties']['forecast']
        forecast_data = self.weather_gateway.get_forecast(forecast_url)

        hourly_url = points_data['properties']['forecastHourly']
        hourly_data = self.weather_gateway.get_hourly_forecast(hourly_url)

        weather_data_list = []

        # ---- NOW: live observation ----
        now_data = None
        try:
            stations_data = self.weather_gateway.get_observation_stations(points_data)
            features = stations_data.get('features', [])
            if features:
                station_id = features[0]['properties']['stationIdentifier']
                observation = self.weather_gateway.get_latest_observation(station_id)
                now_data = _observation_weather_data(observation)
        except Exception:
            now_data = None

        # Fall back to hourly forecast first period if observation fails
        if now_data is None and hourly_data['properties']['periods']:
            p = hourly_data['properties']['periods'][0]
            now_data = WeatherData(
                temperature=p['temperature'],
                temperature_unit=p['temperatureUnit'],
                wind_speed=p['windSpeed'],
                wind_direction=p['windDirection'],
                short_forecast=p['shortForecast'],
                detailed_forecast=p['detailedForecast'],
                relative_humidity=p.get('relativeHumidity', {}).get('value'),
                timestamp=p['startTime'],
                period_name='NOW'
            )

        if now_data is not None:
            weather_data_list.append(now_data)

        # ---- TONIGHT / TOMORROW: forecast summary periods ----
        forecast_periods = forecast_data['properties']['periods'][1:periods_count]
        for period in forecast_periods:
            relative_humidity = now_data.relative_humidity if now_data is not None else None

            weather_data = WeatherData(
                temperature=period['temperature'],
                temperature_unit=period['temperatureUnit'],
                wind_speed=period['windSpeed'],
                wind_direction=period['windDirection'],
                short_forecast=period['shortForecast'],
                detailed_forecast=period['detailedForecast'],
                relative_humidity=relative_humidity,
                timestamp=period['startTime'],
                period_name=period.get('name', '').upper() or None
            )
            weather_data_list.append(weather_data)

        return weather_data_list