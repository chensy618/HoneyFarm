import json
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
import os

# ========== Step 1: Load Cowrie Logs ==========
LOG_FILE = "cowrie.json" 
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

# 字段判断
has_ip = "src_ip" in df.columns
user_col = "username" if "username" in df.columns else "user" if "user" in df.columns else None
has_user = user_col is not None

# 登录统计
total_attempts = len(df)
success_attempts = df["input"].str.contains("sh|shell|bash|enable|sudo", case=False, na=False).sum()

# Top 20 Attacker IPs
if has_ip:
    top_ips = df["src_ip"].value_counts().head(20).reset_index()
    top_ips.columns = ["src_ip", "count"]
    fig_ip = px.pie(top_ips, names="src_ip", values="count", title="Top 20 Attacker IPs")
else:
    fig_ip = {}

# Top 20 Attempted Users
if has_user:
    top_users = df[user_col].value_counts().head(20).reset_index()
    top_users.columns = ["username", "count"]
    fig_user = px.pie(top_users, names="username", values="count", title="Top 20 Attempted Users")
else:
    fig_user = {}

# 最新命令表格
cmd_table = dash_table.DataTable(
    columns=[{"name": i, "id": i} for i in ["timestamp", "session", "input"] if i in df.columns],
    data=df[["timestamp", "session", "input"]].head(15).to_dict("records"),
    style_table={"overflowX": "auto"},
    style_cell={"textAlign": "left", "padding": "6px"},
    page_size=15,
)

# 来源国家词云（如果有 geo_country 字段）
if "geo_country" in df.columns:
    country_counts = df["geo_country"].value_counts().to_dict()
    wordcloud = WordCloud(width=600, height=400, background_color="white").generate_from_frequencies(country_counts)
    wordcloud_path = "wordcloud.png"
    wordcloud.to_file(wordcloud_path)

    encoded = base64.b64encode(open(wordcloud_path, "rb").read()).decode()
    wordcloud_img = html.Img(src=f"data:image/png;base64,{encoded}", style={"width": "100%"})
    os.remove(wordcloud_path)
else:
    wordcloud_img = html.Div("No geo_country data found for word cloud.")

# ========== Step 3: Build Dashboard ==========
app = Dash(__name__)
app.title = "Cowrie Honeypot Dashboard"

app.layout = html.Div([
    html.H1("Cowrie Honeypot Dashboard", style={"textAlign": "center", "color": "#2c3e50", "margin": "30px"}),

    html.Div([
        html.Div([
            html.H4("Total Login Attempts"),
            html.H1(f"{total_attempts}", style={"color": "#34495e"})
        ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

        html.Div([
            html.H4("Successful Login Attempts"),
            html.H1(f"{success_attempts}", style={"color": "#27ae60"})
        ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),
    ], style={"textAlign": "center"}),

    html.Div([
        html.H3("Latest Commands Executed"),
        cmd_table
    ], style={"padding": "40px 5%"}),

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
        html.H3("Top Source Countries (Word Cloud)"),
        wordcloud_img
    ], style={"padding": "20px 5%"})
], style={"fontFamily": "Arial, sans-serif"})

# ========== Run Server ==========
if __name__ == "__main__":
    app.run(debug=True)
