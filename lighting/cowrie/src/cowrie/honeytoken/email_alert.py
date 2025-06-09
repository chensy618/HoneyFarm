# cowrie/email_alert.py

import smtplib
from email.mime.text import MIMEText
import os
import requests
from datetime import datetime


def get_ip_location(ip):
    try:
        response = requests.get(
            f"http://ip-api.com/json/{ip}?fields=country,regionName,city,zip,lat,lon,org,query",
            timeout=3
        )
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


def send_honeytoken_email(filename: str, session: str, src_ip: str, src_port: int | str, timestamp: str = None):
    timestamp = timestamp or datetime.utcnow().isoformat()
    location_info = get_ip_location(src_ip)

    body = f"""\
ALERT: Honeytoken file accessed!

File Location: {filename}
Session ID: {session}
Source IP-Port: {src_ip} : {src_port}
Timestamp (UTC): {timestamp}
{location_info}
"""

    msg = MIMEText(body)
    msg['Subject'] = "Cowrie Honeytoken Alert 🚨"
    msg['From'] = os.environ.get("SMTP_FROM", "cowrie@honeypot.local")

    # support multiple recipients
    raw_to = os.environ.get("SMTP_TO", "")
    to_addrs = [addr.strip() for addr in raw_to.replace("\n", ",").split(",") if addr.strip()]
    msg['To'] = ", ".join(to_addrs)

    if not to_addrs:
        print("[!] No valid recipient email addresses configured.")
        return

    try:
        server = smtplib.SMTP(os.environ.get("SMTP_SERVER", "localhost"), int(os.environ.get("SMTP_PORT", 587)))
        server.starttls()
        server.login(os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS"))
        server.sendmail(msg['From'], to_addrs, msg.as_string())
        server.quit()
        print(f"[+] Honeytoken alert email sent to {', '.join(to_addrs)} for {filename}")
    except Exception as e:
        print(f"[!] Failed to send honeytoken email: {e}")
