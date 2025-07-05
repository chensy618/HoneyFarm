# file: pages/lighting.py
from dash import html, dcc
from data_loader import load_and_process_log, enrich_geo
from components import *

def lighting_layout():
    df = load_and_process_log("./data_visualization/cowrie.json.2025-06-27")
    df = enrich_geo(df)

    return html.Div([
        html.H1("Lighting Node Dashboard"),
        html.Div([
            html.Div([
                html.H3("Top 15 Commands"),
                dcc.Graph(figure=top_command_bar(df))
            ], style={"width": "48%", "display": "inline-block"}),

            html.Div([
                html.H3("Top 20 Attacker IPs"),
                dcc.Graph(figure=top_ip_pie(df))
            ], style={"width": "48%", "display": "inline-block", "float": "right"})
        ], style={"padding": "20px 5%"}),

        html.Div([
            html.Div([
                html.H3("Top 20 Attempted Users"),
                dcc.Graph(figure=top_user_pie(df))
            ], style={"width": "48%", "display": "inline-block"}),

            html.Div([
                html.H3("Geo Origin Wordcloud"),
                wordcloud_img(df)
            ], style={"width": "48%", "display": "inline-block", "float": "right"})
        ], style={"padding": "20px 5%"}),

        html.H3("Latest Commands Executed"),
        latest_commands_table(df)
    ])