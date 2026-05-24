class WeatherData:
    def __init__(self, temperature, temperature_unit, wind_speed, wind_direction, 
                 short_forecast, detailed_forecast, relative_humidity, 
                 timestamp=None, period_name=None):
        self.temperature = temperature
        self.temperature_unit = temperature_unit
        self.wind_speed = wind_speed
        self.wind_direction = wind_direction
        self.short_forecast = short_forecast
        self.detailed_forecast = detailed_forecast
        self.relative_humidity = relative_humidity
        self.timestamp = timestamp
        self.period_name = period_name

    def to_dict(self):
        return {
            "temperature": self.temperature,
            "temperature_unit": self.temperature_unit,
            "wind_speed": self.wind_speed,
            "wind_direction": self.wind_direction,
            "short_forecast": self.short_forecast,
            "detailed_forecast": self.detailed_forecast,
            "relative_humidity": self.relative_humidity,
            "timestamp": self.timestamp,
            "period_name": self.period_name
        }