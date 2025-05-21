# cowrie/email_alert.py

import smtplib
from email.mime.text import MIMEText
import os

def send_honeytoken_email(filename: str, session: str):
    msg = MIMEText(f"ALERT: The file '{filename}' was accessed by an attacker in session {session}.")
    msg['Subject'] = "Cowrie Honeytoken Alert"
    msg['From'] = os.environ.get("SMTP_FROM")
    msg['To'] = os.environ.get("SMTP_TO")

    try:
        server = smtplib.SMTP(os.environ.get("SMTP_SERVER"), int(os.environ.get("SMTP_PORT", 587)))
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS"))
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
        server.quit()
    except Exception as e:
        print(f"[!] Failed to send honeytoken email: {e}")
