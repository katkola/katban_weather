class MockWeatherGateway:
    def __init__(self):
        self.stations_data = {
            'features': [
                {'properties': {'stationIdentifier': 'KJFK'}}
            ]
        }
        self.observation_data = {
            'properties': {
                'temperature': {'value': 22.2},
                'relativeHumidity': {'value': 58},
                'timestamp': '2025-05-24T14:00:00+00:00',
            }
        }

    def set_observation(self, temp_c=None, humidity=None):
        if temp_c is not None:
            self.observation_data['properties']['temperature']['value'] = temp_c
        if humidity is not None:
            self.observation_data['properties']['relativeHumidity']['value'] = humidity
        return self

    def get_points(self, latitude, longitude):
        return {
            'properties': {
                'forecast': 'https://mock/forecast',
                'forecastHourly': 'https://mock/hourly',
                'forecastGridData': 'https://mock/grid',
                'observationStations': 'https://mock/stations',
            }
        }

    def get_forecast(self, forecast_url):
        return {
            'properties': {
                'periods': [
                    {
                        'number': 1,
                        'name': 'Today',
                        'startTime': '2025-05-24T06:00:00-05:00',
                        'endTime': '2025-05-24T18:00:00-05:00',
                        'temperature': 72,
                        'temperatureUnit': 'F',
                        'windSpeed': '5 mph',
                        'windDirection': 'NE',
                        'shortForecast': 'Partly Cloudy',
                        'detailedForecast': 'Partly cloudy throughout the day.',
                    },
                    {
                        'number': 2,
                        'name': 'Tonight',
                        'startTime': '2025-05-24T18:00:00-05:00',
                        'endTime': '2025-05-25T06:00:00-05:00',
                        'temperature': 55,
                        'temperatureUnit': 'F',
                        'windSpeed': '10 mph',
                        'windDirection': 'N',
                        'shortForecast': 'Clear',
                        'detailedForecast': 'Clear overnight.',
                    },
                    {
                        'number': 3,
                        'name': 'Tuesday',
                        'startTime': '2025-05-25T06:00:00-05:00',
                        'endTime': '2025-05-25T18:00:00-05:00',
                        'temperature': 68,
                        'temperatureUnit': 'F',
                        'windSpeed': '8 mph',
                        'windDirection': 'SW',
                        'shortForecast': 'Sunny',
                        'detailedForecast': 'Sunny with high clouds.',
                    },
                ]
            }
        }

    def get_hourly_forecast(self, hourly_url):
        return {
            'properties': {
                'periods': [
                    {
                        'number': 1,
                        'startTime': '2025-05-24T14:00:00-05:00',
                        'endTime': '2025-05-24T15:00:00-05:00',
                        'temperature': 72,
                        'temperatureUnit': 'F',
                        'windSpeed': '5 mph',
                        'windDirection': 'NE',
                        'shortForecast': 'Partly Cloudy',
                        'detailedForecast': 'Partly cloudy.',
                        'relativeHumidity': {'value': 60},
                    },
                    {
                        'number': 2,
                        'startTime': '2025-05-24T15:00:00-05:00',
                        'endTime': '2025-05-24T16:00:00-05:00',
                        'temperature': 71,
                        'temperatureUnit': 'F',
                        'windSpeed': '6 mph',
                        'windDirection': 'NE',
                        'shortForecast': 'Partly Cloudy',
                        'detailedForecast': 'Partly cloudy.',
                        'relativeHumidity': {'value': 62},
                    },
                ]
            }
        }

    def get_alerts(self, alerts_url):
        return {'features': []}

    def get_observation_stations(self, points_data):
        return self.stations_data

    def get_latest_observation(self, station_id):
        return self.observation_data
