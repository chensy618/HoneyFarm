# file: data_loader.py
import json
import os
import time
import requests
import pandas as pd
import geoip2.database

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