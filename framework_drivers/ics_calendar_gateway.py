import time
import requests
from datetime import datetime, date, timedelta, timezone
from typing import List, Dict, Any, Optional
from icalendar import Calendar


class IcsCalendarGateway:
    def __init__(self, ics_url: str, cache_ttl: int = 60):
        self.ics_url = ics_url
        self.cache_ttl = cache_ttl
        self._cache: Optional[str] = None
        self._cache_time: float = 0

    def _fetch_ics(self) -> str:
        now = time.time()
        if self._cache is not None and (now - self._cache_time) < self.cache_ttl:
            return self._cache
        response = requests.get(self.ics_url, timeout=10)
        response.raise_for_status()
        self._cache = response.text
        self._cache_time = now
        return self._cache

    def get_today_events(self, max_results: int = 10) -> List[Dict[str, Any]]:
        try:
            ics_content = self._fetch_ics()
            cal = Calendar.from_ical(ics_content)
        except Exception:
            return []

        utc_now = datetime.now(timezone.utc)
        today_start = datetime(
            utc_now.year, utc_now.month, utc_now.day, tzinfo=timezone.utc)
        today_end = today_start + timedelta(days=1) - timedelta(microseconds=1)

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

        events.sort(key=lambda e: (
            e.get('start', {}).get('dateTime') or e.get('start', {}).get('date', '')
        ))
        return events[:max_results]

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
