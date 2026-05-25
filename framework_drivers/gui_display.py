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

from framework_drivers.theme import Colors, Fonts, Padding


class WeatherAndCalendarDisplay:
    _SECTION_COLORS = {
        'ALL DAY': Colors.ALL_DAY,
        'EVENTS': Colors.EVENTS,
        'TASKS': Colors.TASKS,
    }

    def __init__(self, weather_controller, calendar_controller):
        from use_cases.display_info import FetchDisplayInfoUseCase
        from interface_adapters.view_presenter import ViewPresenter
        self.display_use_case = FetchDisplayInfoUseCase(
            weather_controller, calendar_controller)
        self.presenter = ViewPresenter()
        self.root = tk.Tk()
        self.root.title("KanBan Weather & Calendar Display")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg=Colors.BACKGROUND)

        # Configure grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Main frame
        self.main_frame = tk.Frame(self.root, bg=Colors.BACKGROUND)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Configure main frame grid - side by side
        self.main_frame.grid_columnconfigure(0, weight=1)  # Weather side
        self.main_frame.grid_columnconfigure(1, weight=1)  # Calendar side
        self.main_frame.grid_rowconfigure(0, weight=1)     # Main content
        self.main_frame.grid_rowconfigure(1, weight=0)     # Alerts

        # Weather side (left column)
        self.weather_side = tk.Frame(self.main_frame, bg=Colors.BACKGROUND)
        self.weather_side.grid(row=0, column=0, sticky="nsew", pady=(0, 10), padx=(0, 10))
        self.weather_side.grid_rowconfigure(0, weight=2)  # Current weather
        self.weather_side.grid_rowconfigure(1, weight=1)  # Forecast
        self.weather_side.grid_columnconfigure(0, weight=1)

        # Current weather section
        self.current_frame = tk.Frame(self.weather_side, bg=Colors.BACKGROUND)
        self.current_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        self.temp_label = tk.Label(self.current_frame, text="--°",
                                   font=(Fonts.DISPLAY, Fonts.TEMPERATURE),
                                   fg=Colors.PRIMARY_TEXT, bg=Colors.BACKGROUND)
        self.temp_label.pack()

        self.art_label = tk.Label(self.current_frame, text="",
                                  font=("Noto Color Emoji", Fonts.ART),
                                  fg=Colors.PRIMARY_TEXT, bg=Colors.BACKGROUND,
                                  justify="center")
        self.art_label.pack(pady=(5, 0))

        self.condition_label = tk.Label(self.current_frame, text="--",
                                        font=(Fonts.DISPLAY, Fonts.CONDITION),
                                        fg=Colors.PRIMARY_TEXT, bg=Colors.BACKGROUND)
        self.condition_label.pack(pady=(10, 0))

        self.details_frame = tk.Frame(self.current_frame, bg=Colors.BACKGROUND)
        self.details_frame.pack(pady=(10, 0))

        self.humidity_label = tk.Label(self.details_frame, text="Humidity: --%",
                                       font=(Fonts.FAMILY, Fonts.DETAIL),
                                       fg=Colors.SECONDARY_TEXT, bg=Colors.BACKGROUND)
        self.humidity_label.grid(row=0, column=0, padx=20)

        self.wind_label = tk.Label(self.details_frame, text="Wind: --",
                                   font=(Fonts.FAMILY, Fonts.DETAIL),
                                   fg=Colors.SECONDARY_TEXT, bg=Colors.BACKGROUND)
        self.wind_label.grid(row=0, column=1, padx=20)

        # Forecast section
        self.hourly_frame = tk.Frame(self.weather_side, bg=Colors.BACKGROUND)
        self.hourly_frame.grid(row=1, column=0, sticky="nsew")

        self.hourly_label = tk.Label(self.hourly_frame, text="Forecast",
                                     font=(Fonts.DISPLAY, Fonts.SECTION_TITLE),
                                     fg=Colors.PRIMARY_TEXT, bg=Colors.BACKGROUND)
        self.hourly_label.pack(anchor="w")

        self.hourly_container = tk.Frame(self.hourly_frame, bg=Colors.BACKGROUND)
        self.hourly_container.pack(fill="x", pady=(5, 0))

        # Calendar section (right column)
        self.calendar_frame = tk.Frame(self.main_frame, bg=Colors.BACKGROUND)
        self.calendar_frame.grid(row=0, column=1, sticky="nsew", pady=(0, 10))

        self.calendar_label = tk.Label(self.calendar_frame, text="Today's Schedule",
                                       font=(Fonts.DISPLAY, Fonts.SECTION_TITLE),
                                       fg=Colors.PRIMARY_TEXT, bg=Colors.BACKGROUND)
        self.calendar_label.pack(anchor="w")

        self.calendar_container = tk.Frame(self.calendar_frame, bg=Colors.BACKGROUND)
        self.calendar_container.pack(fill="both", expand=True, pady=(5, 0))

        # Alerts section (bottom, spanning both columns)
        self.alerts_frame = tk.Frame(self.main_frame, bg=Colors.BACKGROUND)
        self.alerts_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.alerts_label = tk.Label(self.alerts_frame, text="Alerts",
                                     font=(Fonts.DISPLAY, Fonts.ALERTS_TITLE),
                                     fg=Colors.PRIMARY_TEXT, bg=Colors.BACKGROUND)
        self.alerts_label.pack(anchor="w")

        self.alerts_text = tk.Text(self.alerts_frame, height=4,
                                   bg=Colors.BACKGROUND, fg=Colors.ALERT_TEXT,
                                   font=(Fonts.FAMILY, Fonts.SECTION_TITLE),
                                   wrap="word")
        self.alerts_text.pack(fill="x", pady=(5, 0))
        self.alerts_text.config(state="disabled")

        # Loading overlay (covers everything until first data fetch)
        self.loading_frame = tk.Frame(self.root, bg=Colors.BACKGROUND)
        self.loading_frame.place(x=0, y=0, relwidth=1, relheight=1)

        loading_center = tk.Frame(self.loading_frame, bg=Colors.BACKGROUND)
        loading_center.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(loading_center, text="Loading...",
                 font=(Fonts.DISPLAY, Fonts.LOADING_TITLE),
                 fg=Colors.PRIMARY_TEXT, bg=Colors.BACKGROUND
                 ).pack(pady=20)

        tk.Label(loading_center, text="Fetching weather and calendar data",
                 font=(Fonts.FAMILY, Fonts.SECTION_TITLE),
                 fg=Colors.SECONDARY_TEXT, bg=Colors.BACKGROUND
                 ).pack()

        self._loaded = False

        # Bottom time display
        self.time_label = tk.Label(self.root, text="",
                                   font=(Fonts.FAMILY, Fonts.TIME_LABEL),
                                   fg=Colors.PRIMARY_TEXT, bg=Colors.BACKGROUND)
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

    def _hide_loading(self):
        if not self._loaded:
            self._loaded = True
            self.loading_frame.place_forget()

    def render_weather(self, weather_vm):
        self._hide_loading()
        cw = weather_vm['current']
        self.temp_label.config(text=cw['temp_text'])
        self.art_label.config(text=cw['art'])
        self.condition_label.config(text=cw['condition'])
        self.humidity_label.config(text=cw['humidity'])
        self.wind_label.config(text=cw['wind'])
        self._render_hourly(weather_vm['hourly'])
        self._render_alerts(weather_vm.get('alerts', []))

    def _render_hourly(self, periods):
        for widget in self.hourly_container.winfo_children():
            widget.destroy()

        if not periods:
            return

        for p in periods:
            frame = tk.Frame(self.hourly_container, bg=Colors.BACKGROUND)
            frame.pack(side="left", expand=True, fill="both", padx=5)

            tk.Label(frame, text=p['name'],
                     font=(Fonts.FAMILY, Fonts.HOURLY_NAME),
                     fg=Colors.PRIMARY_TEXT, bg=Colors.BACKGROUND
                     ).pack(pady=(5, 0))
            tk.Label(frame, text=p['temp'],
                     font=(Fonts.FAMILY, Fonts.HOURLY_TEMP),
                     fg=Colors.ACCENT_TEXT, bg=Colors.BACKGROUND
                     ).pack(pady=2)
            tk.Label(frame, text=p['condition'],
                     font=(Fonts.FAMILY, Fonts.HOURLY_LABEL),
                     fg=Colors.PRIMARY_TEXT, bg=Colors.BACKGROUND
                     ).pack(pady=2)
            tk.Label(frame, text=p['humidity'],
                     font=(Fonts.FAMILY, Fonts.HOURLY_LABEL),
                     fg=Colors.SECONDARY_TEXT, bg=Colors.BACKGROUND
                     ).pack(pady=2)
            tk.Label(frame, text=p['wind'],
                     font=(Fonts.FAMILY, Fonts.HOURLY_LABEL),
                     fg=Colors.SECONDARY_TEXT, bg=Colors.BACKGROUND
                     ).pack(pady=(2, 5))

    def _render_alerts(self, alerts):
        self.alerts_text.config(state="normal")
        self.alerts_text.delete("1.0", tk.END)

        if not alerts:
            self.alerts_frame.grid_remove()
        else:
            self.alerts_frame.grid()
            for a in alerts:
                self.alerts_text.insert(tk.END,
                    f"⚠ {a['event']}: {a['headline']}\n\n")
            self.alerts_text.config(state="disabled")

    def _render_event_row(self, parent, item, accent_color):
        card = tk.Frame(parent, bg=Colors.CARD_BACKGROUND)
        card.pack(fill="x", pady=2)

        accent = tk.Frame(card, bg=accent_color, width=4)
        accent.pack(side="left", fill="y")

        content = tk.Frame(card, bg=Colors.CARD_BACKGROUND)
        content.pack(side="left", fill="x", expand=True)

        time_label = tk.Label(content, text=item['time'],
                              font=(Fonts.FAMILY, Fonts.CALENDAR_TIME),
                              fg=Colors.SECONDARY_TEXT,
                              bg=Colors.CARD_BACKGROUND, width=10)
        time_label.pack(side="left", padx=(14, 14), pady=8)

        details = tk.Frame(content, bg=Colors.CARD_BACKGROUND)
        details.pack(side="left", fill="x", expand=True)

        title_label = tk.Label(details, text=item['title'],
                               font=(Fonts.FAMILY, Fonts.CALENDAR_TITLE),
                               fg=Colors.PRIMARY_TEXT,
                               bg=Colors.CARD_BACKGROUND, anchor="w")
        title_label.pack(anchor="w", pady=(8, 2), padx=(0, 20))

        loc = item.get('location')
        if loc:
            location_label = tk.Label(details, text=f"📍 {loc}",
                                      font=(Fonts.FAMILY, Fonts.CALENDAR_LOCATION),
                                      fg=Colors.SECONDARY_TEXT,
                                      bg=Colors.CARD_BACKGROUND, anchor="w")
            location_label.pack(anchor="w", padx=(0, 20), pady=(0, 6))

    @staticmethod
    def _render_section_header(parent, title, color=Colors.SECTION_HEADER):
        tk.Label(parent, text=title,
                 font=(Fonts.FAMILY, Fonts.SECTION_HEADER, "bold"),
                 fg=color, bg=Colors.BACKGROUND,
                 anchor="w"
                 ).pack(fill="x", pady=(10, 2))

    def render_calendar(self, calendar_vm):
        self._hide_loading()
        for widget in self.calendar_container.winfo_children():
            widget.destroy()

        sections = calendar_vm['sections']
        if not sections:
            tk.Label(self.calendar_container, text="No events today",
                     font=(Fonts.FAMILY, Fonts.NO_EVENTS),
                     fg=Colors.SECONDARY_TEXT, bg=Colors.BACKGROUND
                     ).pack(pady=20)
            return

        for section in sections:
            color = self._SECTION_COLORS.get(
                section['title'], Colors.SECTION_HEADER)
            self._render_section_header(
                self.calendar_container, section['title'], color)
            for item in section['items']:
                self._render_event_row(self.calendar_container, item, color)

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


if __name__ == "__main__":
    from framework_drivers.weather_gateway import WeatherGateway
    from use_cases.fetch_weather import FetchWeatherUseCase
    from interface_adapters.weather_controller import WeatherController
    from framework_drivers.ics_calendar_gateway import IcsCalendarGateway
    from use_cases.fetch_calendar import FetchCalendarUseCase
    from interface_adapters.calendar_controller import CalendarController

    try:
        weather_gateway = WeatherGateway()
        fetch_weather_use_case = FetchWeatherUseCase(weather_gateway)
        weather_controller = WeatherController(fetch_weather_use_case)

        from utils.config_loader import ConfigLoader
        config = ConfigLoader()
        calendar_config = config.load_config().get('calendar', {})
        ics_url = calendar_config.get('ics_url', '')
        if ics_url:
            calendar_gateway = IcsCalendarGateway(ics_url)
        else:
            print("Calendar ICS URL not configured, using mock data.")
            from mock_data.calendar_mock_data import MockCalendarGateway
            calendar_gateway = MockCalendarGateway()

        fetch_calendar_use_case = FetchCalendarUseCase(calendar_gateway)
        calendar_controller = CalendarController(fetch_calendar_use_case)

        app = WeatherAndCalendarDisplay(
            weather_controller, calendar_controller)
        app.run()
    except Exception as e:
        print(f"Error initializing application: {e}")
