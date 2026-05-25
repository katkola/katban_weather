import zoneinfo
from typing import List, Dict, Any, Optional
from entities.calendar_event import CalendarEvent
from entities.weather_data import WeatherData
from use_cases.display_info import DisplayInfo
from utils.weather_art import get_weather_symbol, get_current_weather_art


class ViewPresenter:
    @staticmethod
    def _parse_alerts(info: DisplayInfo) -> List[Dict[str, Any]]:
        alerts = []
        for feature in (info.alerts or []):
            p = feature.get('properties', {})
            alerts.append({
                'event': p.get('event', 'Alert'),
                'headline': p.get('headline', ''),
                'severity': p.get('severity', 'Unknown'),
            })
        return alerts

    def present_weather(self, info: DisplayInfo) -> Dict[str, Any]:
        periods = info.weather_periods
        if not periods:
            return {
                'current': {
                    'temp_text': '--°',
                    'condition': '--',
                    'art': '',
                    'humidity': 'Humidity: --%',
                    'wind': 'Wind: --',
                },
                'hourly': [],
            }

        cw = periods[0]
        art = get_current_weather_art(cw.short_forecast, cw.period_name)
        current = {
            'temp_text': f"{cw.temperature}°{cw.temperature_unit}",
            'condition': cw.short_forecast,
            'art': art,
            'humidity': f"Humidity: {cw.relative_humidity}%",
            'wind': f"Wind: {cw.wind_speed} {cw.wind_direction}",
        }

        hourly = []
        for p in periods[:3]:
            symbol = get_weather_symbol(p.short_forecast, p.period_name)
            hourly.append({
                'name': p.period_name or f'Period {len(hourly) + 1}',
                'temp': f"{p.temperature}°{p.temperature_unit}",
                'condition': f"{symbol} {p.short_forecast}",
                'humidity': f"Humidity: {p.relative_humidity}%",
                'wind': f"Wind: {p.wind_speed} {p.wind_direction}",
            })

        return {'current': current, 'hourly': hourly, 'alerts': self._parse_alerts(info)}

    def present_calendar(self, info: DisplayInfo) -> Dict[str, Any]:
        events = info.calendar_events
        if not events:
            return {'sections': []}

        sections = []

        all_day = [e for e in events if e.is_all_day]
        timed_events = [e for e in events
                        if not e.is_all_day and e.category == 'event']
        timed_tasks = [e for e in events
                       if not e.is_all_day and e.category == 'task']

        if all_day:
            sections.append({
                'title': 'ALL DAY',
                'items': [self._item_vm(e) for e in all_day],
            })

        if timed_events:
            sections.append({
                'title': 'EVENTS',
                'items': [self._item_vm(e) for e in timed_events],
            })

        if timed_tasks:
            sections.append({
                'title': 'TASKS',
                'items': [self._item_vm(e) for e in timed_tasks],
            })

        return {'sections': sections}

    @staticmethod
    def _item_vm(event: CalendarEvent) -> Dict[str, Any]:
        LOCAL_TZ = zoneinfo.ZoneInfo("America/New_York")
        start = event.start_time.astimezone(LOCAL_TZ) if event.start_time.tzinfo else event.start_time
        time_str = start.strftime("%I:%M %p")
        if event.is_all_day:
            time_str = "All Day"
        return {
            'time': time_str,
            'title': event.summary,
            'location': event.location,
            'source': event.source,
        }
