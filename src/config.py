import os

# --- Ingestion & Buffer ---
BUFFER_SIZE = 50000

# --- Aggregation ---
MASK_IDS = True
# Options: "service", "level", "message"
# If "level" is removed, the same message across ERROR and WARN and etc will be grouped together.
SIGNATURE_COMPONENTS = ["service","level" ,"message"]

# --- Notification ---
NOTIFICATION_MIN_THRESHOLD = 1000    # Don't bother me for less than 1000 logs
NOTIFICATION_MAX_THRESHOLD = 50000   # Critical mass: send regardless of timer
NOTIFICATION_COOLDOWN = 300          # Base time between reports

# --- SMTP Config ---
SMTP_SERVER = "sandbox.smtp.mailtrap.io" 
SMTP_PORT = 587
SMTP_USERNAME = "d21784593bab57"
SMTP_PASSWORD = "09447f1699a15a"
SENDER_EMAIL = "sender@example.com"
RECEIVER_EMAIL = "receiver@example.com"