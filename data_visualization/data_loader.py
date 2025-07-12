# file: data_loader.py
import json
import os
import time
import requests
import pandas as pd
import geoip2.database
import re
import ast
from datetime import datetime

def load_and_process_log(filepath):
    df = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            try:
                log = json.loads(line)
                if "timestamp" in log:
                    df.append(log)
            except:
                continue

    df = pd.DataFrame(df)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df = df.sort_values("timestamp", ascending=False)
    df["hour"] = df["timestamp"].dt.floor("h")
    return df

def load_logs_bulk(log_dir):
    """
    Load all Cowrie logs from a directory and return as a combined DataFrame.
    """
    logs = []
    for filename in os.listdir(log_dir):
        if filename.startswith("cowrie.json"):
            filepath = os.path.join(log_dir, filename)
            with open(filepath, "r") as f:
                lines = f.readlines()
                for line in lines:
                    try:
                        logs.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
    return pd.DataFrame(logs)

GEOIP_DB_PATH = "./data_visualization/GeoLite2-City.mmdb"

def enrich_geo(df):
    reader = geoip2.database.Reader(GEOIP_DB_PATH)

    def lookup(ip):
        try:
            res = reader.city(ip)
            lat = res.location.latitude
            lon = res.location.longitude
            country = res.country.name
            # print(f"[GEO] {ip} → {lat}, {lon} ({country})")
            return lat, lon, country
        except Exception as e:
            print(f"[GEO FAIL] {ip}: {e}")
            return None, None, None

    df["src_ip"] = df["src_ip"].astype(str)

    ip_series = (
        df["src_ip"]
        .dropna()
        .drop_duplicates()
        .astype(str)
    )
    ip_series = ip_series[~ip_series.str.lower().isin(["", "none", "nan"])]

    geo_df = pd.DataFrame(
        ip_series.apply(lookup).tolist(), 
        index=ip_series.values, 
        columns=["latitude", "longitude", "country"]
    )
    geo_df.index.name = "src_ip"

    df = df.merge(geo_df, how="left", left_on="src_ip", right_index=True)

    return df


# This function is used to fetch data from miniprint log
def load_miniprint_file(filepath: str) -> pd.DataFrame:
    logs = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if "timestamp" in entry:
                    logs.append(entry)
            except json.JSONDecodeError:
                continue

    df = pd.DataFrame(logs)

    # identify src_ip field
    if "src_ip" not in df.columns:
        if "src" in df.columns:
            df["src_ip"] = df["src"]
        elif "peerIP" in df.columns:
            df["src_ip"] = df["peerIP"]
        elif "ip" in df.columns:
            df["src_ip"] = df["ip"]
        else:
            df["src_ip"] = None

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df = df.sort_values("timestamp", ascending=False)
    df["hour"] = df["timestamp"].dt.floor("h")

    return df

# This function is used to fetch data from snare.err
def load_snare_err_data(log_path: str) -> pd.DataFrame:
    """
    Parses the snare.err log into a structured DataFrame.
    Each row includes timestamp, method, path, IP, port, status.
    """
    log_data = []
    pattern = re.compile(
        r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
        r"ERROR:snare\.tanner_handler:submit_data: .*?url=URL\('(?P<url>[^']+)'\) (?P<json_data>\{.*\})$"
    )

    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                match = pattern.match(line.strip())
                if match:
                    ts = match.group("timestamp")
                    json_str = match.group("json_data")
                    try:
                        parsed_json = eval(json_str)
                        log_data.append({
                            "timestamp": pd.to_datetime(ts),
                            "url": match.group("url"),
                            "method": parsed_json.get("method"),
                            "path": parsed_json.get("path"),
                            "ip": parsed_json.get("peer", {}).get("ip"),
                            "port": parsed_json.get("peer", {}).get("port"),
                            "status": parsed_json.get("status"),
                        })
                    except Exception:
                        continue
    except FileNotFoundError:
        print(f"Log file not found: {log_path}")
        return pd.DataFrame()

    return pd.DataFrame(log_data)
    
# This function is used to fetch data from snare.log

def load_snare_log_data(filepath):
    base_pattern = re.compile(
        r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) '
        r'(?P<level>\w+):(?P<source>[\w\.]+):(?P<method>\w+)[: ]+'
        r'(?:Request path: (?P<path>\S+)|(?P<msg>.+))'
    )

    aiohttp_extra_pattern = re.compile(
        r'"(?P<http_method>[A-Z]+) (?P<http_path>/[^ ]*) HTTP/(?P<http_version>[^"]+)" '
        r'(?P<status_code>\d{3}) (?P<response_size>\d+) "(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )

    records = []

    with open(filepath, 'r') as file:
        for line in file:
            match = base_pattern.search(line)
            if not match:
                continue

            data = match.groupdict()

            # 提取 IP
            ip_match = re.search(r'(\d{1,3}(?:\.\d{1,3}){3})', line)
            data['src_ip'] = ip_match.group(1) if ip_match else None

            # 针对 snare.server:handle_request 的情况：构造 msg 为 Request path: xxx
            if data['source'] == 'snare.server' and data['method'] == 'handle_request' and data.get('path'):
                data['msg'] = f"Request path: {data['path']}"

            # 提取 aiohttp.access 的额外字段
            if data['source'] == 'aiohttp.access' and data['msg']:
                extra = aiohttp_extra_pattern.search(data['msg'])
                if extra:
                    extra_data = extra.groupdict()
                    data['path'] = extra_data.get('http_path') or data.get('path')
                    data['status_code'] = extra_data.get('status_code')
                    data['http_method'] = extra_data.get('http_method')
                    data['user_agent'] = extra_data.get('user_agent')
                else:
                    data['status_code'] = None
                    data['http_method'] = None
                    data['user_agent'] = None
            else:
                data['status_code'] = None
                data['http_method'] = None
                data['user_agent'] = None

            records.append(data)

    df = pd.DataFrame(records)

    # build dataframe
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['path'] = df['path'].fillna("N/A")
    df['msg'] = df['msg'].fillna("")
    df['behavior'] = "unknown"

    return df



# This function is used to fetch data from tanner.log
def load_tanner_log_data(filepath: str) -> pd.DataFrame:
    """
    Parses tanner.log with 3-line pattern:
    1. Access log line with timestamp, IP, status
    2. Path line with requested path
    3. TANNER response line with sess_uuid and detection
    """
    records = []
    with open(filepath, 'r') as file:
        lines = file.readlines()

    current = {}
    for line in lines:
        line = line.strip()

        # Line 1: Access Log
        match_access = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) INFO:aiohttp\.access:log: (\d+\.\d+\.\d+\.\d+).*?"\w+ .*?" (\d{3})', line)
        if match_access:
            current = {
                "timestamp": match_access.group(1),
                "src_ip": match_access.group(2),
                "status": int(match_access.group(3))
            }
            continue

        # Line 2: Path
        match_path = re.search(r"Requested path (.+)", line)
        if match_path and current:
            current["path"] = match_path.group(1)
            continue

        # Line 3: JSON Response
        match_resp = re.search(r"TANNER response (.+)", line)
        if match_resp and current:
            try:
                response_dict = ast.literal_eval(match_resp.group(1))
                message = response_dict.get("response", {}).get("message", {})
                detection = message.get("detection", {})
                current["uuid"] = message.get("sess_uuid", None)
                current["detection_name"] = detection.get("name", None)
                current["detection_type"] = detection.get("type", None)
            except Exception as e:
                current["uuid"] = None
                current["detection_name"] = None
                current["detection_type"] = None

            records.append(current)
            current = {}  # Reset for next record

    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df


def extract_error_type_from_message(message: str) -> str:
    """
    from traceback get Error, such as PermissionError
    """
    lines = message.strip().splitlines()
    for line in reversed(lines):
        match = re.match(r"^\s*(\w+Error):", line)
        if match:
            return match.group(1)
    return "Unknown"

def load_tanner_err_data(filepath: str) -> pd.DataFrame:
    """
    Load tanner.err logs as plain text DataFrame,
    extracting timestamp, level, source, function, message,
    file info and error type.
    """
    records = []
    with open(filepath, 'r') as file:
        for line in file:
            match = re.match(
                r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (?P<level>\w+):(?P<source>[^:]+):(?P<function>[^:]+): (?P<message>.*)",
                line.strip()
            )
            if match:
                data = match.groupdict()

                # extract file and line number from traceback if present
                fileline = re.search(r'File "(.+?)", line (\d+)', data["message"])
                if fileline:
                    data["file"] = fileline.group(1)
                    data["line"] = int(fileline.group(2))
                else:
                    data["file"] = None
                    data["line"] = None

                # extract error type (e.g., PermissionError)
                data["error_type"] = extract_error_type_from_message(data["message"])

                records.append(data)

    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df