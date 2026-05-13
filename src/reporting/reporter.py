import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
import src.config as config
from collections import defaultdict

class Reporter:
    def __init__(self):
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.username = config.SMTP_USERNAME
        self.password = config.SMTP_PASSWORD
        self.sender_email = config.SENDER_EMAIL
        self.receiver_email = config.RECEIVER_EMAIL

    def format_report(self, report_data: Dict[str, Dict[str, Any]]) -> str:
        # 1. Dynamic Stats Aggregation
        stats = defaultdict(int)
        total_events = 0
        grouped_by_level = defaultdict(list)

        for data in report_data.values():
            lvl = data["sample"].level.upper()
            count = data["count"]
            
            stats[lvl] += count
            total_events += count
            grouped_by_level[lvl].append(data)

        # 2. Header & Stats Sheet
        # Logic: Show common levels first, then any custom "Other" levels found
        common_lvls = ["ERROR", "WARN", "INFO", "DEBUG"]
        other_lvls = [l for l in stats.keys() if l not in common_lvls]
        
        stats_line = " | ".join([f"{l}: {stats[l]}" for l in common_lvls + other_lvls if stats[l] > 0])

        lines = [
            "=== LOG AGGREGATION SUMMARY ===",
            f"Total Events: {total_events}",
            f"Breakdown:    {stats_line}",
            "=" * 40,
            ""
        ]

        # 3. Detail Sheets (Sorted by Severity then Frequency)
        for level in common_lvls + other_lvls:
            if level not in grouped_by_level:
                continue
                
            lines.append(f"[{level} LEVEL DETAILS]")
            
            # Sort by frequency (most frequent first)
            sorted_issues = sorted(grouped_by_level[level], key=lambda x: x["count"], reverse=True)
            
            for item in sorted_issues:
                s = item["sample"]
                lines.append(f" {item['count']:<5} | {s.service:<15} | {s.message}")
            
            lines.append("-" * 40)

        return "\n".join(lines)

    def send_report(self, report_data: Dict[str, Dict[str, Any]]):
        """Orchestrates formatting and SMTP delivery."""
        ##TODO:improve creating report logic
        if not report_data:
            return

        body = self.format_report(report_data)
        
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