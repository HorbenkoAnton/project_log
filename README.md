# project_log

A lightweight log processing tool designed to ingest JSON logs, aggregate identical errors, and send consolidated email reports while avoiding spam filters.

## 🎯 MVP Scope (Current Focus)
The initial version of the project implements the following core workflow:
1. **JSON Ingestion:** Receiving and validating structured log data.
2. **Exact-Match Grouping:** Identifying and counting identical error messages to reduce redundancy.
3. **Threshold-Based Alerting:** Sending email reports only when specific criteria are met to prevent "alert fatigue" and avoid triggering spam filters.
4. **Email Integration:** Delivering clean, summarized reports via SMTP.

## 📂 Documentation
Detailed technical documentation and future scaling plans:
* [Project Specification (PL)](docs/SPECIFICATION.md) — Requirements and Use Cases.
* [Architecture & Logic](docs/ARCHITECTURE.md) — Internal data flow and grouping algorithms.

## 🛠️ Technical Implementation
* **Format:** Structured JSON logs.
* **Mechanism:** In-memory aggregation window.
* **Output:** Periodic HTML/Text email summaries.

## 🚦 Getting Started
*Status: Documentation & Design Phase.*
