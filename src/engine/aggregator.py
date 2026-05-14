import re
from typing import Dict, Any, Tuple
import config
from src.models.models import LogEntry

class AggregationEngine:
    def __init__(self, mask_ids: bool = True):
        # Key: (service, level, message)
        self.registry: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
        self.total_processed = 0
        self.mask_ids = mask_ids
        self.sig_components = getattr(config, "SIGNATURE_COMPONENTS", ["service", "level", "message"])

        
        self.masks = [
                    # 1. UUID (Most specific: dashes and specific length)
                    (re.compile(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'), '<UUID>'),
                    
                    # 2. IPv4 (Specific: dots and digit clusters)
                    (re.compile(r'\d{1,3}(\.\d{1,3}){3}'), '<IP>'),
                    
                    # 3. Hex codes (Specific: 0x prefix)
                    (re.compile(r'0x[0-9a-fA-F]+'), '<HEX>'),
                    
                    # 4. Integers (Most generic: just numbers)
                    # We use \b to ensure we only catch standalone numbers, not parts of words
                    (re.compile(r'\b\d+\b'), '<ID>')
                ]


    def _create_signature(self, entry: LogEntry) -> Tuple:
        # Use the same config the formatter uses
        active_cols = getattr(config, "SIGNATURE_COMPONENTS", ["service", "level", "message"])
        
        sig_parts = []
        for col in active_cols:
            # Map config string to object attribute
            val = getattr(entry, col, "N/A")
            sig_parts.append(val)
            
        return tuple(sig_parts)

    def _sanitize(self, message: str) -> str:
        """Applies all regex masks to the message string."""
        if not self.mask_ids:
            return message
            
        for pattern, replacement in self.masks:
            message = pattern.sub(replacement, message)
        return message

    def process(self, entry: LogEntry) -> Tuple[str, str, str]:
        clean_msg = self._sanitize(entry.message)
        entry.message = clean_msg
        sig = self._create_signature(entry)

        if sig not in self.registry:
            self.registry[sig] = {
                "count": 1,
                "first_seen": entry.timestamp,
                "sample": entry 
            }
        else:
            self.registry[sig]["count"] += 1
            self.registry[sig]["sample"] = entry 
        self.total_processed += 1
        return sig

    def flush_report(self) -> Dict[Tuple[str, str, str], Dict[str, Any]]:
        report_data = self.registry.copy()
        self.registry.clear()
        return report_data