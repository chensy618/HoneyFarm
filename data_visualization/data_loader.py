# file: data_loader.py
import json
import os
import time
import requests
import pandas as pd

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

def enrich_geo(df, cache_path="./data_visualization/ip_country_cache.json"):
    if "src_ip" not in df.columns:
        return df

    ip_country_map = {}
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            ip_country_map = json.load(f)

    unique_ips = df["src_ip"].dropna().unique()
    for ip in unique_ips:
        if ip not in ip_country_map:
            try:
                r = requests.get(f"http://ip-api.com/json/{ip}?fields=country", timeout=2)
                ip_country_map[ip] = r.json().get("country", "Unknown")
            except:
                ip_country_map[ip] = "Unknown"
            time.sleep(0.4)

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(ip_country_map, f)

    df["geo_country"] = df["src_ip"].map(ip_country_map)
    return df