from datetime import datetime

class TimeFilter:
    # Day Constants (Monday=0 ... Sunday=6)
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    def is_trading_allowed(self, current_time: datetime | str) -> tuple[bool, str]:
        """
        Validates if trading is allowed based on the Weekend Skill Rule.
        """
        dt = self._parse_time(current_time)
        if not dt:
             return True, "Time format error (Default Open)"

        day = dt.weekday()
        hour = dt.hour
        
        # Guard Clause: Always closed on Saturday
        if day == self.SATURDAY:
            return False, "Weekend (Saturday)"

        # Guard Clause: Sunday Pre-Open logic (< 22:00 UTC)
        if day == self.SUNDAY and hour < 22:
             return False, "Weekend (Sunday Pre-Open)"
             
        # Guard Clause: Friday Post-Close logic (>= 21:00 UTC)
        if day == self.FRIDAY and hour >= 21:
            return False, "Weekend (Friday Post-Close)"
            
        return True, "Market Open"

    def _parse_time(self, time_input: datetime | str) -> datetime | None:
        """Helper to safely parse datetime input."""
        if isinstance(time_input, datetime):
            return time_input
        try:
            return datetime.fromisoformat(str(time_input))
        except (ValueError, TypeError):
            return None

class NewsFilter:
    def is_news_safe(self, timestamp):
        # Placeholder for future News API integration
        return True, "No High Impact News (Placeholder)"
