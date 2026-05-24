#!/usr/bin/env python3
"""
Test script to verify configuration loading
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config():
    print("Testing configuration loader...")
    
    try:
        from utils.config_loader import ConfigLoader
        config = ConfigLoader()
        
        print(f"Latitude: {config.get_latitude()}")
        print(f"Longitude: {config.get_longitude()}")
        print(f"City: {config.get_city_name()}")
        print(f"Update interval: {config.get_update_interval()} seconds")
        print(f"Use GUI: {config.get_use_gui()}")
        print(f"User agent: {config.get_user_agent()}")
        
        print("Configuration test successful!")
        return True
    except Exception as e:
        print(f"Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)