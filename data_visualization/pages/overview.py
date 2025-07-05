# file: pages/overview.py
from dash import html

def overview_layout():
    return html.Div([
        html.H1("Honeyfarm Overview Dashboard"),
        html.H4("Summary and Comparison across Nodes"),
        html.Div("This page will be used to display aggregate metrics and visual comparisons across Appliance, Lighting, Thermostat, Diagnostics, Snare, and Miniprint nodes."),
        html.Br(),
        html.Div("(Placeholder for aggregated charts: total logins, top commands across all, stage distributions, cross-node heatmaps, etc.)")
    ], style={
        "maxWidth": "900px",
        "margin": "auto",
        "padding": "40px"
    })
