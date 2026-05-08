import os

# --- Ingestion & Buffer ---
BUFFER_SIZE = 10

# --- Producer ---
LOG_INTERVAL = 1

# --- Aggregator ---
REPORTING_INTERVAL = 300 
# Exact Match grouping keys
GROUPING_KEYS = ["service", "level", "message"]
# Levels that trigger an entry in the final report
REPORT_LEVELS = ["ERROR", "WARN"]   