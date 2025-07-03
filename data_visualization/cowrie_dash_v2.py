import json
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table
from wordcloud import WordCloud
import base64
import os
import requests
import time

# ========== Step 1: Load Cowrie Logs ==========
LOG_FILE = "./data_visualization/cowrie.json.2025-06-27"
df = []

with open(LOG_FILE, "r", encoding="utf-8") as f:
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

# ========== Step 2: Preprocessing ==========
df["hour"] = df["timestamp"].dt.floor("h")

# Field check
has_ip = "src_ip" in df.columns
user_col = "username" if "username" in df.columns else "user" if "user" in df.columns else None
has_user = user_col is not None

# Login statistics
total_attempts = len(df)
success_attempts = df["message"].str.contains("login attempt .* succeeded", case=False, na=False).sum()

# Command frequency statistics
top_cmds = df["input"].dropna().value_counts().reset_index()
top_cmds.columns = ["command", "count"]
fig_cmds = px.bar(
    top_cmds.head(15),
    x="count",
    y="command",
    orientation='h',
    title="Top 15 Most Used Commands"
)
fig_cmds.update_layout(height=400, margin=dict(l=100, r=20, t=40, b=20))

# Attack stage classification
stage_keywords = {
    "Reconnaissance": ["uname", "whoami", "id", "ps", "netstat", "ifconfig", "ls", "pwd"],
    "Execution": ["sh", "bash", "chmod", "./", "perl", "python", "./script"],
    "Credential Access": ["cat /etc/passwd", "history"],
    "Initial Access": ["wget", "curl", "scp"],
    "Defense Evasion": ["rm", "clear", "unset", "echo"]
}

def classify_stage(cmd):
    for stage, keywords in stage_keywords.items():
        for kw in keywords:
            if kw in cmd:
                return stage
    return "Other"

if "input" in df.columns:
    df["attack_stage"] = df["input"].fillna("").apply(classify_stage)
    stage_counts = df["attack_stage"].value_counts().reset_index()
    stage_counts.columns = ["stage", "count"]
    fig_stage = px.bar(stage_counts, x="stage", y="count", title="Attack Behavior Stage Distribution")
else:
    fig_stage = {}

# ========== Step 2.1: Geo Country Lookup ==========
geo_cache_path = "./data_visualization/ip_country_cache.json"
ip_country_map = {}

if os.path.exists(geo_cache_path):
    with open(geo_cache_path, "r", encoding="utf-8") as f:
        ip_country_map = json.load(f)

if has_ip:
    unique_ips = df["src_ip"].dropna().unique()
    for ip in unique_ips:
        if ip not in ip_country_map:
            try:
                response = requests.get(f"http://ip-api.com/json/{ip}?fields=country", timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    ip_country_map[ip] = data.get("country", "Unknown")
                else:
                    ip_country_map[ip] = "Unknown"
            except:
                ip_country_map[ip] = "Unknown"
            time.sleep(0.5)  # Avoid hitting free API rate limit

    with open(geo_cache_path, "w", encoding="utf-8") as f:
        json.dump(ip_country_map, f)

    df["geo_country"] = df["src_ip"].map(ip_country_map)

# ========== Step 3: Visualization ==========
if has_ip:
    top_ips = df["src_ip"].value_counts().head(20).reset_index()
    top_ips.columns = ["src_ip", "count"]
    fig_ip = px.pie(top_ips, names="src_ip", values="count", title="Top 20 Attacker IPs")
else:
    fig_ip = {}

if has_user:
    top_users = df[user_col].value_counts().head(20).reset_index()
    top_users.columns = ["username", "count"]
    fig_user = px.pie(top_users, names="username", values="count", title="Top 20 Attempted Users")
else:
    fig_user = {}

# Latest commands table
cmd_table = dash_table.DataTable(
    columns=[{"name": i, "id": i} for i in ["timestamp", "session", "input"] if i in df.columns],
    data=df[["timestamp", "session", "input"]].to_dict("records"),
    style_table={"maxHeight": "400px", "overflowY": "auto", "overflowX": "auto"},
    style_cell={"textAlign": "left", "padding": "6px", "whiteSpace": "pre-line", "maxWidth": "400px"},
    style_header={"fontWeight": "bold", "backgroundColor": "#f9f9f9"},
    page_action="none",
    fixed_rows={"headers": True}
)

# Country of origin word cloud
if "geo_country" in df.columns:
    country_counts = df["geo_country"].value_counts().to_dict()
    wordcloud = WordCloud(width=400, height=250, background_color="white").generate_from_frequencies(country_counts)
    wordcloud_path = "wordcloud.png"
    wordcloud.to_file(wordcloud_path)
    encoded = base64.b64encode(open(wordcloud_path, "rb").read()).decode()
    wordcloud_img = html.Img(
        src=f"data:image/png;base64,{encoded}",
        style={"maxWidth": "600px", "maxHeight": "300px", "display": "block", "margin": "0 auto"}
    )
    os.remove(wordcloud_path)
else:
    wordcloud_img = html.Div("No geo_country data found for word cloud.")

# ========== Step 4: Build Dashboard ==========
app = Dash(__name__)
app.title = "Honeyfarm Dashboard"

app.layout = html.Div([
    html.H1("Honeyfarm Dashboard", style={"textAlign": "center", "color": "#2c3e50", "margin": "30px"}),

    html.Div([
        html.Div([
            html.H4("Total Login Attempts"),
            html.H2(f"{total_attempts}", style={"color": "#34495e"})
        ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

        html.Div([
            html.H4("Successful Logins (message based)"),
            html.H2(f"{success_attempts}", style={"color": "#27ae60"})
        ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

    ], style={"textAlign": "center"}),

    html.Div([
        html.Div([
            html.H3("Latest Commands Executed"),
            html.Div(cmd_table, style={"overflowY": "auto"})
        ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top"}),

        html.Div([
            html.H3("Attack Stage Distribution"),
            html.Div(dcc.Graph(figure=fig_stage), style={"maxHeight": "400px", "overflowY": "auto", "overflowX": "hidden"})
        ], style={"width": "48%", "display": "inline-block", "float": "right", "verticalAlign": "top"})
    ], style={"padding": "40px 5%", "display": "flex", "justifyContent": "space-between"}),

    html.Div([
        html.Div([
            html.H3("Top 20 Attacker IPs"),
            dcc.Graph(figure=fig_ip)
        ], style={"width": "48%", "display": "inline-block"}),

        html.Div([
            html.H3("Top 20 Attempted Users"),
            dcc.Graph(figure=fig_user)
        ], style={"width": "48%", "display": "inline-block", "float": "right"})
    ], style={"padding": "20px 5%"}),

    html.Div([
        html.Div([
            html.H3("Top Source Countries (Word Cloud)"),
            wordcloud_img
        ], style={"width": "48%", "display": "inline-block"}),

        html.Div([
            html.H3("Top 15 Most Used Commands"),
            dcc.Graph(figure=fig_cmds, style={"maxHeight": "400px", "overflowY": "auto"})
        ], style={"width": "48%", "display": "inline-block", "float": "right"})
    ], style={"padding": "20px 5%", "display": "flex", "justifyContent": "space-between"})

], style={"fontFamily": "Arial, sans-serif"})

# ========== Run Server ==========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
