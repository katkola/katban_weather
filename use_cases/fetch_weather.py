from entities.weather_data import WeatherData

class FetchWeatherUseCase:
    def __init__(self, weather_gateway):
        self.weather_gateway = weather_gateway
    
    def execute(self, latitude, longitude, periods_count=3):
        # Get points data to determine grid coordinates
        points_data = self.weather_gateway.get_points(latitude, longitude)
         
        # Extract forecast URL from points data
        forecast_url = points_data['properties']['forecast']
         
        # Get forecast data (day/night summary periods)
        forecast_data = self.weather_gateway.get_forecast(forecast_url)
         
        # Get hourly forecast for accurate current conditions
        hourly_url = points_data['properties']['forecastHourly']
        hourly_data = self.weather_gateway.get_hourly_forecast(hourly_url)
         
        weather_data_list = []
        
        # Period 0: "NOW" — use the first hourly period for accurate current conditions
        if hourly_data['properties']['periods']:
            hourly_period = hourly_data['properties']['periods'][0]
            now_data = WeatherData(
                temperature=hourly_period['temperature'],
                temperature_unit=hourly_period['temperatureUnit'],
                wind_speed=hourly_period['windSpeed'],
                wind_direction=hourly_period['windDirection'],
                short_forecast=hourly_period['shortForecast'],
                detailed_forecast=hourly_period['detailedForecast'],
                relative_humidity=hourly_period.get('relativeHumidity', {}).get('value'),
                timestamp=hourly_period['startTime'],
                period_name='NOW'
            )
            weather_data_list.append(now_data)
        
        # Periods 1 and 2: "TONIGHT", "TOMORROW" — use forecast summary periods
        forecast_periods = forecast_data['properties']['periods'][1:periods_count]
        for period in forecast_periods:
            # Forecast periods don't include relativeHumidity, so use current hourly value
            relative_humidity = None
            if hourly_data['properties']['periods']:
                relative_humidity = hourly_data['properties']['periods'][0].get('relativeHumidity', {}).get('value')
            
            weather_data = WeatherData(
                temperature=period['temperature'],
                temperature_unit=period['temperatureUnit'],
                wind_speed=period['windSpeed'],
                wind_direction=period['windDirection'],
                short_forecast=period['shortForecast'],
                detailed_forecast=period['detailedForecast'],
                relative_humidity=relative_humidity,
                timestamp=period['startTime'],
                period_name=period['name'].upper() if 'name' in period else None
            )
            weather_data_list.append(weather_data)
         
        return weather_data_list