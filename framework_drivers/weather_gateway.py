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
        """Get hourly forecast data"""
        response = self.session.get(hourly_url)
        response.raise_for_status()
        return response.json()
    
    def get_alerts(self, alerts_url):
        """Get alerts data"""
        response = self.session.get(alerts_url)
        response.raise_for_status()
        return response.json()