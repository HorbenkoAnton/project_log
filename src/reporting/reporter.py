import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
import src.config as config
from reporting.report_formatter import ReportFormatter


class Reporter:
    def __init__(self):
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.username = config.SMTP_USERNAME
        self.password = config.SMTP_PASSWORD
        self.sender_email = config.SENDER_EMAIL
        self.receiver_email = config.RECEIVER_EMAIL
        self.formatter = ReportFormatter()


    def send_report(self, report_data: Dict[str, Dict[str, Any]]):
        """Orchestrates formatting and SMTP delivery."""
        if not report_data:
            return

        body = self.formatter.build_text_report(report_data)
        
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = self.receiver_email
        msg['Subject'] = f"Log Alert: {len(report_data)} Unique Issues Detected"
        
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(self.username, self.password)
                server.send_message(msg)
            print(f"--- Reporter: Email sent to {self.receiver_email} ---", flush=True)
        except Exception as e:
            print(f"--- Reporter Error: Failed to send email: {e} ---", flush=True)