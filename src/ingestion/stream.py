#Responsible for getting stream of logs


import sys
from typing import Generator

def get_stream() -> Generator[str, None, None]:
    """
    Step 1: Catch logs from the system stream (stdin).
    Yields raw strings to be processed by the validator.
    """
    # PYTHONUNBUFFERED=1 in docker-compose ensures lines arrive in real-time
    try:
        for line in sys.stdin:
            clean_line = line.strip()
            if not clean_line:
                continue
            yield clean_line
    except KeyboardInterrupt:
        # Graceful exit for local testing
        sys.exit(0)
    except Exception as e:
        # Minimalist error handling for the transport layer
        sys.stderr.write(f"Stream Error: {e}\n")
        #TODO Once an exception is caught, the generator is "exhausted." It cannot resume even if the stream recovers.
        yield from []