import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import time
from datetime import datetime
import sys
import os

# Add the project root to the path for config loader
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class WeatherAndCalendarDisplay:
    def __init__(self, weather_controller, calendar_controller):
        self.weather_controller = weather_controller
        self.calendar_controller = calendar_controller
        self.root = tk.Tk()
        self.root.title("KanBan Weather & Calendar Display")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg='black')

        # Configure grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Main frame
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Configure main frame grid
        self.main_frame.grid_rowconfigure(
            0, weight=2)  # Current weather (larger)
        self.main_frame.grid_rowconfigure(1, weight=1)  # Hourly forecast
        self.main_frame.grid_rowconfigure(2, weight=1)  # Calendar
        self.main_frame.grid_rowconfigure(3, weight=0)  # Alerts
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Current weather section
        self.current_frame = tk.Frame(self.main_frame, bg='black')
        self.current_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        self.temp_label = tk.Label(self.current_frame, text="--°",
                                   font=("Helvetica", 100), fg="white", bg="black")
        self.temp_label.pack()

        self.condition_label = tk.Label(self.current_frame, text="--",
                                        font=("Helvetica", 30), fg="white", bg="black")
        self.condition_label.pack(pady=(10, 0))

        self.details_frame = tk.Frame(self.current_frame, bg='black')
        self.details_frame.pack(pady=(10, 0))

        self.humidity_label = tk.Label(self.details_frame, text="Humidity: --%",
                                       font=("Helvetica", 18), fg="lightgray", bg="black")
        self.humidity_label.grid(row=0, column=0, padx=20)

        self.wind_label = tk.Label(self.details_frame, text="Wind: --",
                                   font=("Helvetica", 18), fg="lightgray", bg="black")
        self.wind_label.grid(row=0, column=1, padx=20)

        # Hourly forecast section
        self.hourly_frame = tk.Frame(self.main_frame, bg='black')
        self.hourly_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        self.hourly_label = tk.Label(self.hourly_frame, text="Hourly Forecast",
                                     font=("Helvetica", 24), fg="white", bg="black")
        self.hourly_label.pack(anchor="w")

        self.hourly_container = tk.Frame(self.hourly_frame, bg='black')
        self.hourly_container.pack(fill="x", pady=(5, 0))

        # Calendar section
        self.calendar_frame = tk.Frame(self.main_frame, bg='black')
        self.calendar_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))

        self.calendar_label = tk.Label(self.calendar_frame, text="Today's Schedule",
                                       font=("Helvetica", 24), fg="white", bg="black")
        self.calendar_label.pack(anchor="w")

        self.calendar_container = tk.Frame(self.calendar_frame, bg='black')
        self.calendar_container.pack(fill="both", expand=True, pady=(5, 0))

        # Alerts section
        self.alerts_frame = tk.Frame(self.main_frame, bg='black')
        self.alerts_frame.grid(row=3, column=0, sticky="nsew")

        self.alerts_label = tk.Label(self.alerts_frame, text="Alerts",
                                     font=("Helvetica", 24), fg="white", bg="black")
        self.alerts_label.pack(anchor="w")

        self.alerts_text = tk.Text(self.alerts_frame, height=4, bg='black', fg='red',
                                   font=("Helvetica", 16), wrap="word")
        self.alerts_text.pack(fill="x", pady=(5, 0))
        self.alerts_text.config(state="disabled")

        # Bottom time display
        self.time_label = tk.Label(self.root, text="",
                                   font=("Helvetica", 20), fg="white", bg="black")
        self.time_label.grid(row=1, column=0, sticky="se", padx=20, pady=10)

        # Import config loader
        from utils.config_loader import ConfigLoader
        config = ConfigLoader()

        # Start update threads
        self.running = True
        self.weather_update_thread = threading.Thread(
            target=self.weather_update_loop, daemon=True)
        self.weather_update_thread.start()

        if calendar_controller is not None:
            self.calendar_update_thread = threading.Thread(
                target=self.calendar_update_loop, daemon=True)
            self.calendar_update_thread.start()

        self.update_time()

    def update_weather(self, weather_data_list):
        """Update the display with new weather data for multiple periods"""
        if not weather_data_list:
            return

        # Update current weather (first period)
        current_weather = weather_data_list[0]
        self.temp_label.config(
            text=f"{current_weather.temperature}°{current_weather.temperature_unit}")
        self.condition_label.config(text=current_weather.short_forecast)
        self.humidity_label.config(
            text=f"Humidity: {current_weather.relative_humidity}%")
        self.wind_label.config(
            text=f"Wind: {current_weather.wind_speed} {current_weather.wind_direction}")

        # TODO: Update hourly forecast - we could show the three periods here instead
        # For now, we'll update the hourly container to show our three-period forecast
        self.update_hourly_forecast(weather_data_list)

    def update_hourly_forecast(self, weather_data_list):
        """Update the hourly forecast container with our three-period forecast"""
        # Clear existing widgets
        for widget in self.hourly_container.winfo_children():
            widget.destroy()

        if not weather_data_list:
            return

        # Create a label for each period
        # Limit to 3 periods
        for i, weather_data in enumerate(weather_data_list[:3]):
            period_frame = tk.Frame(self.hourly_container, bg='black')
            period_frame.pack(side="left", expand=True, fill="both", padx=5)

            # Period name from API
            period_name = weather_data.period_name or f'Period {i+1}'
            name_label = tk.Label(period_frame, text=period_name,
                                  font=("Helvetica", 16), fg="white", bg="black")
            name_label.pack(pady=(5, 0))

            # Temperature
            temp_label = tk.Label(period_frame, text=f"{weather_data.temperature}°{weather_data.temperature_unit}",
                                  font=("Helvetica", 20), fg="yellow", bg="black")
            temp_label.pack(pady=2)

            # Conditions
            condition_label = tk.Label(period_frame, text=weather_data.short_forecast,
                                       font=("Helvetica", 12), fg="white", bg="black")
            condition_label.pack(pady=2)

            # Humidity
            humidity_label = tk.Label(period_frame, text=f"Humidity: {weather_data.relative_humidity}%",
                                      font=("Helvetica", 12), fg="lightgray", bg="black")
            humidity_label.pack(pady=2)

            # Wind
            wind_label = tk.Label(period_frame, text=f"Wind: {weather_data.wind_speed} {weather_data.wind_direction}",
                                  font=("Helvetica", 12), fg="lightgray", bg="black")
            wind_label.pack(pady=(2, 5))

    def update_calendar(self, events):
        """Update the calendar display"""
        # Clear existing widgets
        for widget in self.calendar_container.winfo_children():
            widget.destroy()

        if not events:
            no_events_label = tk.Label(self.calendar_container, text="No events today",
                                       font=("Helvetica", 18), fg="lightgray", bg="black")
            no_events_label.pack(pady=20)
            return

        # Display events
        for i, event in enumerate(events[:5]):  # Show max 5 events
            event_frame = tk.Frame(self.calendar_container, bg='black')
            event_frame.pack(fill="x", pady=5)

            # Time
            time_str = event.start_time.strftime("%I:%M %p")
            if event.is_all_day:
                time_str = "All Day"

            time_label = tk.Label(event_frame, text=time_str,
                                  font=("Helvetica", 16), fg="lightgray", bg="black", width=10)
            time_label.pack(side="left", padx=(0, 10))

            # Event details
            details_frame = tk.Frame(event_frame, bg='black')
            details_frame.pack(side="left", fill="x", expand=True)

            title_label = tk.Label(details_frame, text=event.summary,
                                   font=("Helvetica", 18), fg="white", bg="black", anchor="w")
            title_label.pack(anchor="w")

            if event.location:
                location_label = tk.Label(details_frame, text=f"📍 {event.location}",
                                          font=("Helvetica", 14), fg="lightgray", bg="black", anchor="w")
                location_label.pack(anchor="w")

    def update_time(self):
        """Update the time display"""
        current_time = datetime.now().strftime("%A, %B %d, %Y %I:%M:%S %p")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)  # Update every second

    def weather_update_loop(self):
        """Background thread to periodically fetch weather data"""
        # Get coordinates from config
        from utils.config_loader import ConfigLoader
        config = ConfigLoader()
        latitude = config.get_latitude()
        longitude = config.get_longitude()

        while self.running:
            try:
                weather_data_list = self.weather_controller.get_weather(
                    latitude, longitude, periods_count=3)
                # Update UI in main thread
                self.root.after(0, self.update_weather, weather_data_list)
            except Exception as e:
                print(f"Error fetching weather: {e}")

            # Wait 15 minutes before next update
            time.sleep(15 * 60)

    def calendar_update_loop(self):
        """Background thread to periodically fetch calendar data"""
        while self.running:
            try:
                events = self.calendar_controller.get_today_events(
                    max_results=10)
                # Update UI in main thread
                self.root.after(0, self.update_calendar, events)
            except Exception as e:
                print(f"Error fetching calendar: {e}")

            # Wait 5 minutes before next update
            time.sleep(5 * 60)

    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """Handle application closing"""
        self.running = False
        self.root.destroy()


# Example usage (will be replaced with proper dependency injection)
if __name__ == "__main__":
    # This is just for testing - in real app, we'd use proper DI
    from framework_drivers.weather_gateway import WeatherGateway
    from use_cases.fetch_weather import FetchWeatherUseCase
    from interface_adapters.weather_controller import WeatherController
    from framework_drivers.calendar_gateway import CalendarGateway
    from use_cases.fetch_calendar import FetchCalendarUseCase
    from interface_adapters.calendar_controller import CalendarController

    try:
        weather_gateway = WeatherGateway()
        fetch_weather_use_case = FetchWeatherUseCase(weather_gateway)
        weather_controller = WeatherController(fetch_weather_use_case)

        calendar_gateway = CalendarGateway()
        fetch_calendar_use_case = FetchCalendarUseCase(calendar_gateway)
        calendar_controller = CalendarController(fetch_calendar_use_case)

        app = WeatherAndCalendarDisplay(
            weather_controller, calendar_controller)
        app.run()
    except Exception as e:
        print(f"Error initializing application: {e}")
        print("Make sure you have credentials.json for Google Calendar API")
