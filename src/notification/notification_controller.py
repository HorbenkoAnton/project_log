import time
import src.config as config

class NotificationController:
    def __init__(self):
        self.last_sent_at = 0
        self.last_sent_count = 0
        
        # Adaptive state
        self.backoff_multiplier = 1.0
        
        # Config values
        self.min_logs = getattr(config, "NOTIFICATION_MIN_LOGS", 1000)
        self.max_logs = getattr(config, "NOTIFICATION_MAX_LOGS", 50000)
        self.cooldown = getattr(config, "NOTIFICATION_COOLDOWN", 300)

    def check_trigger(self, total_processed: int, registry_size: int):
        """
        Returns (bool, str): (Should send, Trigger type)
        """
        if registry_size == 0:
            return False, None

        now = time.time()
        elapsed = now - self.last_sent_at
        delta_logs = total_processed - self.last_sent_count

        # 1. Suppression: Not enough data yet
        if delta_logs < self.min_logs:
            return False, None

        # 2. Panic Trigger: Hit maximum threshold (with backoff)
        current_max = self.max_logs * self.backoff_multiplier
        if delta_logs >= current_max:
            return True, "MAX"

        # 3. Routine Trigger: Cooldown elapsed
        if elapsed >= self.cooldown:
            return True, "TIME"

        return False, None

    def mark_sent(self, total_processed: int, trigger_type: str):
        self.last_sent_at = time.time()
        self.last_sent_count = total_processed
        
        if trigger_type == "MAX":
            # Increase backoff to slow down repeated panic alerts
            self.backoff_multiplier = min(self.backoff_multiplier * 2, 16.0)
        else:
            # Reset backoff on routine/timed successful sends
            self.backoff_multiplier = 1.0