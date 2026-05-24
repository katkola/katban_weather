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
        from use_cases.display_info import FetchDisplayInfoUseCase
        from interface_adapters.view_presenter import ViewPresenter
        self.display_use_case = FetchDisplayInfoUseCase(
            weather_controller, calendar_controller)
        self.presenter = ViewPresenter()
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

        # Configure main frame grid - side by side
        self.main_frame.grid_columnconfigure(0, weight=1)  # Weather side
        self.main_frame.grid_columnconfigure(1, weight=1)  # Calendar side
        self.main_frame.grid_rowconfigure(0, weight=1)     # Main content
        self.main_frame.grid_rowconfigure(1, weight=0)     # Alerts

        # Weather side (left column)
        self.weather_side = tk.Frame(self.main_frame, bg='black')
        self.weather_side.grid(row=0, column=0, sticky="nsew", pady=(0, 10), padx=(0, 10))
        self.weather_side.grid_rowconfigure(0, weight=2)  # Current weather
        self.weather_side.grid_rowconfigure(1, weight=1)  # Hourly forecast
        self.weather_side.grid_columnconfigure(0, weight=1)

        # Current weather section
        self.current_frame = tk.Frame(self.weather_side, bg='black')
        self.current_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        self.temp_label = tk.Label(self.current_frame, text="--°",
                                   font=("Helvetica", 100), fg="white", bg="black")
        self.temp_label.pack()

        self.art_label = tk.Label(self.current_frame, text="",
                                  font=("Courier", 14), fg="white", bg="black",
                                  justify="center")
        self.art_label.pack(pady=(5, 0))

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
        self.hourly_frame = tk.Frame(self.weather_side, bg='black')
        self.hourly_frame.grid(row=1, column=0, sticky="nsew")

        self.hourly_label = tk.Label(self.hourly_frame, text="Hourly Forecast",
                                     font=("Helvetica", 24), fg="white", bg="black")
        self.hourly_label.pack(anchor="w")

        self.hourly_container = tk.Frame(self.hourly_frame, bg='black')
        self.hourly_container.pack(fill="x", pady=(5, 0))

        # Calendar section (right column)
        self.calendar_frame = tk.Frame(self.main_frame, bg='black')
        self.calendar_frame.grid(row=0, column=1, sticky="nsew", pady=(0, 10))

        self.calendar_label = tk.Label(self.calendar_frame, text="Today's Schedule",
                                       font=("Helvetica", 24), fg="white", bg="black")
        self.calendar_label.pack(anchor="w")

        self.calendar_container = tk.Frame(self.calendar_frame, bg='black')
        self.calendar_container.pack(fill="both", expand=True, pady=(5, 0))

        # Alerts section (bottom, spanning both columns)
        self.alerts_frame = tk.Frame(self.main_frame, bg='black')
        self.alerts_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

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

        self.calendar_update_thread = threading.Thread(
            target=self.calendar_update_loop, daemon=True)
        self.calendar_update_thread.start()

        self.update_time()

    def render_weather(self, weather_vm):
        cw = weather_vm['current']
        self.temp_label.config(text=cw['temp_text'])
        self.art_label.config(text=cw['art'])
        self.condition_label.config(text=cw['condition'])
        self.humidity_label.config(text=cw['humidity'])
        self.wind_label.config(text=cw['wind'])
        self._render_hourly(weather_vm['hourly'])

    def _render_hourly(self, periods):
        for widget in self.hourly_container.winfo_children():
            widget.destroy()

        if not periods:
            return

        for p in periods:
            frame = tk.Frame(self.hourly_container, bg='black')
            frame.pack(side="left", expand=True, fill="both", padx=5)

            tk.Label(frame, text=p['name'],
                     font=("Helvetica", 16), fg="white", bg="black"
                     ).pack(pady=(5, 0))
            tk.Label(frame, text=p['temp'],
                     font=("Helvetica", 20), fg="yellow", bg="black"
                     ).pack(pady=2)
            tk.Label(frame, text=p['condition'],
                     font=("Helvetica", 12), fg="white", bg="black"
                     ).pack(pady=2)
            tk.Label(frame, text=p['humidity'],
                     font=("Helvetica", 12), fg="lightgray", bg="black"
                     ).pack(pady=2)
            tk.Label(frame, text=p['wind'],
                     font=("Helvetica", 12), fg="lightgray", bg="black"
                     ).pack(pady=(2, 5))

    @staticmethod
    def _draw_rounded_border(canvas):
        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        if cw < 2 or ch < 2:
            return

        r = 8
        x1, y1 = 1, 1
        x2, y2 = cw - 2, ch - 2
        color = '#87CEEB'

        canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r,
                          start=90, extent=90, outline=color, width=2,
                          style='arc', tag='border')
        canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r,
                          start=0, extent=90, outline=color, width=2,
                          style='arc', tag='border')
        canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2,
                          start=180, extent=90, outline=color, width=2,
                          style='arc', tag='border')
        canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2,
                          start=270, extent=90, outline=color, width=2,
                          style='arc', tag='border')

        canvas.create_line(x1 + r, y1, x2 - r, y1,
                           fill=color, width=2, tag='border')
        canvas.create_line(x2, y1 + r, x2, y2 - r,
                           fill=color, width=2, tag='border')
        canvas.create_line(x1 + r, y2, x2 - r, y2,
                           fill=color, width=2, tag='border')
        canvas.create_line(x1, y1 + r, x1, y2 - r,
                           fill=color, width=2, tag='border')

        canvas.tag_lower('border')

    def _render_event_row(self, parent, item):
        canvas = tk.Canvas(parent, bg='black', highlightthickness=0)
        canvas.pack(fill="x", pady=5)

        content = tk.Frame(canvas, bg='black')

        time_label = tk.Label(content, text=item['time'],
                              font=("Helvetica", 15), fg="lightgray",
                              bg="black", width=10)
        time_label.pack(side="left", padx=(20, 14), pady=8)

        details = tk.Frame(content, bg='black')
        details.pack(side="left", fill="x", expand=True)

        title_label = tk.Label(details, text=item['title'],
                               font=("Helvetica", 16), fg="white",
                               bg="black", anchor="w")
        title_label.pack(anchor="w", pady=(8, 2), padx=(0, 20))

        loc = item.get('location')
        if loc:
            location_label = tk.Label(details, text=f"📍 {loc}",
                                      font=("Helvetica", 13), fg="lightgray",
                                      bg="black", anchor="w")
            location_label.pack(anchor="w", padx=(0, 20), pady=(0, 6))

        content.update_idletasks()
        pad = 12
        canvas.configure(height=content.winfo_reqheight() + pad * 2)
        canvas.create_window((pad, pad), window=content, anchor="nw")
        canvas.after_idle(
            lambda c=canvas: self._draw_rounded_border(c))

    @staticmethod
    def _render_section_header(parent, title, color="#888"):
        tk.Label(parent, text=title,
                 font=("Helvetica", 13, "bold"), fg=color, bg="black",
                 anchor="w"
                 ).pack(fill="x", pady=(10, 2))

    def render_calendar(self, calendar_vm):
        for widget in self.calendar_container.winfo_children():
            widget.destroy()

        sections = calendar_vm['sections']
        if not sections:
            tk.Label(self.calendar_container, text="No events today",
                     font=("Helvetica", 18), fg="lightgray", bg="black"
                     ).pack(pady=20)
            return

        for section in sections:
            self._render_section_header(
                self.calendar_container, section['title'], section['color'])
            for item in section['items']:
                self._render_event_row(self.calendar_container, item)

    def update_time(self):
        """Update the time display"""
        current_time = datetime.now().strftime("%A, %B %d, %Y %I:%M:%S %p")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)  # Update every second

    def weather_update_loop(self):
        from utils.config_loader import ConfigLoader
        config = ConfigLoader()
        latitude = config.get_latitude()
        longitude = config.get_longitude()

        while self.running:
            try:
                info = self.display_use_case.execute(
                    latitude, longitude)
                vm = self.presenter.present_weather(info)
                self.root.after(0, self.render_weather, vm)
            except Exception as e:
                print(f"Error fetching weather: {e}")

            time.sleep(15 * 60)

    def calendar_update_loop(self):
        from utils.config_loader import ConfigLoader
        config = ConfigLoader()
        latitude = config.get_latitude()
        longitude = config.get_longitude()

        while self.running:
            try:
                info = self.display_use_case.execute(
                    latitude, longitude)
                vm = self.presenter.present_calendar(info)
                self.root.after(0, self.render_calendar, vm)
            except Exception as e:
                print(f"Error fetching calendar: {e}")

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
