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
    #personality_traits_bar,
    most_requested_endpoints_table,
    node_navigation   
)

def diagnostics_layout():
    df = load_and_process_log("./data_visualization/raw_data/merged/filtered+merged_diagnostics.json")
    df = enrich_geo(df)

    def two_column_block(left_title, left_component, right_title, right_component):
        return html.Div([
            html.Div([
                html.H3(left_title),
                left_component
            ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top"}),

            html.Div([
                html.H3(right_title),
                right_component
            ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top"})
        ], style={
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "flex-start",
            "padding": "20px 5%"
        })

    return html.Div([
        
        node_navigation("Diagnostics"),
        
        html.H1("Diagnostics Node Dashboard"),

        two_column_block(
            "Top 15 Commands", dcc.Graph(figure=top_command_bar(df)),
            "Top 10 Attacker IPs", dcc.Graph(figure=top_ip_pie(df))
        ),

        two_column_block(
            "Top 10 Attempted Users", dcc.Graph(figure=top_user_pie(df)),
            "Source IP Summary Table", ip_summary_table(df)
        ),

        html.Div([
            html.H3("Geographic Distribution of Attacker IPs"),
            html.Div(geo_heatmap(df), style={"width": "100%"})
        ], style={"padding": "20px 5%"}),

        two_column_block(
            "Event Type Distribution", dcc.Graph(figure=event_type_bar_with_line(df)),
            "Commands Summary Table", commands_summary_table(df)
        ),

        html.Div([
        html.H3("Most Requested Endpoints"),
        most_requested_endpoints_table(df)
         ], style={"padding": "20px 5%", "maxWidth": "90%", "margin": "0 auto"}),

        html.Div([
        html.H3("Time-of-Day Analysis of Malicious Activity"),
        dcc.Graph(figure=activity_hour_bar(df))
        ], style={"padding": "20px 5%", "maxWidth": "90%", "margin": "0 auto"}),

        html.Div([
            html.H3("IP Session Duration"),
            ip_duration_table(df)
        ], style={"padding": "20px 5%", "maxWidth": "90%", "margin": "0 auto"}),

        html.Div([
            html.H3("Top IPs Based on Duration"),
            top_10_duration_ips_table(df)
        ], style={"padding": "20px 5%", "maxWidth": "90%", "margin": "0 auto"}),


        html.Div([
            html.H3("Executed Commands"),
            latest_commands_table(df)
        ], style={"maxWidth": "90%", "margin": "0 auto"})
    ])
