# file: components.py
import base64
import os
from dash import html, dash_table
from wordcloud import WordCloud
import plotly.express as px

def top_command_bar(df):
    cmds = df["input"].dropna().value_counts().reset_index()
    cmds.columns = ["command", "count"]
    return px.bar(cmds.head(15), x="count", y="command", orientation='h', title="Top 15 Commands")

def top_ip_pie(df):
    if "src_ip" not in df.columns: return None
    ip_count = df["src_ip"].value_counts().head(20).reset_index()
    ip_count.columns = ["src_ip", "count"]
    return px.pie(ip_count, names="src_ip", values="count", title="Top 20 Attacker IPs")

def top_user_pie(df):
    user_col = "username" if "username" in df.columns else "user" if "user" in df.columns else None
    if not user_col: return None
    user_count = df[user_col].value_counts().head(20).reset_index()
    user_count.columns = ["username", "count"]
    return px.pie(user_count, names="username", values="count", title="Top 20 Attempted Users")

def wordcloud_img(df):
    if "geo_country" not in df.columns: return html.Div("No geo data")
    country_counts = df["geo_country"].value_counts().to_dict()
    wc = WordCloud(width=400, height=250, background_color="white").generate_from_frequencies(country_counts)
    path = "tmp_wc.png"
    wc.to_file(path)
    img = base64.b64encode(open(path, "rb").read()).decode()
    os.remove(path)
    return html.Img(src=f"data:image/png;base64,{img}", style={"width": "100%"})

def latest_commands_table(df):
    if not {"timestamp", "session", "input"}.issubset(df.columns):
        return html.Div("No command data found.")
    return dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in ["timestamp", "session", "input"]],
        data=df[["timestamp", "session", "input"]].to_dict("records"),
        style_table={"maxHeight": "400px", "overflowY": "auto"},
        style_cell={"textAlign": "left", "whiteSpace": "pre-line", "maxWidth": "400px"},
        style_header={"fontWeight": "bold"},
        page_action="none",
        fixed_rows={"headers": True}
    )
