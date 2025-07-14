# file: components.py
import base64
import os
from dash import html, dash_table
from wordcloud import WordCloud
import plotly.express as px
from dash import dcc
import plotly.graph_objects as go
import pandas as pd
from collections import Counter

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
        margin=dict(l=250, r=80, t=50, b=50),  
        yaxis=dict(autorange="reversed"),
    )

    fig.update_traces(
        textposition="outside",
        marker_color="cornflowerblue"
    )

    return fig


def top_ip_pie(df):
    if "src_ip" not in df.columns:
        return html.Div("No attacker IP data.")
    ip_count = df["src_ip"].value_counts().head(10).reset_index()
    ip_count.columns = ["src_ip", "count"]
    return px.pie(ip_count, names="src_ip", values="count", title="Top 10 Attacker IPs")

def top_user_pie(df):
    user_col = "username" if "username" in df.columns else "user" if "user" in df.columns else None
    if not user_col:
        return html.Div("No attempted user data.")
    user_count = df[user_col].value_counts().head(10).reset_index()
    user_count.columns = ["username", "count"]
    return px.pie(user_count, names="username", values="count", title="Top 10 Attempted Users")

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

    return dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in merged.columns],
        data=merged.to_dict("records"),
        style_cell={"textAlign": "left", "padding": "5px"},
        style_header={"fontWeight": "bold", "backgroundColor": "#f8f8f8"},
        style_table={"overflowX": "auto"},
        page_size=15
    )

def latest_commands_table(df):
    """
    Create a DataTable of all executed commands,
    dropping empty input, and adding src_ip for each command.
    """

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

def most_requested_endpoints_table(df):
    from dash import dash_table, html

    # Filter for honeytoken events with valid input
    honeytoken_df = df[
        (df["eventid"] == "cowrie.honeytoken") & 
        df["input"].notna() & (df["input"] != "")
    ].copy()

    if honeytoken_df.empty:
        return html.Div("No honeytoken file/folder requests found.")

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
        geo_grouped, lat="latitude", lon="longitude", z="count", radius=15,
        center=dict(lat=20, lon=0), zoom=1,
        mapbox_style="carto-positron"
    )
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
        geo_grouped, lat="latitude", lon="longitude", z="count", radius=15,
        center=dict(lat=20, lon=0), zoom=1,
        mapbox_style="carto-positron",
        # title="Geographic Heatmap of Interactions"
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
    df["hour"] = df["timestamp"].dt.floor("h") 
    freq_df = df.groupby("hour").size().reset_index(name="count")

    fig = px.line(
        freq_df,
        x="hour",
        y="count",
        title="Attack Frequency Over Time (per Hour)",
        labels={"hour": "Time", "count": "Requests"},
        markers=True,
        text="count"
    )

    fig.update_traces(textposition="top center")

    fig.update_layout(
        title={
            "text": "Attack Frequency Over Time (per Hour)",
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
        {"name": "Behavior", "id": "behavior"},
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
        geo_grouped, lat="latitude", lon="longitude", z="count", radius=15,
        center=dict(lat=20, lon=0), zoom=1,
        mapbox_style="carto-positron",
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
    )
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
        title="Hourly Request Distribution"
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



