# file: components.py
import base64
import os
from dash import html, dash_table
from wordcloud import WordCloud
import plotly.express as px
from dash import dcc
import plotly.graph_objects as go



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
    # 过滤 append 和 save 事件
    filtered_df = df[df["event"].isin(["append_raw_print_job", "save_raw_print_job"])].copy()

    # 显示 job_text 或 file_name
    def extract_content(row):
        if row["event"] == "append_raw_print_job":
            return row.get("job_text", "")[:200]  # 限制展示长度
        elif row["event"] == "save_raw_print_job":
            return row.get("file_name", "")
        return ""

    filtered_df["Content"] = filtered_df.apply(extract_content, axis=1)

    # 提取并简化展示字段
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





