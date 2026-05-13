import time
import src.config as config

class NotificationController:
    def __init__(self):
        # Tracking the last time an email was successfully sent
        self.last_sent_at = 0
        
        # Anti-spam interval (e.g., 300 seconds / 5 minutes)
        # Pull from config or default to 300
        self.cooldown_period = getattr(config, "NOTIFICATION_COOLDOWN", 300)

    def should_send(self, report_data: dict) -> bool:
        """
        MVP Logic: Check if the cooldown period has passed.
        """
        if not report_data:
            return False

        current_time = time.time()
        time_since_last = current_time - self.last_sent_at

        if time_since_last >= self.cooldown_period:
            return True
        
        return False

    def mark_sent(self):
        """Updates the timestamp after a successful dispatch."""
        self.last_sent_at = time.time()