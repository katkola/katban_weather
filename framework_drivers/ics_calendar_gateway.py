import zoneinfo
import time
import requests
from datetime import datetime, date, timedelta, timezone
from typing import List, Dict, Any, Optional
from icalendar import Calendar


class IcsCalendarGateway:
    TIMEZONE = zoneinfo.ZoneInfo("America/New_York")

    def __init__(self, calendars: List[Dict[str, str]], cache_ttl: int = 60):
        self.calendars = calendars
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, tuple[str, float]] = {}

    def _fetch_ics(self, url: str) -> str:
        now = time.time()
        cached = self._cache.get(url)
        if cached is not None and (now - cached[1]) < self.cache_ttl:
            return cached[0]
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        self._cache[url] = (response.text, now)
        return response.text

    def get_today_events(self, max_results: int = 10) -> List[Dict[str, Any]]:
        local_now = datetime.now(self.TIMEZONE)
        today_start_local = datetime(
            local_now.year, local_now.month, local_now.day, tzinfo=self.TIMEZONE)
        today_start = today_start_local.astimezone(timezone.utc)
        today_end = today_start + timedelta(days=1) - timedelta(microseconds=1)

        all_events = []
        for cal_entry in self.calendars:
            url = cal_entry['url']
            label = cal_entry.get('label', '')
            try:
                ics_content = self._fetch_ics(url)
                cal = Calendar.from_ical(ics_content)
                events = self._parse_calendar(cal, today_start, today_end)
                for e in events:
                    e['calendar_name'] = label
                all_events.extend(events)
            except Exception:
                continue

        all_events.sort(key=lambda e: (
            e.get('start', {}).get('dateTime') or e.get('start', {}).get('date', '')
        ))
        return all_events[:max_results]

    def _parse_calendar(self, cal, today_start, today_end):
        events = []
        for component in cal.walk():
            if component.name != 'VEVENT':
                continue

            dtstart = component.get('dtstart')
            dtend = component.get('dtend')
            if dtstart is None:
                continue

            start_dt = dtstart.dt
            end_dt = dtend.dt if dtend is not None else None

            start_utc = self._to_utc_datetime(start_dt)
            end_utc = self._to_utc_datetime(end_dt) if end_dt is not None else start_utc + timedelta(hours=1)

            if start_utc > today_end or end_utc < today_start:
                continue

            categories = component.get('categories')
            category = 'default'
            if categories is not None:
                cat_list = list(categories)
                if cat_list:
                    category = str(cat_list[0])

            event = {
                'summary': str(component.get('summary', 'No Title')),
                'start': self._build_start(start_dt),
                'end': self._build_start(end_dt) if end_dt is not None else self._build_start(start_dt),
                'eventType': category,
            }

            location = component.get('location')
            if location is not None:
                event['location'] = str(location)

            description = component.get('description')
            if description is not None:
                event['description'] = str(description)

            events.append(event)
        return events

    @staticmethod
    def _to_utc_datetime(dt_value):
        if isinstance(dt_value, datetime):
            if dt_value.tzinfo is None:
                return dt_value.replace(tzinfo=timezone.utc)
            return dt_value.astimezone(timezone.utc)
        return datetime(dt_value.year, dt_value.month, dt_value.day, tzinfo=timezone.utc)

    @staticmethod
    def _build_start(dt_value):
        if isinstance(dt_value, datetime):
            return {'dateTime': dt_value.isoformat()}
        return {'date': dt_value.isoformat()}
