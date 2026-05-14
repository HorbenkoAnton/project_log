# Architecture & Technical Design: Sentinel Log Aggregator

This document describes the internal logic, data structures, and component architecture of the log aggregation system.

## 1. System Overview
The system is a high-performance, containerized pipeline designed to transform unstructured, high-velocity log streams into actionable intelligence. It prioritizes data reduction through pattern-based deduplication and protects the notification layer via adaptive backpressure and intelligent triggering.

## 2. Data Flow & Logical Components

### 2.1. Ingestion Layer (The Producer)
* **Role:** High-load data entry point.
* **Process:**
    * Generates or receives JSON-formatted logs at a peak rate of 1,500+ events per second.
    * Validates schema and maps raw input to a strictly typed `LogEntry` container.

### 2.2. Processing & Aggregation Engine
* **Role:** Data reduction and PII (Personally Identifiable Information) masking.
* **The Regex Masking Hierarchy:** To ensure unique grouping, the engine applies a **Specific-to-Generic** masking strategy:
    1.  **UUIDs:** `[0-9a-fA-F]{8}-...` -> `<UUID>`
    2.  **IP Addresses:** `\\d{1,3}(\\.\\d{1,3}){3}` -> `<IP>`
    3.  **Hex/Memory:** `0x[0-9a-fA-F]+` -> `<HEX>`
    4.  **Integers:** `\\b\\d+\\b` -> `<ID>` (Uses word boundaries to prevent partial corruption).
* **Fingerprinting:** Generates a **Signature Tuple** based on user-defined `SIGNATURE_COMPONENTS` (e.g., `service`, `level`, `masked_message`).
* **Storage:** Maintains an in-memory `Registry` (Dictionary) for $O(1)$ deduplication and tracking.

### 2.3. Notification Controller (The Gatekeeper)
* **Role:** Intelligent alert triggering and anti-spam protection.
* **Hybrid Trigger Logic:**
    * **Routine (Time-based):** Triggers a report if the `NOTIFICATION_COOLDOWN` has elapsed.
    * **Panic (Volume-based):** Triggers immediately if the count of logs since the last send exceeds `NOTIFICATION_MAX_LOGS`.
    * **Suppression:** Blocks reports if the volume is below `NOTIFICATION_MIN_LOGS`.
* **Adaptive Backoff:** If a volume-based trigger occurs, the controller applies an exponential multiplier to the next threshold to prevent email saturation during "Log Storms."

### 2.4. Presentation Layer (Formatter & Reporter)
* **Role:** Human-readable data transformation and delivery.
* **Dynamic Formatting:** The `ReportFormatter` inspects the active signature components and builds a column-aligned table dynamically, responding to configuration changes without code modification.
* **Transport:** The `Reporter` handles the SMTP handshake and dispatches reports via `MIMEMultipart` email.

## 3. Data Structures

### 3.1. Log Entry Structure
Internal representation of a single log:
* `timestamp`: datetime
* `level`: string (ERROR, WARN, INFO, etc.)
* `service`: string (Source service name)
* `message`: string (The raw log text, later sanitized)

### 3.2. Aggregation Map Logic
The core engine stores data in a dictionary where the key is the identifying **Signature Tuple**, ensuring collision-free grouping:

``` python
{
    ('auth-service', 'ERROR', 'Failed login for user <ID>'): {
        "count": 4655,
        "first_seen": "10:30:01",
        "sample": LogEntry_Object  # Maintains representative metadata
    }
}
```
### 4. Technical Implementation Detail
* `Concurrency`: Utilizes asyncio for non-blocking ingestion and run_in_executor for blocking SMTP network tasks.
* `Deployment`: Fully containerized via Docker, isolating environment variables and ensuring consistent Python pathing.