from datetime import datetime
from typing import Optional

class CalendarEvent:
    def __init__(self, summary: str, start_time: datetime, end_time: datetime,
                 location: Optional[str] = None, description: Optional[str] = None):
        self.summary = summary
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.description = description
    
    def to_dict(self):
        return {
            "summary": self.summary,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "location": self.location,
            "description": self.description
        }
    
    @property
    def duration_minutes(self) -> int:
        """Calculate duration in minutes"""
        if self.start_time and self.end_time:
            return int((self.end_time - self.start_time).total_seconds() / 60)
        return 0
    
    @property
    def is_all_day(self) -> bool:
        """Check if this is an all-day event"""
        # All-day events in Google Calendar have date-only values (no time component)
        # This is a simplified check - in practice, you'd need to check how the times are represented
        return (self.end_time - self.start_time).days >= 1 and \
               self.start_time.hour == 0 and self.start_time.minute == 0 and \
               self.end_time.hour == 0 and self.end_time.minute == 0