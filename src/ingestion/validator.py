from typing import Optional, Tuple
from pydantic import ValidationError
from src.core.models import LogEntry

def validate_log(raw_line: str) -> Tuple[Optional[LogEntry], bool]:
    """
    Step 2 & 3: Structural Validation and Transformation.
    
    Returns:
        A Tuple containing (LogEntry object or None, Success boolean).
    """
    try:
        # Pydantic parses JSON and validates schema in one step
        entry = LogEntry.model_validate_json(raw_line)
        return entry, True
        
    except ValidationError:
        # FR-2: Catch missing fields or wrong data types
        #TODO more info in return
        return None, False
        
    except Exception:
        # Catch malformed JSON that isn't even a dictionary
        #TODO more info in return
        return None, False