# file: pages/miniprint.py
from dash import html, dcc
from data_loader import load_miniprint_file, enrich_geo
from components import (
    miniprint_top_ip_pie,
    miniprint_event_type_bar,
    miniprint_event_trend_line,
    miniprint_job_table,
    miniprint_activity_hour_bar,
    miniprint_ip_summary_table,
    miniprint_geo_heatmap,
    miniprint_job_detail_table,
    miniprint_merged_table,
    miniprint_event_type_bar_with_line,
    miniprint_event_type_pie,
    node_navigation
)


def miniprint_layout():
    df = load_miniprint_file("./data_visualization/raw_data/miniprint/miniprint_merged.json")
    df = enrich_geo(df)
    # print(df[["src_ip", "latitude", "longitude"]].dropna().head(10))
    # print("Total points with geo info:", df.dropna(subset=["latitude", "longitude"]).shape[0])
    # print("=== After Enrich ===")
    # print(df[["src_ip", "latitude", "longitude"]].dropna().head(10))
    # print("Total points with geo info:", df.dropna(subset=["latitude", "longitude"]).shape[0])

    return html.Div([

        node_navigation("MiniPrint"),

        html.H1("MiniPrint Node Dashboard"),

        html.Div([
            html.Div([
                html.H3("Event Type Distribution"),
                dcc.Graph(figure=miniprint_event_type_pie(df))
            ], style={"width": "48%", "display": "inline-block"}),
            
             
            html.Div([
                html.H3("Top Source IP Summary Table"),
                miniprint_ip_summary_table(df)
            ], style={"width": "48%", "display": "inline-block", "float": "right"})
        ], style={"padding": "20px 5%"}),

        html.Div([
            
            html.Div([
                html.H3("Event Type Distribution"),
                dcc.Graph(figure=miniprint_event_type_bar_with_line(df))
            ], style={"width": "48%", "display": "inline-block"}),
            
            html.Div([
                html.H3("Top 10 Source IPs"),
                dcc.Graph(figure=miniprint_top_ip_pie(df))
            ], style={"width": "48%", "display": "inline-block"}),
        ], style={"padding": "20px 5%"}),
        
        html.Hr(),
        
        html.Div([
            html.H3("Geo Heatmap of Attacker IPs"),
            miniprint_geo_heatmap(df)
        ], style={"width": "96%", "display": "inline-block", "float": "right"}),
          
        html.Div([
            html.Div([
                html.H3("Print Job Event Trend Over Time"),
                dcc.Graph(figure=miniprint_event_trend_line(df))
            ], style={"width": "100%", "display": "inline-block"}),

            html.Div([
                html.H3("Time-of-Day Analysis of Malicious Activity"),
                dcc.Graph(figure=miniprint_activity_hour_bar(df))
            ], style={"width": "100%", "display": "inline-block"})
        ], style={"padding": "20px 5%"}),
        
        html.Div([
            html.H1("MiniPrint Job Analysis"),
            # miniprint_job_table(df),
            # miniprint_job_detail_table(df),  # detailed job content
            miniprint_merged_table(df)  # summarized table
        ]),

    ])
