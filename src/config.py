import os

# --- Ingestion & Buffer ---
BUFFER_SIZE = 1000

# --- Aggregation ---
GROUPING_KEYS = ["service", "level", "message"]
REPORT_LEVELS = ["ERROR", "WARN"]

# --- Notification ---
NOTIFICATION_COOLDOWN = 300

# --- SMTP Config ---
SMTP_SERVER = "sandbox.smtp.mailtrap.io" 
SMTP_PORT = 587
SMTP_USERNAME = "d21784593bab57"
SMTP_PASSWORD = "09447f1699a15a"
SENDER_EMAIL = "sender@example.com"
RECEIVER_EMAIL = "receiver@example.com"