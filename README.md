# KanBan Weather Display

A Raspberry Pi project that displays weather information from weather.gov API and calendar events from Google Calendar API using clean architecture principles.

## Project Structure

```
KanBan_Weather/
├── entities/                 # Business objects
│   ├── weather_data.py       # Weather data entity
│   └── calendar_event.py     # Calendar event entity
├── use_cases/                # Application-specific business rules
│   ├── fetch_weather.py      # Weather retrieval use case
│   └── fetch_calendar.py     # Calendar retrieval use case
├── interface_adapters/       # Controllers, presenters, gateways
│   ├── weather_controller.py # Weather controller
│   ├── calendar_controller.py # Calendar controller
│   └── view_presenter.py     # Prepares data for display
├── framework_drivers/        # External interfaces
│   ├── weather_gateway.py    # Weather.gov API client
│   ├── calendar_gateway.py   # Google Calendar API client
│   ├── gui_display.py        # Tkinter-based GUI display
│   └── simple_display.py     # Console-based display for testing
├── main.py                   # Main entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Features

- Clean architecture implementation
- Weather data from weather.gov API
- Calendar events from Google Calendar API
- Console-based display for testing
- GUI display (Tkinter) for Raspberry Pi with HDMI monitor
- Modular, testable code structure

## Setup

1. Install Python 3.x
2. Create virtual environment: `python3 -m venv venv`
3. Activate virtual environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

## Usage

### Console Display (for testing)
```bash
python simple_display.py
```

### GUI Display (for Raspberry Pi with HDMI monitor)
```bash
python main.py
```

## API Configuration

### Weather.gov API
No API key required for weather.gov API.

### Google Calendar API
1. Create a project in Google Cloud Console
2. Enable Google Calendar API
3. Create OAuth 2.0 credentials
4. Download credentials.json and place in project root
5. The first run will guide you through authentication

## Development

The project follows clean architecture principles:
- Entities layer: Business objects (WeatherData, CalendarEvent)
- Use cases layer: Application business rules (FetchWeather, FetchCalendar)
- Interface adapters layer: Controllers and gateways
- Frameworks & drivers layer: External APIs and GUI framework

## Testing

Run tests with:
```bash
python test_weather.py
```

## License

MIT