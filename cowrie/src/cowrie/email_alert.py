# # cowrie/email_alert.py

# import smtplib
# from email.mime.text import MIMEText
# import os

# def send_honeytoken_email(filename: str, session: str):
#     msg = MIMEText(f"ALERT: The file '{filename}' was accessed by an attacker in session {session}.")
#     msg['Subject'] = "Cowrie Honeytoken Alert"
#     msg['From'] = os.environ.get("SMTP_FROM")
#     msg['To'] = os.environ.get("SMTP_TO")

#     try:
#         server = smtplib.SMTP(os.environ.get("SMTP_SERVER"), int(os.environ.get("SMTP_PORT", 587)))
#         server.ehlo()
#         server.starttls()
#         server.ehlo()
#         server.login(os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS"))
#         server.sendmail(msg['From'], [msg['To']], msg.as_string())
#         server.quit()
#     except Exception as e:
#         print(f"[!] Failed to send honeytoken email: {e}")


# cowrie/email_alert.py

import smtplib
from email.mime.text import MIMEText
import os
import requests
from datetime import datetime

def get_ip_location(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=country,regionName,city,zip,lat,lon,org,query", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return f"""
IP Address: {data.get("query")}
Location: {data.get("city")}, {data.get("regionName")}, {data.get("country")} {data.get("zip")}
Coordinates: {data.get("lat")}, {data.get("lon")}
ISP/Org: {data.get("org")}
"""
    except Exception as e:
        return f"IP Geolocation failed: {e}"
    return "IP Geolocation unavailable"

def send_honeytoken_email(filename: str, session: str, src_ip: str, src_port: int | str,timestamp: str = None):
    timestamp = timestamp or datetime.utcnow().isoformat()
    location_info = get_ip_location(src_ip)

    body = f"""\
ALERT: Honeytoken file accessed!

Filename: {filename}
Session ID: {session}
Source IP-Port: {src_ip} : {src_port}
Timestamp (UTC): {timestamp}
{location_info}
"""

    msg = MIMEText(body)
    msg['Subject'] = "Cowrie Honeytoken Alert 🚨"
    msg['From'] = os.environ.get("SMTP_FROM")
    msg['To'] = os.environ.get("SMTP_TO")

    try:
        server = smtplib.SMTP(os.environ.get("SMTP_SERVER"), int(os.environ.get("SMTP_PORT", 587)))
        server.starttls()
        server.login(os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS"))
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
        server.quit()
        print(f"[+] Honeytoken alert email sent for {filename}")
    except Exception as e:
        print(f"[!] Failed to send honeytoken email: {e}")
