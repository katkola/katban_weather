import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import patch, Mock
from datetime import datetime, date, timezone

from icalendar import Calendar, Event
from framework_drivers.ics_calendar_gateway import IcsCalendarGateway
from use_cases.fetch_calendar import FetchCalendarUseCase
from entities.calendar_event import CalendarEvent


def _build_ics(events):
    cal = Calendar()
    cal.add('prodid', '-//Test//mxm.dk//')
    cal.add('version', '2.0')

    for ev_data in events:
        e = Event()
        e.add('summary', ev_data['summary'])
        e.add('dtstart', ev_data['dtstart'])
        dtend = ev_data.get('dtend')
        if dtend is not None:
            e.add('dtend', dtend)
        if 'location' in ev_data:
            e.add('location', ev_data['location'])
        if 'description' in ev_data:
            e.add('description', ev_data['description'])
        if 'categories' in ev_data:
            e.add('categories', ev_data['categories'])
        cal.add_component(e)

    return cal.to_ical().decode('utf-8')


def _utc_today():
    return datetime.now(timezone.utc).date()


def _make_mock_response(ics_text, status=200):
    mock_resp = Mock()
    mock_resp.text = ics_text
    mock_resp.status_code = status
    mock_resp.raise_for_status = Mock()
    if status >= 400:
        mock_resp.raise_for_status.side_effect = Exception(
            f"HTTP {status}")
    return mock_resp


URL = 'https://example.com/cal.ics'


class TestIcsCalendarGateway:
    def test_returns_google_api_style_dicts(self):
        today = _utc_today()
        ics = _build_ics([
            {
                'summary': 'Test Event',
                'dtstart': datetime(today.year, today.month, today.day, 10, 0, tzinfo=timezone.utc),
                'dtend': datetime(today.year, today.month, today.day, 11, 0, tzinfo=timezone.utc),
                'location': 'Room A',
                'description': 'A test event',
            },
        ])

        with patch('requests.get', return_value=_make_mock_response(ics)):
            gateway = IcsCalendarGateway([{'url': URL}])
            events = gateway.get_today_events(max_results=10)

        assert len(events) == 1
        e = events[0]
        assert e['summary'] == 'Test Event'
        assert 'dateTime' in e['start']
        assert 'dateTime' in e['end']
        assert e['location'] == 'Room A'
        assert e['description'] == 'A test event'
        assert e['eventType'] == 'default'

    def test_all_day_events_use_date_format(self):
        today = _utc_today()
        tomorrow = date(today.year, today.month, today.day + 1)
        ics = _build_ics([
            {
                'summary': 'All Day Thing',
                'dtstart': today,
                'dtend': tomorrow,
            },
        ])

        with patch('requests.get', return_value=_make_mock_response(ics)):
            gateway = IcsCalendarGateway([{'url': URL}])
            events = gateway.get_today_events(max_results=10)

        assert len(events) == 1
        e = events[0]
        assert e['summary'] == 'All Day Thing'
        assert 'date' in e['start']
        assert 'dateTime' not in e['start']
        assert e['start']['date'] == today.isoformat()

    def test_maps_categories_to_event_type(self):
        today = _utc_today()
        ics = _build_ics([
            {
                'summary': 'Task Item',
                'dtstart': datetime(today.year, today.month, today.day, 14, 0, tzinfo=timezone.utc),
                'dtend': datetime(today.year, today.month, today.day, 15, 0, tzinfo=timezone.utc),
                'categories': ['task'],
            },
        ])

        with patch('requests.get', return_value=_make_mock_response(ics)):
            gateway = IcsCalendarGateway([{'url': URL}])
            events = gateway.get_today_events(max_results=10)

        assert events[0]['eventType'] == 'task'

    def test_filters_events_not_today(self):
        today = _utc_today()
        yesterday = date(today.year, today.month, today.day - 1)
        tomorrow = date(today.year, today.month, today.day + 1)
        ics = _build_ics([
            {
                'summary': 'Yesterday Event',
                'dtstart': datetime(yesterday.year, yesterday.month, yesterday.day, 10, 0, tzinfo=timezone.utc),
                'dtend': datetime(yesterday.year, yesterday.month, yesterday.day, 11, 0, tzinfo=timezone.utc),
            },
            {
                'summary': 'Today Event',
                'dtstart': datetime(today.year, today.month, today.day, 10, 0, tzinfo=timezone.utc),
                'dtend': datetime(today.year, today.month, today.day, 11, 0, tzinfo=timezone.utc),
            },
            {
                'summary': 'Tomorrow Event',
                'dtstart': datetime(tomorrow.year, tomorrow.month, tomorrow.day, 10, 0, tzinfo=timezone.utc),
                'dtend': datetime(tomorrow.year, tomorrow.month, tomorrow.day, 11, 0, tzinfo=timezone.utc),
            },
        ])

        with patch('requests.get', return_value=_make_mock_response(ics)):
            gateway = IcsCalendarGateway([{'url': URL}])
            events = gateway.get_today_events(max_results=10)

        summaries = [e['summary'] for e in events]
        assert 'Today Event' in summaries
        assert 'Yesterday Event' not in summaries
        assert 'Tomorrow Event' not in summaries

    def test_respects_max_results(self):
        today = _utc_today()
        events_data = []
        for i in range(5):
            events_data.append({
                'summary': f'Event {i}',
                'dtstart': datetime(today.year, today.month, today.day, 9 + i, 0, tzinfo=timezone.utc),
                'dtend': datetime(today.year, today.month, today.day, 10 + i, 0, tzinfo=timezone.utc),
            })

        ics = _build_ics(events_data)
        with patch('requests.get', return_value=_make_mock_response(ics)):
            gateway = IcsCalendarGateway([{'url': URL}])
            events = gateway.get_today_events(max_results=3)

        assert len(events) == 3

    def test_sorts_by_start_time(self):
        today = _utc_today()
        ics = _build_ics([
            {
                'summary': 'Late',
                'dtstart': datetime(today.year, today.month, today.day, 16, 0, tzinfo=timezone.utc),
                'dtend': datetime(today.year, today.month, today.day, 17, 0, tzinfo=timezone.utc),
            },
            {
                'summary': 'Early',
                'dtstart': datetime(today.year, today.month, today.day, 8, 0, tzinfo=timezone.utc),
                'dtend': datetime(today.year, today.month, today.day, 9, 0, tzinfo=timezone.utc),
            },
            {
                'summary': 'Middle',
                'dtstart': datetime(today.year, today.month, today.day, 12, 0, tzinfo=timezone.utc),
                'dtend': datetime(today.year, today.month, today.day, 13, 0, tzinfo=timezone.utc),
            },
        ])

        with patch('requests.get', return_value=_make_mock_response(ics)):
            gateway = IcsCalendarGateway([{'url': URL}])
            events = gateway.get_today_events(max_results=10)

        assert [e['summary'] for e in events] == ['Early', 'Middle', 'Late']

    def test_network_error_returns_empty_list(self):
        with patch('requests.get', side_effect=Exception("Connection error")):
            gateway = IcsCalendarGateway([{'url': URL}])
            events = gateway.get_today_events()

        assert events == []

    def test_invalid_ics_returns_empty_list(self):
        with patch('requests.get', return_value=_make_mock_response("NOT ICS")):
            gateway = IcsCalendarGateway([{'url': URL}])
            events = gateway.get_today_events()

        assert events == []

    def test_events_are_parseable_by_use_case(self):
        today = _utc_today()
        ics = _build_ics([
            {
                'summary': 'UseCase Event',
                'dtstart': datetime(today.year, today.month, today.day, 10, 0, tzinfo=timezone.utc),
                'dtend': datetime(today.year, today.month, today.day, 11, 0, tzinfo=timezone.utc),
            },
            {
                'summary': 'UseCase All Day',
                'dtstart': today,
                'dtend': date(today.year, today.month, today.day + 1),
            },
        ])

        with patch('requests.get', return_value=_make_mock_response(ics)):
            gateway = IcsCalendarGateway([{'url': URL}])
            use_case = FetchCalendarUseCase(gateway)
            events = use_case.execute(max_results=10)

        assert len(events) == 2
        assert all(isinstance(e, CalendarEvent) for e in events)
        timed = [e for e in events if not e.is_all_day]
        all_day = [e for e in events if e.is_all_day]
        assert len(timed) == 1
        assert len(all_day) == 1
        assert timed[0].summary == 'UseCase Event'
        assert all_day[0].summary == 'UseCase All Day'

    def test_merges_events_from_multiple_urls(self):
        today = _utc_today()
        ics_a = _build_ics([
            {
                'summary': 'From A',
                'dtstart': datetime(today.year, today.month, today.day, 10, 0, tzinfo=timezone.utc),
                'dtend': datetime(today.year, today.month, today.day, 11, 0, tzinfo=timezone.utc),
            },
        ])
        ics_b = _build_ics([
            {
                'summary': 'From B',
                'dtstart': datetime(today.year, today.month, today.day, 14, 0, tzinfo=timezone.utc),
                'dtend': datetime(today.year, today.month, today.day, 15, 0, tzinfo=timezone.utc),
            },
        ])

        mock_get = Mock(side_effect=[
            _make_mock_response(ics_a),
            _make_mock_response(ics_b),
        ])
        with patch('requests.get', mock_get):
            gateway = IcsCalendarGateway([
                {'url': 'https://a.com/cal.ics', 'label': 'Cal A'},
                {'url': 'https://b.com/cal.ics', 'label': 'Cal B'},
            ])
            events = gateway.get_today_events(max_results=10)

        assert len(events) == 2
        assert events[0]['summary'] == 'From A'
        assert events[0]['calendar_name'] == 'Cal A'
        assert events[1]['summary'] == 'From B'
        assert events[1]['calendar_name'] == 'Cal B'

    def test_one_url_failure_does_not_block_other(self):
        today = _utc_today()
        ics = _build_ics([
            {
                'summary': 'Survivor',
                'dtstart': datetime(today.year, today.month, today.day, 10, 0, tzinfo=timezone.utc),
                'dtend': datetime(today.year, today.month, today.day, 11, 0, tzinfo=timezone.utc),
            },
        ])

        mock_get = Mock(side_effect=[
            Exception("Network error"),
            _make_mock_response(ics),
        ])
        with patch('requests.get', mock_get):
            gateway = IcsCalendarGateway([
                {'url': 'https://bad.com/cal.ics'},
                {'url': 'https://good.com/cal.ics'},
            ])
            events = gateway.get_today_events(max_results=10)

        assert len(events) == 1
        assert events[0]['summary'] == 'Survivor'

    def test_tags_events_with_calendar_name(self):
        today = _utc_today()
        ics = _build_ics([
            {
                'summary': 'Labelled Event',
                'dtstart': datetime(today.year, today.month, today.day, 10, 0, tzinfo=timezone.utc),
                'dtend': datetime(today.year, today.month, today.day, 11, 0, tzinfo=timezone.utc),
            },
        ])

        with patch('requests.get', return_value=_make_mock_response(ics)):
            gateway = IcsCalendarGateway([{'url': URL, 'label': 'My Cal'}])
            events = gateway.get_today_events(max_results=10)

        assert events[0]['calendar_name'] == 'My Cal'

    def test_caches_ics_content(self):
        today = _utc_today()
        ics = _build_ics([
            {
                'summary': 'Cached Event',
                'dtstart': datetime(today.year, today.month, today.day, 10, 0, tzinfo=timezone.utc),
                'dtend': datetime(today.year, today.month, today.day, 11, 0, tzinfo=timezone.utc),
            },
        ])

        mock_get = Mock(return_value=_make_mock_response(ics))
        with patch('requests.get', mock_get):
            gateway = IcsCalendarGateway([{'url': URL}], cache_ttl=60)
            gateway.get_today_events()
            gateway.get_today_events()

        assert mock_get.call_count == 1

    def test_cache_expires(self):
        today = _utc_today()
        ics = _build_ics([
            {
                'summary': 'Event',
                'dtstart': datetime(today.year, today.month, today.day, 10, 0, tzinfo=timezone.utc),
                'dtend': datetime(today.year, today.month, today.day, 11, 0, tzinfo=timezone.utc),
            },
        ])

        mock_get = Mock(return_value=_make_mock_response(ics))
        with patch('requests.get', mock_get):
            gateway = IcsCalendarGateway([{'url': URL}], cache_ttl=0)
            gateway.get_today_events()
            gateway.get_today_events()

        assert mock_get.call_count == 2

    def test_handles_events_without_end_time(self):
        today = _utc_today()
        ics_text = _build_ics([
            {
                'summary': 'No End Event',
                'dtstart': datetime(today.year, today.month, today.day, 10, 0, tzinfo=timezone.utc),
            },
        ])

        with patch('requests.get', return_value=_make_mock_response(ics_text)):
            gateway = IcsCalendarGateway([{'url': URL}])
            use_case = FetchCalendarUseCase(gateway)
            events = use_case.execute(max_results=10)

        assert len(events) == 1
        assert events[0].summary == 'No End Event'

    def test_returns_empty_for_no_events_today(self):
        today = _utc_today()
        future = date(today.year, today.month, today.day + 5)
        ics = _build_ics([
            {
                'summary': 'Future Event',
                'dtstart': datetime(future.year, future.month, future.day, 10, 0, tzinfo=timezone.utc),
                'dtend': datetime(future.year, future.month, future.day, 11, 0, tzinfo=timezone.utc),
            },
        ])

        with patch('requests.get', return_value=_make_mock_response(ics)):
            gateway = IcsCalendarGateway([{'url': URL}])
            events = gateway.get_today_events()

        assert events == []
