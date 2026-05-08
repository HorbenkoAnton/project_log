from typing import Dict, Any, Tuple
from src.models.models import LogEntry

class AggregationEngine:
    def __init__(self):
        # Key: (service, level, message)
        self.registry: Dict[Tuple[str, str, str], Dict[str, Any]] = {}

    def process(self, entry: LogEntry) -> Tuple[str, str, str]:
        sig = (entry.service, entry.level, entry.message)

        if sig not in self.registry:
            self.registry[sig] = {
                "count": 1,
                "first_seen": entry.timestamp,
                "sample": entry 
            }
        else:
            self.registry[sig]["count"] += 1
            self.registry[sig]["sample"] = entry 
            
        return sig

    def flush_report(self) -> Dict[Tuple[str, str, str], Dict[str, Any]]:
        report_data = self.registry.copy()
        self.registry.clear()
        return report_data