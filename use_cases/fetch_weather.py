from entities.weather_data import WeatherData


def _c_to_f(celsius):
    if celsius is None:
        return None
    return round((celsius * 9 / 5) + 32)


class FetchWeatherUseCase:
    def __init__(self, weather_gateway):
        self.weather_gateway = weather_gateway

    def _now_from_observation(self, points_data, hourly_data):
        """Build NOW WeatherData from observation (temp/humidity) + hourly forecast (wind/conditions)."""
        obs_temp = None
        obs_humidity = None
        obs_ts = None

        try:
            stations = self.weather_gateway.get_observation_stations(
                points_data)
            features = stations.get('features', [])
            if features:
                sid = features[0]['properties']['stationIdentifier']
                obs = self.weather_gateway.get_latest_observation(sid)
                p = obs.get('properties', {})
                obs_temp = p.get('temperature', {}).get('value')
                obs_humidity = p.get('relativeHumidity', {}).get('value')
                obs_ts = p.get('timestamp')
        except Exception:
            pass

        # Always get wind/conditions from the hourly forecast (matches weather.gov display)
        if hourly_data['properties']['periods']:
            hp = hourly_data['properties']['periods'][0]
            temperature = _c_to_f(
                obs_temp) if obs_temp is not None else hp['temperature']
            temperature_unit = 'F' if obs_temp is not None else hp['temperatureUnit']
            relative_humidity = round(obs_humidity) if obs_humidity is not None else hp.get(
                'relativeHumidity', {}).get('value')
            timestamp = obs_ts if obs_ts is not None else hp['startTime']

            return WeatherData(
                temperature=temperature,
                temperature_unit=temperature_unit,
                wind_speed=hp['windSpeed'],
                wind_direction=hp['windDirection'],
                short_forecast=hp['shortForecast'],
                detailed_forecast=hp['detailedForecast'],
                relative_humidity=relative_humidity,
                timestamp=timestamp,
                period_name='NOW'
            )
        return None

    def execute(self, latitude, longitude, periods_count=3):
        points_data = self.weather_gateway.get_points(latitude, longitude)

        forecast_url = points_data['properties']['forecast']
        forecast_data = self.weather_gateway.get_forecast(forecast_url)

        hourly_url = points_data['properties']['forecastHourly']
        hourly_data = self.weather_gateway.get_hourly_forecast(hourly_url)

        weather_data_list = []

        # ---- NOW: observation temp/humidity + hourly forecast wind/conditions ----
        now_data = self._now_from_observation(points_data, hourly_data)

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
