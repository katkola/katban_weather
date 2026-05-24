from use_cases.fetch_calendar import FetchCalendarUseCase


class CalendarController:
    def __init__(self, fetch_calendar_use_case: FetchCalendarUseCase):
        self.fetch_calendar_use_case = fetch_calendar_use_case

    def get_today_events(self, max_results: int = 10):
        """Get today's calendar events"""
        return self.fetch_calendar_use_case.execute(max_results)
