# file: pages/diagnostics.py

from dash import html, dcc
from data_loader import load_and_process_log, enrich_geo
from components import (
    top_command_bar,
    top_ip_pie,
    top_user_pie,
    #wordcloud_img,
    latest_commands_table,
    ip_summary_table,
    geo_heatmap,
    activity_hour_bar,
    commands_summary_table,
    event_type_bar_with_line,
    ip_duration_table,
    top_10_duration_ips_table,
    personality_traits_bar,
    most_requested_endpoints_table   
)

def diagnostics_layout():
    df = load_and_process_log("./data_visualization/raw_data/merged/filtered+merged_diagnostics.json")
    personality_log_file = "./data_visualization/raw_data/diagnostics/diagnostics-json.log"
    df = enrich_geo(df)

    return html.Div([
        html.H1("Diagnostics Node Dashboard"),

        html.Div([
            html.Div([
                html.H3("Top 15 Commands"),
                dcc.Graph(figure=top_command_bar(df))
            ], style={"width": "48%", "display": "inline-block"}),

            html.Div([
                html.H3("Top 10 Attacker IPs"),
                dcc.Graph(figure=top_ip_pie(df))
            ], style={"width": "48%", "display": "inline-block", "float": "right"})
        ], style={"padding": "20px 5%"}),

        html.Div([
            html.Div([
                html.H3("Top 10 Attempted Users"),
                dcc.Graph(figure=top_user_pie(df))
            ], style={
                "width": "48%", 
                "display": "inline-block", 
                "verticalAlign": "top"
        }),

        html.Div([
                html.H3("Source IP Summary Table"),
                ip_summary_table(df)
            ], style={
                "width": "48%", 
                "display": "inline-block", 
                "float": "right",
                "verticalAlign": "top"
            })
        ], style={"padding": "20px 5%"}),

        html.Div([
            html.H3("Geographic Distribution of Attacker IPs"),
            html.Div(geo_heatmap(df), style={"width": "100%", "display": "inline-block"})
        ], style={"padding": "20px 5%"}),

        html.Div([
            html.H3("Top Attacker Personality Traits"),
            personality_traits_bar(personality_log_file)
        ], style={"width": "48%", "padding": "20px 5%"}),

        html.Div([
            html.Div([
                html.H3("Event Type Distribution"),
                dcc.Graph(figure=event_type_bar_with_line(df))
            ], style={"width": "48%", "display": "inline-block"}),

            html.Div([
                html.H3("Commands Summary Table"),
                commands_summary_table(df)
            ], style={"width": "48%", "display": "inline-block", "float": "right"})
        ], style={"padding": "20px 5%"}),

        html.Div([
                html.H3("Most Requested Endpoints", style={"margin-bottom": "10px"}),
                most_requested_endpoints_table(df)
        ], style={"width": "48%", "display": "inline-block"}),

        html.Div([
            html.H3("Time-of-Day Analysis of Malicious Activity"),
            dcc.Graph(figure=activity_hour_bar(df))
        ], style={"width": "100%", "display": "inline-block", "padding": "20px 5%"}),

        html.Div([
            html.H3("IP Session Duration"),
            ip_duration_table(df)
        ], style={"width": "100%", "padding": "20px 5%"}),
        html.Div([
            html.H3("Top IPs Based on Duration"),
            top_10_duration_ips_table(df)
        ], style={"width": "100%", "padding": "20px 5%"}),

        html.H3("Executed Commands"),
        latest_commands_table(df)
    ])
