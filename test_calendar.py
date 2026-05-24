import sys
import os
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_calendar_event_creation():
    """Test that we can create a CalendarEvent object"""
    from entities.calendar_event import CalendarEvent

    start_time = datetime(2023, 1, 1, 10, 0, 0)
    end_time = datetime(2023, 1, 1, 11, 0, 0)

    event = CalendarEvent(
        summary="Test Meeting",
        start_time=start_time,
        end_time=end_time,
        location="Conference Room A",
        description="This is a test meeting"
    )

    assert event.summary == "Test Meeting"
    assert event.start_time == start_time
    assert event.end_time == end_time
    assert event.location == "Conference Room A"
    assert event.description == "This is a test meeting"
    assert event.duration_minutes == 60
    assert event.is_all_day == False

    print("✓ CalendarEvent creation test passed")


def test_calendar_event_all_day():
    """Test all-day event detection"""
    from entities.calendar_event import CalendarEvent

    start_time = datetime(2023, 1, 1, 0, 0, 0)
    end_time = datetime(2023, 1, 2, 0, 0, 0)

    event = CalendarEvent(
        summary="All Day Event",
        start_time=start_time,
        end_time=end_time
    )

    assert event.is_all_day == True
    assert event.duration_minutes == 1440  # 24 hours

    print("✓ CalendarEvent all-day test passed")


def test_calendar_event_to_dict():
    """Test that CalendarEvent.to_dict() works correctly"""
    from entities.calendar_event import CalendarEvent

    start_time = datetime(2023, 1, 1, 10, 0, 0)
    end_time = datetime(2023, 1, 1, 11, 0, 0)

    event = CalendarEvent(
        summary="Test Meeting",
        start_time=start_time,
        end_time=end_time,
        location="Conference Room A",
        description="This is a test meeting"
    )

    result = event.to_dict()

    expected = {
        "summary": "Test Meeting",
        "start_time": "2023-01-01T10:00:00",
        "end_time": "2023-01-01T11:00:00",
        "location": "Conference Room A",
        "description": "This is a test meeting"
    }

    assert result == expected
    print("✓ CalendarEvent.to_dict() test passed")


if __name__ == "__main__":
    test_calendar_event_creation()
    test_calendar_event_all_day()
    test_calendar_event_to_dict()
    print("All calendar tests passed!")
