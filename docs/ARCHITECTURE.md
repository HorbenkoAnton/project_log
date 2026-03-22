# Architecture & Technical Design: project_log

This document describes the internal logic, data structures, and component architecture of the `project_log` system.

## 1. System Overview
The system is designed as a linear processing pipeline. It consumes JSON logs, validates them, aggregates identical entries to prevent redundancy, and dispatches periodic email reports.

## 2. Data Flow & Logical Components
The system consists of four primary modules:

### 2.1. Ingestion & Validation Module
* **Role:** Entry point for raw data.
* **Process:**
    * Receives JSON input (via API or Log File).
    * Validates mandatory fields: `level` and `message`.
    * Maps raw JSON to an internal `LogEntry` data object.

### 2.2. Aggregation & Processing Engine
* **Role:** Deduplication and frequency tracking.
* **Grouping Algorithm:**
    1. Extracts `level`, `message`, and `service`.
    2. Generates a unique `group_id` using a hashing function (e.g., `hashlib.md5`).
    3. Updates an in-memory Dictionary: `{ group_id: Metadata }`.
* **Metadata includes:** Occurrence count, first/last seen timestamps, and a sample message.

### 2.3. Buffer & Queue Manager (Backpressure)
* **Role:** System stability during traffic spikes (e.g., "Black Friday" scenarios).
* **Mechanism:** Uses a fixed-size Circular Buffer (e.g., `collections.deque`).
* **Overflow Policy:** If the buffer is full, the system drops the oldest logs and increments a `dropped_logs_counter` to maintain a constant memory footprint.

### 2.4. Notification & Reporting Service
* **Role:** Communication with the end-user.
* **Anti-Spam Logic:**
    * **Tumbling Window:** Dispatches reports only after a predefined interval (e.g., every 5 minutes).
    * **Rate Limiting:** Enforces a hard cap on total emails sent per hour (e.g., max 12/hour).

## 3. Data Structures (Python-based)

### 3.1. Log Entry Structure
Internal representation of a single log:
* `timestamp`: datetime
* `level`: string (ERROR, WARN, etc.)
* `service`: string (source name)
* `message`: string (main error text)

### 3.2. Aggregation Map Logic
The core engine stores grouped data in a dictionary structure to ensure $O(1)$ lookup time:

```json
{
    "md5_hash_key": {
        "count": 542,
        "first_seen": "2026-03-22 10:00:01",
        "last_seen": "2026-03-22 10:04:59",
        "example_message": "Database connection timeout"
    }
}
```

