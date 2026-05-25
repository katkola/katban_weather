import requests
import sys
import os

# Add the project root to the path for config loader
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class WeatherGateway:
    BASE_URL = "https://api.weather.gov"

    def __init__(self, user_agent=None):
        self.session = requests.Session()
        if user_agent is None:
            # Try to get from config, fallback to default
            try:
                from utils.config_loader import ConfigLoader
                config = ConfigLoader()
                user_agent = config.get_user_agent()
            except ImportError:
                user_agent = 'KanBan_Weather_Display (your.email@example.com)'

        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'application/geo+json'
        })

    def get_points(self, latitude, longitude):
        """Get grid point information for the given coordinates"""
        url = f"{self.BASE_URL}/points/{latitude},{longitude}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_forecast(self, forecast_url):
        """Get forecast data from the forecast URL"""
        response = self.session.get(forecast_url)
        response.raise_for_status()
        return response.json()

    def get_hourly_forecast(self, hourly_url):
        """Get forecast data"""
        response = self.session.get(hourly_url)
        response.raise_for_status()
        return response.json()

    def get_alerts(self, alerts_url):
        """Get alerts data from a full URL"""
        response = self.session.get(alerts_url)
        response.raise_for_status()
        return response.json()

    def get_active_alerts(self, latitude, longitude):
        """Get active alerts for a lat/lon point"""
        from utils.config_loader import ConfigLoader
        config = ConfigLoader()
        if config.get_mock_alert():
            return {
                'features': [{
                    'properties': {
                        'event': 'Mock Heat Advisory',
                        'headline': 'Mock Heat Advisory in effect until 8 PM EDT',
                        'severity': 'Moderate'
                    }
                }]
            }
        url = f"{self.BASE_URL}/alerts/active?point={latitude},{longitude}"
        return self.get_alerts(url)

    def get_observation_stations(self, points_data):
        """Get list of observation stations from points data"""
        stations_url = points_data['properties']['observationStations']
        response = self.session.get(stations_url)
        response.raise_for_status()
        return response.json()

    def get_latest_observation(self, station_id):
        """Get the latest observation from a station"""
        url = f"{self.BASE_URL}/stations/{station_id}/observations/latest"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
