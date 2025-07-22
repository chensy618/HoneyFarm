# file: components.py
import base64
import os
import re
import json
from dash import html, dash_table
from wordcloud import WordCloud
import plotly.express as px
from dash import dcc
import plotly.graph_objects as go
import pandas as pd
import pingouin as pg
import scipy.stats as stats
import statsmodels.api as sm
import numpy as np
from collections import Counter, defaultdict

# COWRIE !!!!!

def top_command_bar(df):
    cmds = df["input"].dropna().value_counts().reset_index()
    cmds.columns = ["command", "count"]

    # optionally truncate long commands for display:
    cmds["command_short"] = cmds["command"].apply(lambda x: x if len(x) < 50 else x[:47] + "...")

    fig = px.bar(
        cmds.head(15),
        x="count",
        y="command_short",
        orientation='h',
        title="Top 15 Commands",
        text="count"
    )

    fig.update_layout(
        yaxis_title="Command",
        xaxis_title="Count",
        xaxis=dict(
        range=[0, cmds['count'].max() * 1.3]),
        margin=dict(l=250, r=80, t=50, b=50),  
        yaxis=dict(autorange="reversed"),
    )

    fig.update_traces(
        textposition="outside",
        marker_color="cornflowerblue"
    )

    return fig


"""

def personality_traits_bar(log_file):
    trait_pattern = re.compile(r"Top-1 Trait Label\s*:\s*(.+)")

    big_five_traits = [
        "Openness to Experience",
        "Conscientiousness",
        "Low Extraversion",
        "Low Agreeableness",
        "Low Neuroticism"
    ]

    trait_counts = Counter({trait: 0 for trait in big_five_traits})

    # def_message
    warning_msg = None

    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("{"):
                    try:
                        entry = json.loads(line)
                        msg = entry.get("log", "")
                    except:
                        continue
                else:
                    msg = line

                match = trait_pattern.search(msg)
                if match:
                    label = match.group(1).strip()
                    if label in trait_counts:
                        trait_counts[label] += 1

        if sum(trait_counts.values()) == 0:
            warning_msg = "No personality trait data found in logs."
    else:
        warning_msg = "No personality trait data found in logs."

    df = pd.DataFrame(
        sorted(trait_counts.items(), key=lambda x: x[1]),
        columns=["Trait", "Count"]
    )

    fig = px.bar(
        df,
        x="Count",
        y="Trait",
        orientation="h",
        text="Count",
        color_discrete_sequence=["#1f77b4"],
        title="Top Attacker Personality Traits"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
        margin=dict(l=120, r=50, t=50, b=50),
        height=400
    )

    children = []
    if warning_msg:
        children.append(html.Div(
            warning_msg,
            style={"color": "red", "fontWeight": "bold", "marginBottom": "10px"}
        ))

    children.append(dcc.Graph(figure=fig))

    return html.Div(children)
    """


def top_ip_pie(df):
    if "src_ip" not in df.columns:
        return html.Div("No attacker IP data.")

    ip_count = df["src_ip"].value_counts().head(10).reset_index()
    ip_count.columns = ["src_ip", "count"]

    fig = px.pie(
        ip_count,
        names="src_ip",
        values="count",
        title="Top 10 Attacker IPs"
    )

    # Rotate so the biggest slice is not on top
    fig.update_traces(
        sort=False,
        rotation=90,   # or tweak to 180, 270 etc
        textposition="inside",
        textinfo="percent+label"
    )

    fig.update_layout(
        margin=dict(t=60, b=60, l=40, r=40)
    )

    return fig


def top_user_pie(df):
    user_col = "username" if "username" in df.columns else "user" if "user" in df.columns else None
    if not user_col:
        return html.Div("No attempted user data.")

    user_count = df[user_col].value_counts().head(10).reset_index()
    user_count.columns = ["username", "count"]

    fig = px.pie(
        user_count,
        names="username",
        values="count",
        title="Top 10 Attempted Users",
        hole=0.0
    )

    # rotate the pie so the biggest slice starts at the side instead of top
    fig.update_traces(
        sort=False,
        rotation=90,   
        textposition="inside",
        textinfo="percent+label"
    )

    fig.update_layout(
        margin=dict(t=60, b=60, l=40, r=40)
    )

    return fig

def wordcloud_img(df):
    if "geo_country" not in df.columns:
        return html.Div("No geo data.")
    country_counts = df["geo_country"].value_counts().to_dict()
    if not country_counts:
        return html.Div("No geo data available.")
    wc = WordCloud(width=400, height=250, background_color="white").generate_from_frequencies(country_counts)
    path = "tmp_wc.png"
    wc.to_file(path)
    img = base64.b64encode(open(path, "rb").read()).decode()
    os.remove(path)
    return html.Img(src=f"data:image/png;base64,{img}", style={"width": "100%"})

def ip_duration_table(df):
    #build a table with source IP and duration spent on honeypot.   
    if not {"session", "eventid", "timestamp"}.issubset(df.columns):
        return html.Div("Required columns missing.")

    # Filter for connect and closed events
    connect_df = df[df["eventid"] == "cowrie.session.connect"].copy()
    closed_df = df[df["eventid"] == "cowrie.session.closed"].copy()

    # merge on session
    merged = pd.merge(
        connect_df[["session", "src_ip", "timestamp"]],
        closed_df[["session", "timestamp"]],
        on="session",
        suffixes=("_start", "_end")
    )

    # calculate duration in seconds
    merged["duration_sec"] = (
        pd.to_datetime(merged["timestamp_end"]) - pd.to_datetime(merged["timestamp_start"])
    ).dt.total_seconds().round(1)

    merged.rename(columns={"src_ip": "IP Address"}, inplace=True)
    merged = merged[["IP Address", "duration_sec"]].copy()
    merged.columns = ["IP Address", "Duration (seconds)"]

    merged.sort_values(by="Duration (seconds)", ascending=False, inplace=True)

    return dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in merged.columns],
        data=merged.to_dict("records"),
        style_cell={"textAlign": "left", "padding": "5px"},
        style_header={"fontWeight": "bold", "backgroundColor": "#f8f8f8"},
        style_table={"overflowX": "auto"},
        page_size=15
    )

def top_10_duration_ips_table(df):
    
    #ips that spent the most time on the honeypot.
    
    if not {"session", "eventid", "timestamp", "src_ip"}.issubset(df.columns):
        return html.Div("Required columns missing for duration analysis.")

    connect_df = df[df["eventid"] == "cowrie.session.connect"].copy()
    closed_df = df[df["eventid"] == "cowrie.session.closed"].copy()
    
    merged = pd.merge(
        connect_df[["session", "src_ip", "timestamp"]],
        closed_df[["session", "timestamp"]],
        on="session",
        suffixes=("_start", "_end")
    )

    # duration per session
    merged["duration_sec"] = (
        pd.to_datetime(merged["timestamp_end"]) - pd.to_datetime(merged["timestamp_start"])
    ).dt.total_seconds()

    # group IP and sum durations
    grouped = (
        merged.groupby("src_ip")["duration_sec"]
        .sum()
        .reset_index()
        .sort_values("duration_sec", ascending=False)
        .head(10)
    )

    grouped["duration_sec"] = grouped["duration_sec"].round(1)
    grouped.columns = ["IP Address", "Total Duration (seconds)"]

    return html.Div([
        dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in grouped.columns],
            data=grouped.to_dict("records"),
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "5px"},
            style_header={"fontWeight": "bold", "backgroundColor": "#f8f8f8"},
            page_size=10
        )
    ], style={"padding": "20px 5%"})

def latest_commands_table(df):
    #table for executed commands    
    required_cols = {"timestamp", "session", "input"}
    if not required_cols.issubset(df.columns):
        return html.Div("No command data found.")

    # If 'src_ip' already exists, use it, else infer it
    if "src_ip" not in df.columns and "eventid" in df.columns:
        # Fill missing IPs by mapping session connect events
        session_ip_map = (
            df[df["eventid"] == "cowrie.session.connect"]
            .groupby("session")["src_ip"]
            .first()
            .to_dict()
        )
        df["src_ip"] = df["session"].map(session_ip_map)

    # Drop rows with empty input
    filtered_df = df[df["input"].notna() & df["input"].str.strip().ne("")].copy()

    if filtered_df.empty:
        return html.Div("No command data available after filtering.")

    # Select and rename columns for clarity
    display_cols = ["timestamp", "session", "src_ip", "input"]

    return dash_table.DataTable(
        columns=[{"name": col.replace("_", " ").title(), "id": col} for col in display_cols],
        data=filtered_df[display_cols].to_dict("records"),
        style_table={"maxHeight": "400px", "overflowY": "auto"},
        style_cell={"textAlign": "left", "whiteSpace": "pre-line", "maxWidth": "600px"},
        style_header={"fontWeight": "bold"},
        page_action="none",
        fixed_rows={"headers": True}
    )
def activity_hour_bar(df):
    df = df.copy()
    df["hour"] = df["timestamp"].dt.hour
    hourly_counts = df["hour"].value_counts().sort_index().reset_index()
    hourly_counts.columns = ["hour", "count"]

    fig = px.line(
        hourly_counts,
        x="hour",
        y="count",
        title="When Do They Strike?",
        labels={"hour": "Hour of Day", "count": "Event Count"},
        text="count"
    )
    fig.update_traces(textposition="top center")
    fig.update_xaxes(dtick=1)

    fig.update_layout(margin=dict(t=60, b=60, l=40, r=20))

    return fig


def event_type_bar_with_line(df):
    if "eventid" not in df.columns:
        return html.Div("No eventid data.")
    event_count = df["eventid"].value_counts().reset_index()
    event_count.columns = ["eventid", "count"]

    bar = go.Bar(
        x=event_count["eventid"], 
        y=event_count["count"], 
        name="Count", 
        text=event_count["count"], 
        textposition="outside"
    )
    line = go.Scatter(
        x=event_count["eventid"], 
        y=event_count["count"], 
        name="Trend", 
        mode="lines+markers", 
        line_shape="spline"
    )

    fig = go.Figure(data=[bar, line])
    fig.update_layout(
        title="Event Type Distribution with Trend",
        xaxis_title="Event ID",
        yaxis_title="Count",
        showlegend=True,
        margin=dict(t=60, l=40, r=20, b=120)
    )
    return fig

def commands_summary_table(df):
    cmds = df["input"].dropna().value_counts().reset_index()
    cmds.columns = ["command", "count"]

    return dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in cmds.columns],
        data=cmds.to_dict("records"),
        style_table={
            "overflowX": "auto",
            "minWidth": "600px",  
        },
        style_cell={
            "textAlign": "left",
            "padding": "5px",
            "whiteSpace": "pre-line",
            "minWidth": "150px",   
            "maxWidth": "500px",   
        },
        style_cell_conditional=[
            {
                "if": {"column_id": "count"},
                "minWidth": "50px",
                "maxWidth": "100px",
                "textAlign": "center",
            }
        ],
        style_header={
            "fontWeight": "bold",
            "backgroundColor": "#f8f8f8",
        },
        page_size=10
    )

def most_requested_endpoints_table(df):
    from dash import dash_table, html

    # Filter for honeytoken events with valid input
    honeytoken_df = df[
        (df["eventid"] == "cowrie.honeytoken") & 
        df["input"].notna() & (df["input"] != "")
    ].copy()

    if honeytoken_df.empty:
        return html.Div("No endpoint requests found.")

    # Count number of requests per input
    counts = honeytoken_df["input"].value_counts().reset_index()
    counts.columns = ["File/Folder", "Requests"]

    # Top 10 only
    top_endpoints = counts.head(10)

    return html.Div([
        dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in top_endpoints.columns],
            data=top_endpoints.to_dict("records"),
            style_table={"maxHeight": "400px", "overflowY": "auto"},
            style_cell={"textAlign": "left", "padding": "5px"},
            style_header={"fontWeight": "bold"},
            page_size=10
        )
    ], style={"padding": "20px 5%"})


def mask_ip_address(ip):
    parts = ip.split(".")
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.xx.xx"
    return ip

def ip_summary_table(df):
    ip_counts = df["src_ip"].dropna().value_counts().reset_index()
    ip_counts.columns = ["src_ip", "count"]

    total = ip_counts["count"].sum()
    ip_counts["percentage"] = ip_counts["count"] / total * 100
    ip_counts["percentage"] = ip_counts["percentage"].map(lambda x: f"{x:.1f}%")

    ip_counts["IP address"] = ip_counts["src_ip"].apply(mask_ip_address)

    if "country" in df.columns:
        ip_country_map = df[["src_ip", "country"]].dropna().drop_duplicates().set_index("src_ip")["country"]
        ip_counts["Country"] = ip_counts["src_ip"].map(ip_country_map)
    else:
        ip_counts["Country"] = "Unknown"

    ip_counts = ip_counts[["IP address", "Country", "count", "percentage"]]
    ip_counts.columns = ["IP address", "Country", "Interactions", "Share (%)"]

    top_10 = ip_counts.head(10)

    return html.Div([
        dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in top_10.columns],
            data=top_10.to_dict("records"),
            style_cell={"textAlign": "left", "padding": "5px"},
            style_cell_conditional=[
                {"if": {"column_id": "Interactions"}, "textAlign": "center"},
                {"if": {"column_id": "Share (%)"}, "textAlign": "center"}
            ],
            style_header={"fontWeight": "bold", "backgroundColor": "#f8f8f8"},
            style_table={"overflowX": "auto"},
            page_size=10
        )
    ], style={"padding": "20px 5%"})

def geo_heatmap(df):
    if not {"latitude", "longitude"}.issubset(df.columns):
        return html.Div("GeoIP data missing.")
    geo_df = df.dropna(subset=["latitude", "longitude"])
    if geo_df.empty:
        return html.Div("No geo data points to plot.")
    geo_grouped = geo_df.groupby(["latitude", "longitude"]).size().reset_index(name="count")

    fig = px.density_mapbox(
        geo_grouped, lat="latitude", lon="longitude", z="count", radius=40,
        center=dict(lat=20, lon=0), zoom=1,
        mapbox_style="carto-positron",
        color_continuous_scale="Turbo"
    )
    fig.update_traces(opacity=0.8) 
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
    return dcc.Graph(figure=fig)

# The following functions are used for miniprint

def miniprint_top_ip_pie(df):
    ip_df = df[df["src_ip"].notna()]
    top_ips = ip_df["src_ip"].value_counts().nlargest(10).reset_index()
    top_ips.columns = ["src_ip", "count"]
    fig = px.pie(top_ips, names="src_ip", values="count", title="Top 10 Source IPs")
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return fig

def miniprint_event_type_bar(df):
    event_count = df["event"].value_counts().reset_index()
    event_count.columns = ["event", "count"]
    fig = px.bar(event_count, x="event", y="count", title="Event Type Distribution",
                 text="count")
    fig.update_traces(textposition="outside")
    return fig

def miniprint_event_type_bar_with_line(df):
    event_count = df["event"].value_counts().reset_index()
    event_count.columns = ["event", "count"]

    # 柱状图部分
    bar = go.Bar(x=event_count["event"], y=event_count["count"], name="Count", text=event_count["count"], textposition="outside")

    # 曲线（平滑折线图）部分
    line = go.Scatter(x=event_count["event"], y=event_count["count"], name="Trend", mode="lines+markers", line_shape="spline")

    fig = go.Figure(data=[bar, line])

    fig.update_layout(
        title="Event Type Distribution with Trend",
        xaxis_title="Event",
        yaxis_title="Count",
        showlegend=True,
        margin=dict(t=60, l=40, r=20, b=120)
    )
    return fig


def miniprint_event_trend_line(df):
    df["hour"] = df["timestamp"].dt.floor("h")
    trend = df.groupby(["hour", "event"]).size().reset_index(name="count")
    fig = px.line(trend, x="hour", y="count", color="event", markers=True,
                  title="What Really Happened?")
    fig.update_layout(xaxis=dict(range=[trend["hour"].min(), "2025-06-29 23:00:00"]))
    return fig

def miniprint_job_table(df):
    # Filter for print job events
    job_df = df[df["event"].isin(["append_raw_print_job", "save_raw_print_job"])].copy()

    # job length
    job_df["job_length"] = job_df["job_text"].apply(lambda x: len(x) if isinstance(x, str) else 0)

    # build the table
    table = dash_table.DataTable(
        columns=[
            {"name": "Timestamp", "id": "timestamp"},
            {"name": "Source IP", "id": "src_ip"},
            {"name": "File Name", "id": "file_name"},
            {"name": "Job Length", "id": "job_length"}
        ],
        data=job_df[["timestamp", "src_ip", "file_name", "job_length"]].to_dict("records"),
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={"textAlign": "left", "padding": "5px"},
        style_header={"fontWeight": "bold", "backgroundColor": "#f2f2f2"}
    )

    return html.Div([table], style={"padding": "20px 5%"})

def miniprint_merged_table(df):
    
    # filter for print job events
    filtered_df = df[df["event"].isin(["append_raw_print_job", "save_raw_print_job"])].copy()

    def get_file_name(row):
        return row.get("file_name") if row["event"] == "save_raw_print_job" else ""

    def get_job_text(row):
        return row.get("job_text") if row["event"] == "append_raw_print_job" else ""

    def get_file_content(row):
        filename = get_file_name(row)
        if filename:
            file_path = os.path.join("./data_visualization/raw_data/miniprint/uploads", filename)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except Exception as e:
                return f"[Read failure: {e}]"
        return ""

    def get_job_length(row):
        content = get_file_content(row) if row["event"] == "save_raw_print_job" else row.get("job_text", "")
        return len(content) if isinstance(content, str) else 0

    filtered_df["File Name"] = filtered_df.apply(get_file_name, axis=1)
    filtered_df["Content"] = filtered_df.apply(
        lambda row: get_job_text(row) if row["event"] == "append_raw_print_job" else get_file_content(row), axis=1
    )
    filtered_df["Job Length"] = filtered_df.apply(get_job_length, axis=1)

    # Build DataFrame
    merged = filtered_df[["timestamp", "src_ip", "event", "File Name", "Job Length", "Content"]].copy()
    merged.columns = ["Timestamp", "Source IP", "Event", "File Name", "Job Length", "Content"]
    merged = merged.sort_values("Timestamp", ascending=False)

    return html.Div([
        html.H3("Print Job Summary Table"),
        dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in merged.columns],
            data=merged.to_dict("records"),
            style_cell={
                "textAlign": "left",
                "padding": "5px",
                "whiteSpace": "pre-line",
                "maxWidth": "800px",
            },
            style_cell_conditional=[
                {"if": {"column_id": "Job Length"}, "textAlign": "center"},
                {"if": {"column_id": "Event"}, "textAlign": "center"},
            ],
            style_header={"fontWeight": "bold", "backgroundColor": "#f8f8f8"},
            style_table={"overflowX": "auto"},
            page_size=10
        )
    ], style={"padding": "20px 5%"})

def miniprint_activity_hour_bar(df):
    df = df.copy()
    df["hour"] = df["timestamp"].dt.hour
    hourly_counts = df["hour"].value_counts().sort_index().reset_index()
    hourly_counts.columns = ["hour", "count"]

    fig = px.line(
        hourly_counts,
        x="hour",
        y="count",
        title="When Do They Strike?",
        labels={"hour": "Hour of Day", "count": "Event Count"},
        text="count"  # show count on the line
    )
    fig.update_traces(textposition="top center")  # position text above the line
    fig.update_xaxes(dtick=1)

    return fig


def mask_ip_address(ip):
    # mask ip address
    parts = ip.split(".")
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.xx.xx"
    return ip

def miniprint_ip_summary_table(df):
    # print(df["event"].value_counts())
    ip_counts = df["src_ip"].dropna().value_counts().reset_index()
    ip_counts.columns = ["src_ip", "count"]

    total = ip_counts["count"].sum()
    ip_counts["percentage"] = ip_counts["count"] / total * 100
    ip_counts["percentage"] = ip_counts["percentage"].map(lambda x: f"{x:.1f}%")

    # Mask IP addresses for privacy
    ip_counts["IP address"] = ip_counts["src_ip"].apply(mask_ip_address)

    # src_ip → country mapping
    if "country" in df.columns:
        ip_country_map = df[["src_ip", "country"]].dropna().drop_duplicates().set_index("src_ip")["country"]
        ip_counts["Country"] = ip_counts["src_ip"].map(ip_country_map)
    else:
        ip_counts["Country"] = "Unknown"

    # Reorder and rename columns
    ip_counts = ip_counts[["IP address", "Country", "count", "percentage"]]
    ip_counts.columns = ["IP address", "Country", "Interactions", "Share (%)"]

    top_10 = ip_counts.head(10)

    return html.Div([
        dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in top_10.columns],
            data=top_10.to_dict("records"),
            style_cell={"textAlign": "left", "padding": "5px"},
            style_cell_conditional=[
                {"if": {"column_id": "Interactions"}, "textAlign": "center"},
                {"if": {"column_id": "Share (%)"}, "textAlign": "center"}
            ],
            style_header={"fontWeight": "bold", "backgroundColor": "#f8f8f8"},
            style_table={"overflowX": "auto"},
            page_size=10
        )
    ], style={"padding": "20px 5%"})

def miniprint_job_detail_table(df):
    # filter append and save events
    filtered_df = df[df["event"].isin(["append_raw_print_job", "save_raw_print_job"])].copy()

    # show job_text or file_name
    def extract_content(row):
        if row["event"] == "append_raw_print_job":
            return row.get("job_text", "")[:200]  # limit to 200 characters
        elif row["event"] == "save_raw_print_job":
            return row.get("file_name", "")
        return ""

    filtered_df["Content"] = filtered_df.apply(extract_content, axis=1)

    # filter and rename columns
    filtered_df = filtered_df[["timestamp", "src_ip", "event", "Content"]].dropna()
    filtered_df.columns = ["Timestamp", "Source IP", "Event", "Content"]

    return html.Div([
        html.H3("Print Job Details"),
        dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in filtered_df.columns],
            data=filtered_df.to_dict("records"),
            style_cell={"textAlign": "left", "padding": "5px", "maxWidth": "800px", "whiteSpace": "pre-line"},
            style_header={"fontWeight": "bold", "backgroundColor": "#f8f8f8"},
            style_table={"overflowX": "auto"},
            page_size=10
        )
    ], style={"padding": "20px 5%"})

def miniprint_geo_heatmap(df):
    if not {"latitude", "longitude"}.issubset(df.columns):
        return html.Div("GeoIP data missing. Please enrich with latitude and longitude.")

    geo_df = df.dropna(subset=["latitude", "longitude"])
    geo_grouped = (
        geo_df
        .groupby(["latitude", "longitude"])
        .size()
        .reset_index(name="count")
    )

    fig = px.density_mapbox(
        geo_grouped, lat="latitude", lon="longitude", z="count", radius=40,
        center=dict(lat=20, lon=0), zoom=1,
        mapbox_style="carto-positron",
        color_continuous_scale="Turbo"
    )

    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

    return dcc.Graph(figure=fig)


# The following functions are used for snare.err
# Snare Error Log: Top IP Table
def snare_err_top_ip_table(df):
    ip_counts = df["src_ip"].value_counts().reset_index()
    ip_counts.columns = ["IP Address", "Count"]
    total = ip_counts["Count"].sum()
    ip_counts["Share (%)"] = (ip_counts["Count"] / total * 100).round(1).astype(str) + "%"

    return html.Div([
        html.H3("Top Attacker IPs"),
        dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in ip_counts.columns],
            data=ip_counts.to_dict("records"),
            style_cell={"textAlign": "left", "padding": "6px"},
            style_header={"fontWeight": "bold", "backgroundColor": "#f0f0f0"},
            style_table={"overflowX": "auto"},
            page_size=10
        )
    ], style={"padding": "10px 5%"})

# Snare Error Log: Access Path Table
def snare_err_path_table(df):
    # count paths
    path_counts = df["path"].value_counts().reset_index()
    path_counts.columns = ["Path", "Request Count"]

    # calculate percentage
    total = path_counts["Request Count"].sum()
    path_counts["Percentage"] = path_counts["Request Count"] / total * 100
    path_counts["Percentage"] = path_counts["Percentage"].map(lambda x: f"{x:.1f}%")

    return html.Div([
        html.H3("Accessed Paths"),
        dash_table.DataTable(
            columns=[
                {"name": "Path", "id": "Path"},
                {"name": "Request Count", "id": "Request Count"},
                {"name": "Percentage", "id": "Percentage"},
            ],
            data=path_counts.to_dict("records"),
            page_size=10,
            style_cell={"textAlign": "left", "padding": "6px"},
            style_header={"fontWeight": "bold", "backgroundColor": "#f0f0f0"},
            style_table={"overflowX": "auto"}
        )
    ], style={"padding": "10px 5%"})


# Snare Error Log: Attack Frequency Line
def snare_err_attack_frequency(df):
    df = df.copy()
    df["date"] = df["timestamp"].dt.floor("d") 
    freq_df = df.groupby("date").size().reset_index(name="count")

    fig = px.line(
        freq_df,
        x="date",
        y="count",
        title="Attack Frequency Over Time (per day)",
        labels={"date": "Time", "count": "Requests"},
        markers=True,
        text="count"
    )

    fig.update_traces(textposition="top center")

    fig.update_layout(
        title={
            "text": "Attack Frequency Over Time (per day)",
            "x": 0.5,  # Center the title
            "xanchor": "center"
        },
        title_font=dict(size=18, family="Arial", color="black"),
        margin=dict(l=20, r=20, t=60, b=40)
    )

    return dcc.Graph(figure=fig)



# The following functions are used for snare.log

def snare_log_classify_behavior(df):
    df['behavior'] = 'unknown'

    df.loc[df['msg'].str.contains("Go-http-client|Odin", na=False), 'behavior'] = 'scanner'

    font_404 = df['path'].str.contains("fa-solid-900.(woff2|ttf)", na=False) & df['msg'].str.contains(' 404 ', na=False)
    df.loc[font_404, 'behavior'] = 'font_404'

    special_paths = df['path'].str.contains(r'\.git/config|XDEBUG_SESSION_START|redlion|solr|HNAP1|evox', na=False)
    df.loc[special_paths, 'behavior'] = 'special_probe'

    browser_agent = df['msg'].str.contains("Mozilla", na=False)
    normal_pages = df['path'].isin([
        "/", "/dashboard.html", "/lighting.html", "/thermostat.html", "/appliances.html", "/printer.html"
    ])
    df.loc[browser_agent & normal_pages, 'behavior'] = 'Human_Attacker'

    return df

# Snare Log: Behavior Pie Chart
def snare_log_behavior_pie(df):
    behavior_counts = df['behavior'].value_counts()
    fig = px.pie(
        names=behavior_counts.index,
        values=behavior_counts.values,
        title="Behavior Classification Breakdown"
    )
    return dcc.Graph(figure=fig)

# Snare Log: Top Request Paths (Bar Chart)
def snare_log_top_paths_bar(df):
    top_paths = df['path'].value_counts().nlargest(10)
    fig = px.bar(
        x=top_paths.index,
        y=top_paths.values,
        labels={'x': 'Request Path', 'y': 'Count'},
        title="Top 10 Requested Paths"
    )
    fig.update_layout(margin=dict(t=40, l=10, r=10, b=40))
    return dcc.Graph(figure=fig)

# Snare Log: Recent Event Table
def snare_log_status_table(df):
    df = df.copy()

    # set IP（snare.server should be replaced to N/A）
    df["src_ip"] = df.apply(
        lambda row: "N/A" if row["source"] == "snare.server" else row.get("src_ip", "None"),
        axis=1
    )

    # intercept message
    df["msg"] = df["msg"].apply(lambda x: x[:250] + "..." if isinstance(x, str) and len(x) > 250 else x)

    columns = [
        {"name": "Timestamp", "id": "timestamp"},
        {"name": "IP Address", "id": "src_ip"},
        {"name": "Path", "id": "path"},
        {"name": "Level", "id": "level"},
        {"name": "Source", "id": "source"},
        # {"name": "Behavior", "id": "behavior"},
        {"name": "Message", "id": "msg"},
    ]

    return html.Div([
        # html.H4("Raw Request Events Behavior Analysis", style={"marginTop": "30px"}),
        dash_table.DataTable(
            columns=columns,
            data=df.sort_values(by="timestamp", ascending=False).to_dict("records"),
            page_size=15,
            style_cell={
                "textAlign": "left",
                "padding": "6px",
                "whiteSpace": "normal",
                "maxWidth": "1000px",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
                "fontSize": "14px"
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': 'src_ip'},
                    'whiteSpace': 'nowrap',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': '120px'
                },
                 {
                    'if': {'column_id': 'timestamp'},
                    'whiteSpace': 'nowrap',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': '160px'
                }
            ],
            style_header={
                "fontWeight": "bold",
                "backgroundColor": "#f0f0f0",
                "fontSize": "15px"
            },
            style_table={
                "overflowX": "auto",
                "minWidth": "1200px",
            }
        )
    ], style={"paddingLeft": "0px", "paddingRight": "0"})

def snare_log_top_ip_pip_chart(df):
    # exclude NaN and "None" values
    filtered_ips = df['src_ip'].dropna()
    filtered_ips = filtered_ips[filtered_ips != "None"]

    top_ips = filtered_ips.value_counts().nlargest(10)

    fig = px.pie(
        names=top_ips.index,
        values=top_ips.values,
        title="Top 10 Source IPs"
    )
    return dcc.Graph(figure=fig)


def snare_log_top_path_table(df):
    # filter out NaN and "N/A" paths
    top_paths = df[df['path'] != 'N/A']['path'].value_counts().nlargest(50).reset_index()
    top_paths.columns = ['Path', 'Count']

    # calculate percentage
    total = top_paths['Count'].sum()
    top_paths['Percentage'] = top_paths['Count'] / total * 100
    top_paths['Percentage'] = top_paths['Percentage'].map(lambda x: f"{x:.1f}%")

    return html.Div([
        html.H3("Top 50 Request Paths"),
        dash_table.DataTable(
            columns=[
                {"name": "Path", "id": "Path"},
                {"name": "Count", "id": "Count"},
                {"name": "Percentage", "id": "Percentage"},
            ],
            data=top_paths.to_dict("records"),
            page_size=10,
            style_cell={"textAlign": "left", "padding": "6px"},
            style_header={"fontWeight": "bold", "backgroundColor": "#f0f0f0"},
            style_table={"overflowX": "auto"}
        )
    ], style={"padding": "10px 5%"})


def snare_log_ip_heatmap(df):
    if not {"latitude", "longitude"}.issubset(df.columns):
        return html.Div("GeoIP data missing. Please enrich with latitude and longitude.")

    geo_df = df.dropna(subset=["latitude", "longitude"])
    geo_grouped = (
        geo_df
        .groupby(["latitude", "longitude"])
        .size()
        .reset_index(name="count")
    )

    fig = px.density_mapbox(
        geo_grouped, lat="latitude", lon="longitude", z="count", radius=40,
        center=dict(lat=20, lon=0), zoom=1,
        mapbox_style="carto-positron",
        color_continuous_scale="Turbo"
    )


    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

    return dcc.Graph(figure=fig)

def snare_log_attack_frequency(df):
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Attack frequency by hour
    df["hour"] = df["timestamp"].dt.hour
    df["date"] = pd.to_datetime(df["timestamp"].dt.date)
    hour_freq = df["hour"].value_counts().sort_index()
    
    fig_hour = go.Figure()
    fig_hour.add_trace(go.Bar(
        x=hour_freq.index,
        y=hour_freq.values,
        name="Hourly Frequency",
        marker_color="#636efa"
    ))
    fig_hour.add_trace(go.Scatter(
    x=hour_freq.index,
    y=hour_freq.values,
    mode="lines+markers+text",
    name="Smoothed Trend",
    line=dict(shape='spline', color='orange', width=2),
    marker=dict(size=6),
    text=[str(v) for v in hour_freq.values],   # add numbers 
    textposition="top center"                  # place text above the markers
    ))

    fig_hour.update_layout(
        title="Snare Log: Hourly Attack Frequency with Trend Line",
        xaxis_title="Hour of Day",
        yaxis_title="Number of Requests",
        plot_bgcolor="#f5f8fc",
        hovermode="x unified",
        margin=dict(t=50, l=50, r=30, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Attack frequency by date
    df["date"] = df["timestamp"].dt.date
    date_freq = df["date"].value_counts().sort_index()
    fig_date = px.line(
        x=date_freq.index,
        y=date_freq.values,
        markers=True,
        labels={"x": "Date", "y": "Number of Requests"},
        title="Snare Log: Daily Attack Frequency",
        text=date_freq.values,
    )
    fig_date.update_traces(textposition="top center")
    fig_date.update_layout(margin=dict(l=20, r=20, t=50, b=40))

    return html.Div([
        html.H3("Snare Log Attack Frequency Overview"),
        dcc.Graph(figure=fig_hour, style={"paddingLeft": "0px", "paddingRight": "0"}),
        dcc.Graph(figure=fig_date, style={"paddingLeft": "0px", "paddingRight": "0"}),
    ])


# The following functions are used for tanner.log
def tanner_log_table(df):
    cols = ["timestamp", "src_ip", "path", "uuid", "detection_name", "detection_type", "status"]
    df = df[cols].copy()

    return html.Div([
        html.H3("Tanner Log Summary Table"),
        dash_table.DataTable(
            # columns=[{"name": c.replace('_', ' ').title(), "id": c} for c in cols],
            columns=[
                {"name": "Timestamp", "id": "timestamp"},
                {"name": "Tanner IP", "id": "src_ip"},  
                {"name": "Requested Path", "id": "path"},
                {"name": "Uuid", "id": "uuid"},
                {"name": "Detection Name", "id": "detection_name"},
                {"name": "Detection Type", "id": "detection_type"},
                {"name": "Status", "id": "status"},
            ],
            data=df.sort_values("timestamp", ascending=False).to_dict("records"),
            page_size=20,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "5px", "maxWidth": "400px", "whiteSpace": "normal"},
            style_header={"fontWeight": "bold", "backgroundColor": "#f8f8f8"}
        )
    ])

def tanner_log_path_bar(df):
    top_paths = df["path"].value_counts().nlargest(10).reset_index()
    top_paths.columns = ["Path", "Count"]
    fig = px.bar(top_paths, x="Path", y="Count", title="Top 10 Attacked Paths", text="Count")
    return dcc.Graph(figure=fig)

def tanner_log_hourly_bar(df):
    df = df.copy()
    df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
    counts = df["hour"].value_counts().sort_index().reset_index()
    counts.columns = ["Hour", "Count"]
    fig = px.bar(counts, x="Hour", y="Count", title="Hourly Request Distribution", text="Count")
    return dcc.Graph(figure=fig)

def tanner_top10_path_table(df):
    path_count = df["path"].value_counts().reset_index().head(10)
    path_count.columns = ["Path", "Count"]

    # Calculate percentage
    total = path_count["Count"].sum()
    path_count["Percentage"] = path_count["Count"] / total * 100
    path_count["Percentage"] = path_count["Percentage"].map(lambda x: f"{x:.1f}%")

    table = dash_table.DataTable(
        columns=[
            {"name": "Path", "id": "Path"},
            {"name": "Count", "id": "Count"},
            {"name": "Percentage", "id": "Percentage"},
        ],
        data=path_count.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "padding": "6px"},
        style_header={"fontWeight": "bold", "backgroundColor": "#f0f0f0"},
    )

    return html.Div([
        html.H4("Top 10 Attacked Paths"),
        table
    ])

def tanner_hourly_line_chart(df):
    df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
    hourly_counts = df["hour"].value_counts().sort_index()
    fig = px.line(
        x=hourly_counts.index,
        y=hourly_counts.values,
        markers=True,
        labels={"x": "Hour", "y": "Count"},
        title="Hourly Request Distribution",
        text=hourly_counts.values  # show count on the line
    )
    fig.update_traces(text=hourly_counts.values, textposition="top center")
    fig.update_layout(xaxis=dict(dtick=1))

    return dcc.Graph(figure=fig)


# The following functions are used for tanner.err
def tanner_err_type_chart(df):
    counts = df["message"].value_counts().nlargest(10).reset_index()
    counts.columns = ["Error Message", "Count"]
    fig = px.bar(counts, x="Error Message", y="Count", title="Top Error Types", text="Count")
    return dcc.Graph(figure=fig)

def tanner_err_type_pie_chart(df):
    counts = df["message"].value_counts().nlargest(10).reset_index()
    counts.columns = ["Error Message", "Count"]

    fig = px.pie(
        counts,
        names="Error Message",
        values="Count",
        title="Top Error Types",
        hole=0.4  
    )

    fig.update_traces(textinfo="percent+label")  # show percentage and label
    fig.update_layout(
        title={
            "text": "Top Error Types",
            "x": 0.0,
            "xanchor": "left"
        },
        title_font=dict(size=18, family="Arial Black", color="black"),
        margin=dict(t=60, l=20, r=20, b=20)
    )

    return dcc.Graph(figure=fig)

def tanner_err_time_series(df):
    df = df.copy()
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date
    time_count = df["date"].value_counts().sort_index().reset_index()
    time_count.columns = ["Date", "Count"]
    fig = px.line(time_count, x="Date", y="Count", title="Error Frequency Over Time", markers=True)
    return dcc.Graph(figure=fig)

def tanner_err_trace_blocks(df):
    df = df.copy()
    traces = df["message"].dropna().unique()[:5]
    return html.Div([
        html.H3("Sample Error Traces"),
        *[html.Details([html.Summary(f"Trace #{i+1}"), html.Pre(trace)]) for i, trace in enumerate(traces)]
    ], style={"padding": "10px 5%"})


# the following functions are used for analysis of the user study data
def sav_trait_distribution_bar(df):
    """Show the distribution of self-reported personality traits."""
    
    trait_mapping = {
        1: "Openness to Experience",
        2: "Conscientiousness",
        3: "Low Extraversion",
        4: "Low Agreeableness",
        5: "Low Neuroticism"
    }

    trait_series = df["Q1_personality_check"].map(trait_mapping)
    all_traits = list(trait_mapping.values())

    trait_counts = trait_series.value_counts().reindex(all_traits, fill_value=0).reset_index()
    trait_counts.columns = ["Trait", "Count"]
    trait_counts["Percentage"] = (trait_counts["Count"] / len(df) * 100).round(2)

    fig = px.bar(
        trait_counts,
        x="Trait",
        y="Count",
        color="Trait",
        text="Count",
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        title=dict(text="Q1: Self-reported personality trait distribution", x=0.5, font=dict(size=16)),
        yaxis=dict(range=[0, max(trait_counts["Count"].max() + 5, 20)]),
        height=450,
        margin=dict(t=50, b=60, l=40, r=40),
        showlegend=False,
        xaxis_title="Trait",
        yaxis_title="Count"
    )

    return dcc.Graph(figure=fig)


def sav_confidence_bar(df: pd.DataFrame):
    """Generate a bar chart for Q2 confidence level responses."""
    
    likert_labels = {
        1: "Not at all",
        2: "Slightly",
        3: "Moderately",
        4: "Very",
        5: "Extremely"
    }

    counts = df["Q2_confident_experience"].value_counts().reindex(likert_labels.keys(), fill_value=0)

    plot_df = pd.DataFrame({
        "Confidence Level": [likert_labels[k] for k in counts.index],
        "Count": counts.values
    })

    # Use pastel colors in fixed order to match labels
    pastel_colors = px.colors.qualitative.Pastel[:5]

    fig = px.bar(
        plot_df,
        x="Confidence Level",
        y="Count",
        text="Count",
        color="Confidence Level",
        color_discrete_sequence=pastel_colors
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        title=dict(text="Q2: Confidence levels while interacting with the system", x=0.5, font=dict(size=16)),
        yaxis=dict(range=[0, max(plot_df["Count"].max() + 5, 20)]),
        height=450,
        margin=dict(t=50, b=60, l=40, r=40),
        showlegend=True,
        xaxis_title="Confidence Level",
        yaxis_title="Count"
    )

    return dcc.Graph(figure=fig)

def likert_bar_chart(df, column_name: str, title: str):
    """
    Generate a standardized Likert-style bar chart for 5-point scale survey items.

    Parameters:
        df (pd.DataFrame): Input data.
        column_name (str): Column name in df containing Likert values (1-5).
        title (str): Title for the chart.
    """

    likert_labels = {
        1: "Not at all",
        2: "Slightly",
        3: "Moderately",
        4: "Very",
        5: "Extremely"
    }

    counts = df[column_name].value_counts().reindex(likert_labels.keys(), fill_value=0)

    plot_df = pd.DataFrame({
        "Response": [likert_labels[k] for k in counts.index],
        "Count": counts.values
    })

    fig = px.bar(
        plot_df,
        x="Response",
        y="Count",
        text="Count",
        color="Response",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=16)),
        yaxis=dict(range=[0, max(plot_df["Count"].max() + 5, 20)]),
        height=450,
        margin=dict(t=50, b=60, l=40, r=40),
        showlegend=True,
        xaxis_title="Response",
        yaxis_title="Count"
    )

    return dcc.Graph(figure=fig)

def likert_pie_chart(df, column_name, title):
    """
    Plot a Likert-style pie chart with balanced, aesthetic colors.
    """
    likert_labels = {
        1: "Not at all",
        2: "Slightly",
        3: "Moderately",
        4: "Very",
        5: "Extremely"
    }

    soft_but_distinct_colors = [
        "#60c5ba",  # Not at all - muted gray-blue
        "#edcd84",  # Slightly - soft orange
        "#ea9b7e",  # Moderately - green-cyan
        "#dab8ea",  # Very - soft red-brown
        "#9dc77b"   # Extremely - purple
    ]

    counts = df[column_name].value_counts().reindex(likert_labels.keys(), fill_value=0)
    plot_df = pd.DataFrame({
        "Label": [f"{likert_labels[i]}: {counts[i]}" for i in counts.index],
        "Value": counts.values
    })

    fig = px.pie(
        plot_df,
        names="Label",
        values="Value",
        title=title,
        color="Label",
        color_discrete_sequence=soft_but_distinct_colors
    )

    fig.update_traces(pull=0, textinfo='label+percent')


    fig.update_layout(
        height=350,
        margin=dict(t=40, b=40, l=40, r=40),
        showlegend=False
    )

    return dcc.Graph(figure=fig)


def analyze_q7_confidence(df):
    """
    Analyze Q7 responses based on existing dataframe.
    Visualize confidence factors: feedback clarity, command success, and system familiarity.
    """

    # Rename for readability 
    df = df.rename(columns={
        'Q7_confident_feedback_clear': 'Clear Feedback',
        'Q7_confident_command_success': 'Command Success',
        'Q7_confident_system_familiarity': 'System Familiarity'
    })

    likert_labels = {
        1: "Not at all",
        2: "Slightly",
        3: "Moderately",
        4: "Very",
        5: "Extremely"
    }

    def get_likert_df(df, question_columns, likert_labels):
        result = []
        for col in question_columns:
            counts = df[col].value_counts().reindex(likert_labels.keys(), fill_value=0)
            for key, val in counts.items():
                result.append({
                    "Question": col,
                    "Confidence Level": likert_labels[key],
                    "Count": val
                })
        return pd.DataFrame(result)

    question_cols = ["Clear Feedback", "Command Success", "System Familiarity"]
    plot_df = get_likert_df(df, question_cols, likert_labels)

    fig = px.bar(
        plot_df,
        x="Question",
        y="Count",
        color="Confidence Level",
        text="Count",
        barmode="group",
        color_discrete_map={
            "Not at all": "#79c2af",
            "Slightly": "#f0d574",
            "Moderately": "#99d9e4",
            "Very": "#d9a3e3",
            "Extremely": "#9ac47a"
        },
        title="Q7: Confidence experience based on different factors"
    )

    fig.update_traces(textposition='outside')
    
    fig.update_layout(
        height=500,
        margin=dict(t=60, b=60, l=40, r=40),
        xaxis_title=None,
        yaxis_title="Count",
        legend_title="Confidence Level"
    )

    return dcc.Graph(figure=fig)

def analyze_q8_surprise(df):
    """
    Analyze Q8 responses based on existing dataframe.
    Visualize surprise factors: exposed credentials, hidden files, and fake errors.
    """

    # Rename for readability
    df = df.rename(columns={
        'Q8_surprise_expose_credentials': 'Exposed Credentials',
        'Q8_surprise_hidden_sensitive_files': 'Hidden Files',
        'Q8_surprise_fake_errors': 'Fake Errors'
    })

    likert_labels = {
        1: "Not at all",
        2: "Slightly",
        3: "Moderately",
        4: "Very",
        5: "Extremely"
    }

    def get_likert_df(df, question_columns, likert_labels):
        result = []
        for col in question_columns:
            counts = df[col].value_counts().reindex(likert_labels.keys(), fill_value=0)
            for key, val in counts.items():
                result.append({
                    "Question": col,
                    "Surprise Level": likert_labels[key],
                    "Count": val
                })
        return pd.DataFrame(result)

    question_cols = ["Exposed Credentials", "Hidden Files", "Fake Errors"]
    plot_df = get_likert_df(df, question_cols, likert_labels)

    fig = px.bar(
        plot_df,
        x="Question",
        y="Count",
        color="Surprise Level",
        text="Count",
        barmode="group",
        color_discrete_map={
            "Not at all": "#79c2af",
            "Slightly": "#f0d574",
            "Moderately": "#99d9e4",
            "Very": "#d9a3e3",
            "Extremely": "#9ac47a"
        },
        title="Q8: Surprise experience based on different system behaviors"
    )
    
    fig.update_traces(textposition='outside')
    
    fig.update_layout(
        height=500,
        margin=dict(t=60, b=60, l=40, r=40),
        xaxis_title=None,
        yaxis_title="Count",
        legend_title="Surprise Level"
    )

    return dcc.Graph(figure=fig)
    
def analyze_q9_confusion(df):
    """
    Analyze Q9 responses based on existing dataframe.
    Visualize confusion factors: difficult output, unclear navigation, and unfamiliar error codes.
    """

    # Rename for readability
    df = df.rename(columns={
        'Q9_confusion_output_difficult': 'Difficult Output',
        'Q9_confusion_navigation_unclear': 'Unclear Navigation',
        'Q9_confusion_error_codes': 'Unfamiliar Error Codes'
    })

    likert_labels = {
        1: "Not at all",
        2: "Slightly",
        3: "Moderately",
        4: "Very",
        5: "Extremely"
    }

    def get_likert_df(df, question_columns, likert_labels):
        result = []
        for col in question_columns:
            counts = df[col].value_counts().reindex(likert_labels.keys(), fill_value=0)
            for key, val in counts.items():
                result.append({
                    "Question": col,
                    "Confusion Level": likert_labels[key],
                    "Count": val
                })
        return pd.DataFrame(result)

    question_cols = ["Difficult Output", "Unclear Navigation", "Unfamiliar Error Codes"]
    plot_df = get_likert_df(df, question_cols, likert_labels)

    fig = px.bar(
        plot_df,
        x="Question",
        y="Count",
        color="Confusion Level",
        barmode="group",
        text="Count",
        color_discrete_map={
            "Not at all": "#79c2af",
            "Slightly": "#f0d574",
            "Moderately": "#99d9e4",
            "Very": "#d9a3e3",
            "Extremely": "#9ac47a"
        },
        title="Q9: Confusion experience based on different system factors"
    )

    fig.update_traces(textposition='outside')
    fig.update_layout(
        height=500,
        margin=dict(t=60, b=60, l=40, r=40),
        xaxis_title=None,
        yaxis_title="Count",
        legend_title="Confusion Level"
    )

    return dcc.Graph(figure=fig)

def analyze_q10_frustration(df):
    """
    Analyze Q10 responses based on existing dataframe.
    Visualize frustration factors: lack of progress, misleading response, and dead ends.
    """

    df = df.rename(columns={
        'Q10_frustration_lack_progress': 'Lack of Progress',
        'Q10_frustration_misleading_response': 'Misleading Response',
        'Q10_frustration_dead_ends': 'Dead Ends'
    })

    likert_labels = {
        1: "Not at all",
        2: "Slightly",
        3: "Moderately",
        4: "Very",
        5: "Extremely"
    }

    def get_likert_df(df, question_columns, likert_labels):
        result = []
        for col in question_columns:
            counts = df[col].value_counts().reindex(likert_labels.keys(), fill_value=0)
            for key, val in counts.items():
                result.append({
                    "Question": col,
                    "Frustration Level": likert_labels[key],
                    "Count": val
                })
        return pd.DataFrame(result)

    question_cols = ["Lack of Progress", "Misleading Response", "Dead Ends"]
    plot_df = get_likert_df(df, question_cols, likert_labels)

    fig = px.bar(
        plot_df,
        x="Question",
        y="Count",
        color="Frustration Level",
        barmode="group",
        text="Count",
        color_discrete_map={
            "Not at all": "#79c2af",
            "Slightly": "#f0d574",
            "Moderately": "#99d9e4",
            "Very": "#d9a3e3",
            "Extremely": "#9ac47a"
        },
        title="Q10: Frustration experience based on different interaction outcomes"
    )

    fig.update_traces(textposition='outside')
    fig.update_layout(
        height=500,
        margin=dict(t=60, b=60, l=40, r=40),
        xaxis_title=None,
        yaxis_title="Count",
        legend_title="Frustration Level"
    )

    return dcc.Graph(figure=fig)

def analyze_q11_selfdoubt(df):
    """
    Analyze Q11 responses based on existing dataframe.
    Visualize self-doubt factors: self-questioning, unusual files, and unexpected outcomes.
    """

    df = df.rename(columns={
        'Q11_selfdoubt_question_self': 'Noticeable Delays',
        'Q11_selfdoubt_unusual_files': 'Unusual Files',
        'Q11_selfdoubt_unexpected_outcomes': 'Unexpected Outcomes'
    })

    likert_labels = {
        1: "Not at all",
        2: "Slightly",
        3: "Moderately",
        4: "Very",
        5: "Extremely"
    }

    def get_likert_df(df, question_columns, likert_labels):
        result = []
        for col in question_columns:
            counts = df[col].value_counts().reindex(likert_labels.keys(), fill_value=0)
            for key, val in counts.items():
                result.append({
                    "Question": col,
                    "Self-Doubt Level": likert_labels[key],
                    "Count": val
                })
        return pd.DataFrame(result)

    question_cols = ["Noticeable Delays", "Unusual Files", "Unexpected Outcomes"]
    plot_df = get_likert_df(df, question_cols, likert_labels)

    fig = px.bar(
        plot_df,
        x="Question",
        y="Count",
        color="Self-Doubt Level",
        barmode="group",
        text="Count",
        color_discrete_map={
            "Not at all": "#79c2af",
            "Slightly": "#f0d574",
            "Moderately": "#99d9e4",
            "Very": "#d9a3e3",
            "Extremely": "#9ac47a"
        },
        title="Q11: Self-doubt experience based on different triggers"
    )

    fig.update_traces(textposition='outside')
    fig.update_layout(
        height=500,
        margin=dict(t=60, b=60, l=40, r=40),
        xaxis_title=None,
        yaxis_title="Count",
        legend_title="Self-Doubt Level"
    )

    return dcc.Graph(figure=fig)

def analyze_q12_emotion_transitions(df):
    """
    Analyze Q12 responses for emotional transitions throughout the interaction.
    Visualize emotion flow from confidence to self-doubt in sequence.
    """

    df = df.rename(columns={
        'Q12_emotion_confident_to_surprise': 'Confidence → Surprise',
        'Q12_emotion_surprise_to_confusion': 'Surprise → Confusion',
        'Q12_emotion_confusion_to_frustration': 'Confusion → Frustration',
        'Q12_emotion_frustration_to_selfdoubt': 'Frustration → Self-Doubt',
        'Q12_emotion_selfdoubt_to_confident': 'Self-Doubt → Confidence'
    })

    likert_labels = {
        1: "Not at all",
        2: "Slightly",
        3: "Moderately",
        4: "Very",
        5: "Extremely"
    }

    def get_transition_df(df, transition_columns, likert_labels):
        result = []
        for col in transition_columns:
            counts = df[col].value_counts().reindex(likert_labels.keys(), fill_value=0)
            for key, val in counts.items():
                result.append({
                    "Transition": col,
                    "Strength": likert_labels[key],
                    "Count": val
                })
        return pd.DataFrame(result)

    transition_cols = [
        "Confidence → Surprise",
        "Surprise → Confusion",
        "Confusion → Frustration",
        "Frustration → Self-Doubt",
        "Self-Doubt → Confidence"
    ]

    plot_df = get_transition_df(df, transition_cols, likert_labels)

    fig = px.bar(
        plot_df,
        x="Transition",
        y="Count",
        color="Strength",
        barmode="group",
        text="Count",
        color_discrete_map={
            "Not at all": "#79c2af",
            "Slightly": "#f0d574",
            "Moderately": "#99d9e4",
            "Very": "#d9a3e3",
            "Extremely": "#9ac47a"
        },
        title="Q12: To what extent did you experience the emotional transitions during the interaction?"
    )

    fig.update_traces(textposition='outside')
    fig.update_layout(
        height=520,
        margin=dict(t=60, b=60, l=40, r=40),
        xaxis_title=None,
        yaxis_title="Count",
        legend_title="Transition Intensity"
    )

    return dcc.Graph(figure=fig)

def likert_line_chart(df, column_name, title):
    import pandas as pd
    import plotly.graph_objects as go
    from dash import dcc

    likert_labels = {
        1: "Strongly disagree",
        2: "Disagree",
        3: "Undecided",
        4: "Agree",
        5: "Strongly agree"
    }

    soft_but_distinct_colors = [
        "#60c5ba", "#edcd84", "#ea9b7e", "#dab8ea", "#9dc77b"
    ]

    counts = df[column_name].value_counts().reindex(likert_labels.keys(), fill_value=0)
    x_labels = list(likert_labels.values())
    y_values = counts.values

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_labels,
        y=y_values,
        mode="lines+markers+text",
        line=dict(color="#2a5a8a", width=3),
        marker=dict(color=soft_but_distinct_colors, size=10),
        text=y_values,
        textposition="top center",
        name="Response Count"
    ))

    fig.update_layout(
        title=title,
        xaxis=dict(
            title="Likert Scale",
            title_font=dict(size=16),
            tickfont=dict(size=14),
            categoryorder='array',
            categoryarray=x_labels,
            range=[-0.6, 4.5]  # 手动留白：将左侧推远一些
        ),
        yaxis=dict(
            title="Count",
            range=[0, max(y_values) + 6],
            title_font=dict(size=16),
            tickfont=dict(size=14),
            showgrid=True,
            gridcolor="#e0e0e0",
            gridwidth=1
        ),
        height=450,
        margin=dict(t=40, b=90, l=60, r=40),
        plot_bgcolor="#ffffff",
        legend=dict(
            title="Response Count",
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5
        )
    )

    return dcc.Graph(figure=fig)


def calculate_cronbach_alpha_q1_to_q17(df):
    """
    Calculate Cronbach's Alpha for Q1 to Q17 items and return a Dash DataTable.
    Uses prefix matching to identify relevant columns.
    """
    # 正则匹配 Q2_ 到 Q17_ 开头的所有列
    q_columns = [col for col in df.columns if re.match(r'^Q([2-9]|1[0-7])_', col)]
    
    if len(q_columns) < 2:
        return html.Div("Not enough items found for reliability analysis (need at least 2).")

    alpha, _ = pg.cronbach_alpha(data=df[q_columns])

    table_df = pd.DataFrame([{
        "Scale": "Q1 to Q17",
        "Number of Items": len(q_columns),
        "Cronbach's Alpha": f"{alpha:.3f}",
        "Interpretation": interpret_alpha(alpha)
    }])

    table = dash_table.DataTable(
        columns=[
            {"name": "Scale", "id": "Scale"},
            {"name": "Number of Items", "id": "Number of Items"},
            {"name": "Cronbach's Alpha", "id": "Cronbach's Alpha"},
            {"name": "Interpretation", "id": "Interpretation"},
        ],
        data=table_df.to_dict("records"),
        style_table={"width": "80%", "margin": "auto"},
        style_cell={"textAlign": "center", "fontFamily": "Arial"},
        style_header={"fontWeight": "bold", "backgroundColor": "#f8f8f8"},
    )

    return html.Div([
        html.H4("Cronbach's Alpha for the Questionnaire", style={"textAlign": "center", "marginTop": "30px"}),
        table
    ])

def calculate_cronbach_by_emotion(df, emotion_label):
    """
    Compute Cronbach's Alpha for a single emotion dimension.
    Emotion options: "Confidence", "Surprise", "Confusion", "Frustration", "Self-Doubt"
    """
    emotion_groups = {
        "Confidence": [
            "Q2_confident_experience",
            "Q7_confident_feedback_clear",
            "Q7_confident_command_success",
            "Q7_confident_system_familiarity"
        ],
        "Surprise": [
            "Q3_surprise_experience",
            "Q8_surprise_expose_credentials",
            "Q8_surprise_hidden_sensitive_files",
            "Q8_surprise_fake_errors"
        ],
        "Confusion": [
            "Q4_confused_experience",
            "Q9_confusion_output_difficult",
            "Q9_confusion_navigation_unclear",
            "Q9_confusion_error_codes",
            "Q9_confusion_unpredictable_behavior"
        ],
        "Frustration": [
            "Q5_frustrated_experience",
            "Q10_frustration_lack_progress",
            "Q10_frustration_misleading_response",
            "Q10_frustration_dead_ends"
        ],
        "Self-Doubt": [
            "Q6_selfdoubt_experience",
            "Q11_selfdoubt_question_self",
            "Q11_selfdoubt_unusual_files",
            "Q11_selfdoubt_unexpected_outcomes"
        ]
    }

    cols = emotion_groups.get(emotion_label, [])
    valid_cols = [col for col in cols if col in df.columns]

    if len(valid_cols) >= 2:
        alpha, _ = pg.cronbach_alpha(data=df[valid_cols])
        alpha_val = f"{alpha:.3f}"
        interpretation = interpret_alpha(alpha)
    else:
        alpha_val = "N/A"
        interpretation = "Too few items"

    return html.Div([
        html.H5(f"Cronbach's Alpha for {emotion_label} Related Items", style={"textAlign": "center"}),
        dash_table.DataTable(
            columns=[
                {"name": "Emotion", "id": "Emotion"},
                {"name": "Items", "id": "Items"},
                {"name": "Cronbach's Alpha", "id": "Alpha"},
                {"name": "Interpretation", "id": "Interpretation"},
            ],
            data=[{
                "Emotion": emotion_label,
                "Items": len(valid_cols),
                "Alpha": alpha_val,
                "Interpretation": interpretation
            }],
            style_table={"width": "100%"},
            style_cell={"textAlign": "center"},
            style_header={"fontWeight": "bold"}
        )
    ])
    
def interpret_alpha(alpha):
    """
    Return interpretation string based on Cronbach's Alpha value.
    """
    if alpha >= 0.9:
        return "Excellent"
    elif alpha >= 0.8:
        return "Reliable"
    elif alpha >= 0.7:
        return "Acceptable"
    elif alpha >= 0.6:
        return "Useful but need revision"
    else:
        return "Poor"

def correlation_heatmap_emotion_q13_17(df):
    selected_cols = [
        "EMOTION_CONFIDENCE",
        "EMOTION_SURPRISE",
        "EMOTION_CONFUSION",
        "EMOTION_FRUSTRATION",
        "EMOTION_SELFDOUBT",
        "Q13_felt_like_real_system",
        "Q14_planned_next_move_based_on_system",
        "Q15_emotion_invoked_by_response",
        "Q16_strategy_adapted_to_behavior",
        "Q17_engage_differently_next_time"
    ]

    df_corr = df[selected_cols].dropna()

    # Compute correlation and p-values
    r_matrix = pd.DataFrame(index=selected_cols, columns=selected_cols, dtype=float)
    p_matrix = pd.DataFrame(index=selected_cols, columns=selected_cols, dtype=float)
    annotation_matrix = pd.DataFrame(index=selected_cols, columns=selected_cols, dtype=object)

    for i in selected_cols:
        for j in selected_cols:
            r, p = stats.pearsonr(df_corr[i], df_corr[j])
            r_matrix.loc[i, j] = r
            p_matrix.loc[i, j] = p
            sig = significance_marker(p)
            annotation_matrix.loc[i, j] = f"{r:.3f}{sig}"

    # Create Heatmap
    heatmap = go.Heatmap(
        z=r_matrix.values.astype(float),
        x=selected_cols,
        y=selected_cols,
        colorscale="RdBu",
        zmin=-1,
        zmax=1,
        text=annotation_matrix.values,
        texttemplate="%{text}",
        textfont={"size": 12},
        colorbar=dict(title="r")
    )

    fig = go.Figure(data=[heatmap])
    fig.update_layout(
        title="Correlation Heatmap",
        height=600,
        margin=dict(t=60, b=60, l=60, r=60),
    )

    return html.Div([
        html.H4("Correlation Analysis: Emotion States vs Q13–Q17", style={"textAlign": "center", "marginTop": "30px"}),
        dcc.Graph(figure=fig)
    ])

def significance_marker(p):
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    else:
        return ""

def plot_coefficient_heatmap(model, X_cols):
    coefs = model.params[X_cols]
    coefs = coefs.to_frame(name="Coefficient").T.round(3)
    fig = go.Figure(data=go.Heatmap(
        z=coefs.values,
        x=coefs.columns,
        y=["Regression Coefficients"],
        colorscale="RdBu",
        zmin=-1,
        zmax=1,
        text=coefs.values,
        texttemplate="%{text:.3f}",
        textfont={"size": 12}
    ))
    fig.update_layout(
        title="Regression Coefficients Heatmap",
        height=220,
        margin=dict(t=40, b=30, l=40, r=40)
    )
    return dcc.Graph(figure=fig)

def plot_correlation_heatmap(df, X_cols, y_col):
    """
    Plots a correlation matrix heatmap including predictors and the dependent variable,
    with significance (p < 0.05) marked with *.
    """
    all_cols = X_cols + [y_col]
    data = df[all_cols].dropna()
    
    n = len(all_cols)
    corr_matrix = np.zeros((n, n))
    pval_matrix = np.zeros((n, n))
    text_matrix = [["" for _ in range(n)] for _ in range(n)]

    for i in range(n):
        for j in range(n):
            corr, pval = stats.pearsonr(data[all_cols[i]], data[all_cols[j]])
            corr_matrix[i][j] = round(corr, 2)
            pval_matrix[i][j] = pval
            sig = ""
            if pval < 0.001:
                sig = "***"
            elif pval < 0.01:
                sig = "**"
            elif pval < 0.05:
                sig = "*"
            text_matrix[i][j] = f"{corr_matrix[i][j]}{sig}"

    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=all_cols,
        y=all_cols,
        colorscale="RdBu",
        zmin=-1,
        zmax=1,
        text=text_matrix,
        texttemplate="%{text}",
        textfont={"size": 12},
        hovertemplate="Correlation: %{z}<extra></extra>"
    ))

    fig.update_layout(
        title="Correlation Matrix (with Significance Stars)",
        height=450,
        margin=dict(t=40, b=40, l=60, r=60)
    )

    return dcc.Graph(figure=fig)

def get_model_summary_table(model):
    import pandas as pd
    from dash import dash_table

    summary_row = pd.DataFrame([{
        "R": round(model.rsquared ** 0.5, 3),
        "R²": round(model.rsquared, 3),
        "Adj. R²": round(model.rsquared_adj, 3),
        "Std. Error": round(model.mse_resid ** 0.5, 5),
        "F-statistic": round(model.fvalue, 3),
        "df1": int(model.df_model),
        "df2": int(model.df_resid),
        "Model p-value": round(model.f_pvalue, 4)
    }])

    table = dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in summary_row.columns],
        data=summary_row.to_dict("records"),
        style_table={"width": "95%", "margin": "auto"},
        style_cell={
            "textAlign": "center",
            "fontFamily": "Arial",
            "fontSize": "14px",
            "padding": "10px"
        },
        style_header={
            "fontWeight": "bold",
            "backgroundColor": "#dbe4f3",   # 柔和蓝灰
            "color": "#003366"
        },
        style_data_conditional=[
            {
                "if": {"filter_query": "{Model p-value} <= 0.05", "column_id": "Model p-value"},
                "backgroundColor": "#ffe0cc",  # 淡橙高亮
                "color": "#000000",
                "fontWeight": "bold"
            },
            {
                "if": {"column_id": "R"},
                "backgroundColor": "#f2f7fc"
            },
            {
                "if": {"column_id": "R²"},
                "backgroundColor": "#f2f7fc"
            },
            {
                "if": {"column_id": "Adj. R²"},
                "backgroundColor": "#f2f7fc"
            },
            {
                "if": {"column_id": "Std. Error"},
                "backgroundColor": "#fefefe"
            },
            {
                "if": {"column_id": "F-statistic"},
                "backgroundColor": "#fdf3e7"
            },
            {
                "if": {"column_id": "df1"},
                "backgroundColor": "#fdf3e7"
            },
            {
                "if": {"column_id": "df2"},
                "backgroundColor": "#fdf3e7"
            }
        ]
    )

    return table


def multivariate_regression_behavioral(df):
    X_cols = [
        "EMOTION_CONFIDENCE",
        "EMOTION_SURPRISE",
        "EMOTION_CONFUSION",
        "EMOTION_FRUSTRATION",
        "EMOTION_SELFDOUBT"
    ]
    y_col = "Behavioral_Perception"
    valid_df = df[X_cols + [y_col]].dropna()

    X = sm.add_constant(valid_df[X_cols])
    y = valid_df[y_col]
    model = sm.OLS(y, X).fit()

    return html.Div([
        html.H4("Multivariate Linear Regression: Behavioral Perception", style={"textAlign": "center", "marginTop": "30px"}),
        plot_coefficient_heatmap(model, X_cols),
        html.H4("Correlation Matrix : Predictors + Behavioral Perception", style={"textAlign": "center", "marginTop": "50px"}),
        plot_correlation_heatmap(valid_df, X_cols, y_col),
        html.H4("Regression Model Summary", style={"textAlign": "center", "marginTop": "30px"}),
        get_model_summary_table(model),
    ])


def plot_behavioral_perception_fit(df):
    """
    Fit a multivariate linear regression model to predict Behavioral_Perception
    using only emotional states, and plot predicted vs actual values.

    Parameters:
        df (pd.DataFrame): The input dataframe containing all necessary columns.

    Returns:
        A Plotly figure showing predicted vs. actual values.
    """
    # Define emotion-only predictors
    emotion_cols = [
        "EMOTION_CONFIDENCE",
        "EMOTION_SURPRISE",
        "EMOTION_CONFUSION",
        "EMOTION_FRUSTRATION",
        "EMOTION_SELFDOUBT"
    ]
    y_col = "Behavioral_Perception"

    # Drop rows with missing values
    valid_df = df[emotion_cols + [y_col]].dropna()
    X = sm.add_constant(valid_df[emotion_cols].astype(float))
    y = valid_df[y_col].astype(float)

    # Fit the regression model
    model = sm.OLS(y, X).fit()
    y_pred = model.predict(X)

    # Prepare figure
    fig = go.Figure()

    # Scatter plot: Actual vs Predicted
    fig.add_trace(go.Scatter(
        x=y,
        y=y_pred,
        mode="markers",
        name="Data Points",
        marker=dict(size=8, opacity=0.7, color="royalblue")
    ))

    # Add y = x reference line
    min_val = min(min(y), min(y_pred))
    max_val = max(max(y), max(y_pred))
    fig.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode="lines",
        name="y = x (Perfect Fit)",
        line=dict(dash="dash", color="gray")
    ))

    # Add R² annotation
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.05, y=0.95,
        showarrow=False,
        text=f"R² = {round(model.rsquared, 3)}",
        font=dict(size=14, color="black"),
        bgcolor="white",
        bordercolor="#ccc",
        borderwidth=1,
        borderpad=4
    )

    # Layout settings
    fig.update_layout(
        title="Predicted vs Actual Behavioral Perception (Emotion-Only Model)",
        xaxis_title="Actual Behavioral Perception",
        yaxis_title="Predicted Behavioral Perception",
        height=500,
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#f9f9f9",
        margin=dict(t=50, l=50, r=50, b=50),
        template="simple_white",
        yaxis=dict(
            range=[min_val - 0.1 * (max_val - min_val), max_val + 0.1 * (max_val - min_val)],
            ticks="outside",
            showgrid=True,
            gridcolor="#e0e0e0"
        )
    )

    return dcc.Graph(figure=fig)


#human attacker analysis

def human_top_command_bar(df):
    if "command" not in df.columns or df["command"].dropna().empty:
        return None

    top_cmds = df["command"].value_counts().head(15).reset_index()
    top_cmds.columns = ["Command", "Count"]

    fig = px.bar(
        top_cmds,
        x="Count",
        y="Command",
        orientation="h",
        title="Most Used Commands",
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        margin=dict(l=80, r=40, t=60, b=40)
    )

    return fig

def human_top_user_pie(df):
    if "username" not in df.columns or df["username"].dropna().empty:
        return None

    user_counts = df["username"].value_counts().head(10).reset_index()
    user_counts.columns = ["Username", "Count"]

    fig = px.pie(
        user_counts,
        names="Username",
        values="Count",
        title="Top Usernames"
    )

    fig.update_traces(
        sort=False,
        rotation=90,
        textposition="inside",
        textinfo="percent+label"
    )

    fig.update_layout(
        margin=dict(t=60, b=60, l=40, r=40)
    )

    return fig

def human_ip_duration_table(df):
    if not {"src_ip", "time_spent"}.issubset(df.columns):
        return html.Div("Required columns missing.")

    # Convert time_spent to numeric
    df["time_spent"] = pd.to_numeric(df["time_spent"], errors="coerce")
    
    # Group by IP and sum total duration
    grouped = (
        df[["src_ip", "time_spent"]]
        .dropna()
        .groupby("src_ip")
        .sum()
        .reset_index()
    )

    grouped["src_ip"] = grouped["src_ip"].apply(lambda ip: ".".join(ip.split(".")[:2]) + ".xx.xx")

    # Rename columns for display
    grouped = grouped.rename(columns={"src_ip": "IP Address", "time_spent": "Total Duration (seconds)"})
    grouped["Total Duration (seconds)"] = grouped["Total Duration (seconds)"].round(1)

    # Sort descending
    grouped = grouped.sort_values("Total Duration (seconds)", ascending=False)

    return dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in grouped.columns],
        data=grouped.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "padding": "5px"},
        style_header={"fontWeight": "bold", "backgroundColor": "#f8f8f8"},
        page_size=15
    )


def human_latest_commands_table(df):
    required_cols = {"timestamp", "src_ip", "command"}
    if not required_cols.issubset(df.columns):
        return html.Div("No command data.")

    df_filtered = df[df["command"].notna() & df["command"].str.strip().ne("")].copy()
    if df_filtered.empty:
        return html.Div("No command data available after filtering.")

    # Anonymize IPs
    df_filtered["src_ip"] = df_filtered["src_ip"].apply(
        lambda ip: ".".join(ip.split(".")[:2]) + ".xx.xx"
    )

    display_cols = ["timestamp", "src_ip", "username", "command"]
    display_cols = [col for col in display_cols if col in df_filtered.columns]

    return dash_table.DataTable(
        columns=[
            {"name": "Timestamp", "id": "timestamp"},
            {"name": "Source IP", "id": "src_ip"},
            {"name": "Username", "id": "username"},
            {"name": "Command", "id": "command"},
        ],
        data=df_filtered[display_cols].to_dict("records"),
        style_table={"width": "100%", "overflowX": "auto", "border": "1px solid #d3d3d3"},
        style_cell={
            "border": "1px solid #d3d3d3",
            "padding": "8px",
            "textAlign": "left",
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_cell_conditional=[
            {"if": {"column_id": "timestamp"}, "width": "25%"},
            {"if": {"column_id": "src_ip"}, "width": "20%"},
            {"if": {"column_id": "username"}, "width": "20%"},
            {"if": {"column_id": "command"}, "width": "35%"},
        ],
        style_header={"fontWeight": "bold", "backgroundColor": "#f8f8f8"},
        page_action="none",
        fixed_rows={"headers": True}
    )

# The following function is used for overview.py 
def interaction_bar_chart(node_dfs: dict):
    counts = {name: len(df) for name, df in node_dfs.items()}
    data = {
        "Node": list(counts.keys()),
        "Total Interactions": list(counts.values())
    }
    
    max_val = max(data["Total Interactions"])
    
    color_map = {
        "Appliance": "#636EFA",         
        "Lighting": "#EF553B",      
        "Thermostat": "#00CC96",    
        "Diagnostics": "#AB63FA",   
        "Snare": "#FFA15A",         
        "Miniprint": "#19D3F3"      
    }
    fig = px.bar(
        data_frame=data,
        x="Node",
        y="Total Interactions",
        color="Node",
        color_discrete_map=color_map,
        text="Total Interactions",
        # title="Total Interactions per Node"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
        margin=dict(t=40, l=20, r=20, b=40),
        yaxis=dict(range=[0, max_val * 1.1])  # y axis range with some padding
    )
    
    return dcc.Graph(figure=fig)

def custom_node_sort(nodes):
    nodes = list(nodes)
    if "Snare" in nodes:
        nodes.remove("Snare")
        return ["Snare"] + sorted(nodes)
    return sorted(nodes)

def common_ip_summary(dfs):
    if isinstance(dfs, dict):
        dfs_named = dfs
    else:
        # if dfs is a list, enumerate to create named dict
        dfs_named = {f"Node {i+1}": df for i, df in enumerate(dfs)}

    # record IP and the nodes they appear in
    ip_nodes_map = defaultdict(set)

    for node_name, df in dfs_named.items():
        if 'src_ip' in df.columns:
            unique_ips = set(df['src_ip'].dropna().unique())
            for ip in unique_ips:
                ip_nodes_map[ip].add(node_name)

    # keep only IPs that appear in at least 2 nodes
    filtered_ip_info = [
        {
            "IP Address": ip,
            "Appeared in Nodes": len(nodes),
            "Nodes": ", ".join(custom_node_sort(nodes))  # keep snare first if present
        }
        for ip, nodes in ip_nodes_map.items() if len(nodes) >= 2
    ]

    # 
    ip_df = pd.DataFrame(filtered_ip_info)
    ip_df = ip_df.sort_values(by="Appeared in Nodes", ascending=False)

    return html.Div([
        html.H4(f"{len(ip_df)} IPs appeared in ≥2 nodes."),
        dash_table.DataTable(
            columns=[
                {"name": "IP Address", "id": "IP Address"},
                {"name": "Appeared in Nodes", "id": "Appeared in Nodes"},
                {"name": "Nodes", "id": "Nodes", "presentation": "markdown"}
            ],
            data=ip_df.to_dict("records"),
            page_size=10,
            style_table={"overflowX": "auto", "marginTop": "15px"},
            style_cell={
                "textAlign": "left",
                "padding": "2px 4px",  
                "fontFamily": "monospace",
                "fontSize": "13px",    
                "lineHeight": "1.2",   
            },
            style_header={
                "backgroundColor": "#f4f4f4",
                "fontWeight": "bold"
            },
            style_data_conditional=[
                {
                    "if": {"filter_query": "{Appeared in Nodes} >= 5"},
                    "backgroundColor": "#ffe5e5"
                }
            ]
        )
    ])

def country_bar_chart(node_name, df):
    if 'country' not in df.columns:
        return html.Div(f"No country data available for {node_name}")

    country_counts = Counter(df['country'].dropna())
    most_common = country_counts.most_common(10)

    colors = {
        "Snare": "#1f77b4",        
        "Appliance": "#ff7f0e",    
        "Lighting": "#2ca02c",     
        "Thermostat": "#d62728",   
        "Diagnostics": "#9467bd",  
        "Miniprint": "#8c564b"    
    }
    node_color = colors.get(node_name, "#1f77b4") 

    fig = px.bar(
        x=[c[0] for c in most_common],
        y=[c[1] for c in most_common],
        labels={'x': 'Country', 'y': 'Count'},
        title=f"Top Source Countries - {node_name}",
        color_discrete_sequence=[node_color]
    )

    fig.update_layout(margin=dict(t=40, l=40, r=20, b=40))

    return html.Div([
        dcc.Graph(figure=fig)
    ], style={"width": "100%", "marginBottom": "30px"})
    
    
# Cowrie session duration computation
def compute_cowrie_session_durations(df):
    # Ensure necessary fields are present
    if not {"session", "eventid", "timestamp", "src_ip"}.issubset(df.columns):
        return pd.DataFrame(columns=["src_ip", "duration_sec"])
    
    connect_df = df[df["eventid"] == "cowrie.session.connect"].copy()
    closed_df = df[df["eventid"] == "cowrie.session.closed"].copy()

    merged = pd.merge(
        connect_df[["session", "src_ip", "timestamp"]],
        closed_df[["session", "timestamp"]],
        on="session",
        suffixes=("_start", "_end")
    )

    merged["duration_sec"] = (
        pd.to_datetime(merged["timestamp_end"]) - pd.to_datetime(merged["timestamp_start"])
    ).dt.total_seconds()

    return merged[["src_ip", "duration_sec"]]


# Snare session duration computation
def compute_snare_session_durations(df, time_gap_minutes=5):
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df[['timestamp', 'src_ip']].dropna().sort_values(by=['src_ip', 'timestamp'])

    df['time_diff'] = df.groupby('src_ip')['timestamp'].diff()
    df['new_session'] = (df['time_diff'] > pd.Timedelta(minutes=time_gap_minutes)).fillna(True)
    df['session_id'] = df.groupby('src_ip')['new_session'].cumsum()

    sessions = df.groupby(['src_ip', 'session_id'])['timestamp'].agg(['min', 'max'])
    sessions['duration_sec'] = (sessions['max'] - sessions['min']).dt.total_seconds()

    return sessions.reset_index()

# Miniprint: session duration computation
def compute_miniprint_session_durations(df):
    df = df.copy()
    print(df['event'].unique())
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    if df['timestamp'].dt.tz is not None:
        df['timestamp'] = df['timestamp'].dt.tz_localize(None)

    df = df[df['event'].isin(['open_conn', 'close_conn'])]
    df = df.drop_duplicates(subset=['timestamp', 'src_ip', 'event'])
    df = df[['timestamp', 'src_ip', 'event']].dropna().sort_values(by=['src_ip', 'timestamp'])

    durations = []

    for src_ip, group in df.groupby('src_ip'):
        stack = []
        for _, row in group.iterrows():
            if row['event'] == 'open_conn':
                stack.append(row['timestamp'])
            elif row['event'] == 'close_conn' and stack:
                start_time = stack.pop(0)
                durations.append((row['timestamp'] - start_time).total_seconds())

    return durations


# calculate average session duration for each node type
def average_duration_bar_chart(node_dfs: dict):
    avg_durations = {}

    for name, df in node_dfs.items():
        try:
            if name == "Snare":
                sessions = compute_snare_session_durations(df)
                avg_duration = sessions["duration_sec"].dropna().mean()
                print(f"[{name}] avg_duration:", avg_duration)
                avg_durations[name] = avg_duration

            elif name == "Miniprint":
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                if df['timestamp'].dt.tz is not None:
                    df['timestamp'] = df['timestamp'].dt.tz_localize(None)

                df = df[df["event"].isin(["connection", "connection_closed"])]
                df = df[["timestamp", "src_ip", "event"]].dropna()
                df = df.drop_duplicates(subset=["timestamp", "src_ip", "event"])
                df = df.sort_values(by=["src_ip", "timestamp"])
                df["is_open"] = df["event"] == "connection"
                df["session_id"] = df.groupby("src_ip")["is_open"].cumsum()

                grouped = df.groupby(["src_ip", "session_id", "event"])["timestamp"].min().unstack()
                grouped.dropna(inplace=True)

                durations = (grouped["connection_closed"] - grouped["connection"]).dt.total_seconds()
                avg_duration = durations.mean()
                print(f"[{name}] avg_duration:", avg_duration)
                avg_durations[name] = avg_duration

            elif 'duration' in df.columns:
                df['duration'] = pd.to_numeric(df['duration'], errors='coerce')
                avg_duration = df['duration'].dropna().mean()
                print(f"[{name}] avg_duration:", avg_duration)
                avg_durations[name] = avg_duration

            else:
                print(f"[{name}] has no duration info")
                avg_durations[name] = None

        except Exception as e:
            print(f"[{name}] error in duration calc:", e)
            avg_durations[name] = None

    # Prepare plot
    nodes = list(avg_durations.keys())
    values = [avg_durations[node] if avg_durations[node] is not None else 0 for node in nodes]

    df_plot = pd.DataFrame({
        "Node": nodes,
        "Avg Duration (s)": values
    })

    # add labels for bar chart
    df_plot["label"] = df_plot["Avg Duration (s)"].apply(lambda v: f"{v:.1f}" if pd.notna(v) else "N/A")

    color_map = {
        "Appliance": "#636EFA",
        "Lighting": "#EF553B",
        "Thermostat": "#00CC96",
        "Diagnostics": "#AB63FA",
        "Snare": "#FFA15A",
        "Miniprint": "#19D3F3"
    }

    fig = px.bar(
        df_plot,
        x="Node",
        y="Avg Duration (s)",
        color="Node",
        color_discrete_map=color_map,
        text="label"
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        showlegend=False,
        yaxis_range=[0, max(df_plot["Avg Duration (s)"].fillna(0)) * 1.2],
        # title="Average Session Duration per Node (seconds)"
    )

    return dcc.Graph(figure=fig)

from collections import Counter
import pandas as pd
from dash import dash_table, html

# Sub-function 1: For Appliance / Lighting / Thermostat
def get_common_resources_appliance_like(df):
    all_results = []

    # Honeytoken-based access
    honeytoken_df = df[
        (df["eventid"] == "cowrie.honeytoken") &
        df["input"].notna() &
        (df["input"] != "")
    ]
    honeytoken_counter = Counter(honeytoken_df["input"])
    honeytoken_df = pd.DataFrame(honeytoken_counter.items(), columns=["Resource", "Requests"])
    all_results.append(honeytoken_df)

    # Command-based access: cat, cd, head, tail
    if "input" in df.columns:
        input_series = df["input"].dropna().astype(str)
        pattern = r"(?:cat|tail|head|cd)\s+(/[\w/\.\-]+)"
        extracted_paths = input_series.str.extractall(pattern)[0]

        if not extracted_paths.empty:
            input_counter = Counter(extracted_paths)
            input_df = pd.DataFrame(input_counter.items(), columns=["Resource", "Requests"])
            all_results.append(input_df)

    if not all_results:
        return pd.DataFrame(columns=["Resource", "Requests"])

    combined = pd.concat(all_results)
    combined = combined.groupby("Resource", as_index=False)["Requests"].sum()
    combined = combined.sort_values(by="Requests", ascending=False).reset_index(drop=True)
    return combined

# Sub-function 2: Diagnostics command-based file extraction
def get_common_resources_diagnostics(df):
    if "input" not in df.columns:
        return pd.DataFrame(columns=["Resource", "Requests"])

    input_series = df["input"].dropna().astype(str)
    pattern = r"(?:cat|tail|head|cd)\s+(/[\w/\.\-]+)"
    extracted_paths = input_series.str.extractall(pattern)[0]

    if extracted_paths.empty:
        return pd.DataFrame(columns=["Resource", "Requests"])

    counter = Counter(extracted_paths)
    df_result = pd.DataFrame(counter.items(), columns=["Resource", "Requests"])
    df_result["Requests"] = df_result["Requests"].astype(int)
    df_result = df_result.sort_values(by="Requests", ascending=False).reset_index(drop=True)
    return df_result

# Sub-function 3: Miniprint file_name analysis
def get_common_resources_miniprint(df):
    filtered_df = df[df["event"] == "save_raw_print_job"].copy()
    if "file_name" not in filtered_df.columns:
        return pd.DataFrame(columns=["Resource", "Requests"])

    file_names = filtered_df["file_name"].dropna()
    counter = Counter(file_names)
    return pd.DataFrame(counter.items(), columns=["Resource", "Requests"]).sort_values(by="Requests", ascending=False)

# Sub-function 4: Snare HTTP request paths
def get_common_resources_snare(df):
    if "path" not in df.columns:
        return pd.DataFrame(columns=["Resource", "Requests"])

    # Clean path entries
    paths = df["path"].dropna()
    paths = paths[paths != "N/A"]

    if paths.empty:
        return pd.DataFrame(columns=["Resource", "Requests"])

    counter = Counter(paths)
    df_result = pd.DataFrame(counter.items(), columns=["Resource", "Requests"])
    df_result["Requests"] = df_result["Requests"].astype(int)
    df_result = df_result.sort_values(by="Requests", ascending=False).reset_index(drop=True)

    return df_result


# Function: generate one table per node
def common_access_resources_table(node_dfs: dict):
    table_components = []

    for node_name, df in node_dfs.items():
        # Select the appropriate handler
        if node_name in ["Appliance", "Lighting", "Thermostat"]:
            resources = get_common_resources_appliance_like(df)
        elif node_name == "Diagnostics":
            resources = get_common_resources_diagnostics(df)
        elif node_name == "Miniprint":
            resources = get_common_resources_miniprint(df)
        elif node_name == "Snare":
            resources = get_common_resources_snare(df)
        else:
            continue

        if resources.empty:
            table_components.append(html.Div(f"No accessed resources found for node: {node_name}"))
            continue

        resources["Requests"] = pd.to_numeric(resources["Requests"], errors="coerce").fillna(0).astype(int)
        resources.sort_values(by="Requests", ascending=False, inplace=True)

        table_components.append(
            html.Div([
                html.H3(
                    f"{node_name} - Accessed Endpoints",
                    style={
                        "textAlign": "center",
                        "fontWeight": "bold",
                        "fontSize": "22px",
                        "marginBottom": "16px"
                    }
                ),
                dash_table.DataTable(
                    columns=[{"name": c, "id": c} for c in resources.columns],
                    data=resources.to_dict("records"),
                    page_size=10,
                    style_table={
                        "overflowX": "auto",
                        "maxHeight": "500px",
                        "borderRadius": "8px",
                        "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.1)"
                    },
                    style_cell={
                        "textAlign": "left",
                        "padding": "8px 12px",
                        "fontFamily": "Courier New, monospace",
                        "fontSize": "14px",
                        "borderBottom": "1px solid #eee"
                    },
                    style_header={
                        "fontWeight": "bold",
                        "backgroundColor": "#f5f5f5",
                        "borderBottom": "2px solid #ccc"
                    },
                    style_data_conditional=[
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "#fafafa"
                        }
                    ]
                )
            ], style={"width": "48%", "padding": "1%"})
        )

    # Wrap every 2 tables into a row
    rows = []
    for i in range(0, len(table_components), 2):
        row = html.Div(
            children=table_components[i:i+2],
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "flexWrap": "wrap",
                "marginBottom": "40px"
            }
        )
        rows.append(row)

    if not rows:
        return html.Div("No resource access records available.")

    return html.Div([
        html.H2("Commonly Accessed Resources Across Honeypot Nodes", style={
            "textAlign": "center",
            "marginTop": "30px",
            "marginBottom": "30px",
            "fontSize": "28px",
            "fontWeight": "bold"
        }),
        *rows  # call rows
    ], style={"padding": "20px 5%"})


def sav_trait_distribution_bar_overview(df):
    """Show the distribution of self-reported personality traits with legend and no x-axis labels."""
    
    trait_mapping = {
        1: "Openness to Experience",
        2: "Conscientiousness",
        3: "Low Extraversion",
        4: "Low Agreeableness",
        5: "Low Neuroticism"
    }

    trait_series = df["Q1_personality_check"].map(trait_mapping)
    all_traits = list(trait_mapping.values())

    trait_counts = trait_series.value_counts().reindex(all_traits, fill_value=0).reset_index()
    trait_counts.columns = ["Trait", "Count"]
    trait_counts["Percentage"] = (trait_counts["Count"] / len(df) * 100).round(2)

    fig = px.bar(
        trait_counts,
        x="Trait",
        y="Count",
        color="Trait",
        text="Count",
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        yaxis=dict(title="Count", range=[0, max(trait_counts["Count"].max() + 5, 20)]),
        xaxis=dict(
            title=None,
            tickmode="array",
            tickvals=[],   # Hides tick labels
            showticklabels=False  # Explicitly disable tick labels
        ),
        height=450,
        width=750,
        margin=dict(t=50, b=60, l=40, r=40),
        showlegend=True  # Show legend for color mapping
    )

    return dcc.Graph(figure=fig)
