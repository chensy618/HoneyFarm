# file: data_loader.py
import json
import os
import time
import requests
import pandas as pd
import geoip2.database
import re
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

    # 清洗
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['path'] = df['path'].fillna("N/A")
    df['msg'] = df['msg'].fillna("")
    df['behavior'] = "unknown"

    return df
