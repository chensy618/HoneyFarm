import smtplib
from email.mime.text import MIMEText
import os
import requests
from datetime import datetime


def get_ip_location(ip):
    def decimal_to_dms(deg):
        degrees = int(deg)
        minutes = abs(deg - degrees) * 60
        return degrees, minutes

    try:
        response = requests.get(
            f"http://ip-api.com/json/{ip}?fields=country,regionName,city,zip,lat,lon,org,query",
            timeout=3
        )
        if response.status_code == 200:
            data = response.json()
            lat = float(data.get("lat"))
            lon = float(data.get("lon"))

            lat_deg, lat_min = decimal_to_dms(lat)
            lon_deg, lon_min = decimal_to_dms(lon)

            lat_dir = 'N' if lat >= 0 else 'S'
            lon_dir = 'E' if lon >= 0 else 'W'

            return f"""\
IP Address: {data.get("query")}
Location:   {data.get("city")}, {data.get("regionName")}, {data.get("country")} {data.get("zip")}
Coordinates: {abs(lat_deg)}°{lat_min:.3f}' {lat_dir}, {abs(lon_deg)}°{lon_min:.3f}' {lon_dir}
ISP/Org:     {data.get("org")}
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

def send_botnet_honeytoken_alert(session: str, src_ip: str, src_port: int | str, command: str, connectors: int, length: int, timestamp: str = None) -> None:
    """
    Triggered when a botnet-like command is detected.
    Uses the same underlying email system as file-based honeytokens.
    """
    timestamp = timestamp or datetime.utcnow().isoformat()
    location_info = get_ip_location(src_ip)

    body = f"""\
ALERT: Botnet-like command detected!

Command:
{command}

Session ID: {session}
Source IP-Port: {src_ip} : {src_port}
Connectors Used: {connectors}
Command Length: {length}
Timestamp (UTC): {timestamp}
{location_info}
"""

    msg = MIMEText(body)
    msg['Subject'] = "Cowrie Botnet Command Alert ⚠️"
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
        print(f"[+] Botnet command alert email sent to {', '.join(to_addrs)} for session {session}")
    except Exception as e:
        print(f"[!] Failed to send botnet alert email: {e}")
