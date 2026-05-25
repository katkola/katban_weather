import json
import os
from typing import Dict, Any, Optional


class ConfigLoader:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance

    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        if self._config is not None:
            return self._config

        if config_path is None:
            # Default to config.json in project root
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'config.json'
            )

        try:
            with open(config_path, 'r') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            # Return default configuration if file not found
            self._config = self._get_default_config()
        except json.JSONDecodeError as e:
            # Return default configuration if JSON is invalid
            print(f"Warning: Invalid JSON in config file: {e}")
            self._config = self._get_default_config()

        return self._config

    def get_location_config(self) -> Dict[str, Any]:
        """Get location configuration"""
        config = self.load_config()
        return config.get('location', self._get_default_config()['location'])

    def get_display_config(self) -> Dict[str, Any]:
        """Get display configuration"""
        config = self.load_config()
        return config.get('display', self._get_default_config()['display'])

    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration"""
        config = self.load_config()
        return config.get('api', self._get_default_config()['api'])

    def get_latitude(self) -> float:
        """Get latitude from config"""
        return self.get_location_config().get('latitude', 37.7749)

    def get_longitude(self) -> float:
        """Get longitude from config"""
        return self.get_location_config().get('longitude', -122.4194)

    def get_city_name(self) -> str:
        """Get city name from config"""
        return self.get_location_config().get('city_name', 'San Francisco')

    def get_update_interval(self) -> int:
        """Get update interval in seconds"""
        return self.get_display_config().get('update_interval_seconds', 30)

    def get_use_gui(self) -> bool:
        """Get whether to use GUI display"""
        return self.get_display_config().get('use_gui', False)

    def get_user_agent(self) -> str:
        """Get user agent string"""
        return self.get_api_config().get('user_agent', 'KanBan_Weather_Display (your.email@example.com)')

    def get_development_config(self) -> Dict[str, Any]:
        """Get development configuration"""
        config = self.load_config()
        return config.get('development', self._get_default_config()['development'])

    def get_mock_alert(self) -> bool:
        """Get whether to use mock alert data instead of real NWS alerts"""
        return self.get_development_config().get('mock_alert', False)

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "location": {
                "latitude": 37.7749,
                "longitude": -122.4194,
                "city_name": "San Francisco"
            },
            "display": {
                "update_interval_seconds": 30,
                "use_gui": False
            },
            "api": {
                "user_agent": "KanBan_Weather_Display (your.email@example.com)"
            },
            "development": {
                "mock_alert": False
            }
        }
