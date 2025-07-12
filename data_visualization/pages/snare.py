# file: pages/snare.py
from dash import html, dcc
from data_loader import load_snare_log_data, enrich_geo, load_snare_err_data
from components import (
    snare_err_top_ip_table,
    snare_err_path_table,
    snare_err_attack_frequency,
    snare_log_classify_behavior,
    snare_log_behavior_pie,
    snare_log_top_paths_bar,
    snare_log_status_table,
    snare_log_top_ip_pip_chart,
    snare_log_top_path_table,
    snare_log_ip_heatmap,
    snare_log_attack_frequency
)

def snare_layout():
    # load and process snare.log data
    df = load_snare_log_data("./data_visualization/raw_data/snare/snare.log")
    df = snare_log_classify_behavior(df)
    df = enrich_geo(df)

    # load and process snare.err data
    df_err = load_snare_err_data("./data_visualization/raw_data/snare/snare.err")
    df_err = df_err.rename(columns={"ip": "src_ip"})
    df_err = enrich_geo(df_err)

    return html.Div([
        html.H1("Snare Node Dashboard"),

        html.H2("Section 1: Snare Log Analysis (snare.log)"),
        # add pie chart for top source IPs
        html.Div([
            html.Div(snare_log_top_ip_pip_chart(df), style={"width": "48%", "display": "inline-block"}),
            html.Div(snare_log_top_path_table(df), style={"width": "48%", "display": "inline-block", "float": "right"})
        ], style={"padding": "20px 5%"}),
        
        # add ip heatmap 
        html.Div([
            html.H3("Geographic Distribution of Attacker IPs"),
            html.Div(snare_log_ip_heatmap(df), style={"width": "100%", "display": "inline-block"})
        ], style={"padding": "20px 5%"}),

        # add frequency analysis
        html.Div([
            snare_log_attack_frequency(df),
        ], style={"padding": "20px 5%"}),

        html.Div([
            html.H3("Raw Request Events Behavior Analysis"),
            html.Div(snare_log_status_table(df), style={"width": "100%", "display": "inline-block"})
        ], style={"padding": "20px 5%"}),

        html.H2("Section 2: Snare Error Analysis (snare.err)"),
        html.Div([
            html.Div(snare_err_top_ip_table(df_err), style={"width": "48%", "display": "inline-block"}),
            html.Div(snare_err_path_table(df_err), style={"width": "48%", "display": "inline-block", "float": "right"})
        ], style={"padding": "20px 5%"}),

        html.Div([
            snare_err_attack_frequency(df_err)
        ], style={"padding": "0 5%"}),
    ])
