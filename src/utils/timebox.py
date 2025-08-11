"""Time and calendar utilities for business day calculations."""

from datetime import datetime, timedelta, time
from typing import List, Tuple
import pytz


class BusinessCalendar:
    """Handles business day calculations and time distributions."""

    def __init__(self, timezone: str = "Asia/Kolkata") -> None:
        """Initialize with timezone."""
        self.timezone = pytz.timezone(timezone)
        self.business_start = time(9, 0)  # 9:00 AM
        self.business_end = time(18, 0)   # 6:00 PM

    def is_business_day(self, dt: datetime) -> bool:
        """Check if datetime falls on a business day."""
        return dt.weekday() < 5  # Monday = 0, Friday = 4

    def is_business_hours(self, dt: datetime) -> bool:
        """Check if datetime falls within business hours."""
        if not self.is_business_day(dt):
            return False
        local_dt = dt.astimezone(self.timezone)
        return self.business_start <= local_dt.time() <= self.business_end

    def get_business_days(self, start: datetime, end: datetime) -> List[datetime]:
        """Get all business days between start and end dates."""
        days = []
        current = start.replace(hour=9, minute=0, second=0, microsecond=0)
        
        while current <= end:
            if self.is_business_day(current):
                days.append(current)
            current += timedelta(days=1)
        
        return days

    def add_business_days(self, dt: datetime, days: int) -> datetime:
        """Add business days to a datetime."""
        current = dt
        remaining = days
        
        while remaining > 0:
            current += timedelta(days=1)
            if self.is_business_day(current):
                remaining -= 1
        
        return current

    def get_sprint_boundaries(
        self, start: datetime, sprint_length_days: int, num_sprints: int
    ) -> List[Tuple[datetime, datetime]]:
        """Generate sprint start/end dates."""
        sprints = []
        current_start = start
        
        for _ in range(num_sprints):
            # Calculate business days for sprint
            current_end = self.add_business_days(current_start, sprint_length_days - 1)
            sprints.append((current_start, current_end))
            
            # Next sprint starts the next business day
            current_start = self.add_business_days(current_end, 1)
        
        return sprints

    def random_business_time(self, date: datetime, rng) -> datetime:
        """Generate a random time during business hours on a given date."""
        if not self.is_business_day(date):
            raise ValueError("Date must be a business day")
        
        # Random hour between 9 AM and 6 PM
        hour = rng.randint(9, 17)
        minute = rng.randint(0, 59)
        
        return date.replace(hour=hour, minute=minute, second=0, microsecond=0)

    def get_reply_delay(self, rng, is_urgent: bool = False) -> timedelta:
        """Get realistic reply delay based on message urgency."""
        if is_urgent:
            # Urgent: 5 minutes to 2 hours
            minutes = rng.randint(5, 120)
        else:
            # Normal: 30 minutes to 8 hours
            minutes = rng.randint(30, 480)
        
        return timedelta(minutes=minutes)

    def ensure_minimum_gap(self, times: List[datetime], min_gap_minutes: int = 5) -> List[datetime]:
        """Ensure minimum time gap between consecutive events."""
        if len(times) <= 1:
            return times
        
        sorted_times = sorted(times)
        adjusted = [sorted_times[0]]
        
        for i in range(1, len(sorted_times)):
            prev_time = adjusted[-1]
            current_time = sorted_times[i]
            
            min_time = prev_time + timedelta(minutes=min_gap_minutes)
            if current_time < min_time:
                current_time = min_time
            
            adjusted.append(current_time)
        
        return adjusted
