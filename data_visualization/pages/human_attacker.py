# file: pages/human_attacker.py
from dash import html

def human_attacker_layout():
    return html.Div([
        html.H1("Honeyfarm Human Attacker Dashboard"),
        html.H4("Human Attacker Analysis and Insights"),
        html.Div("This page will be used to display insights and analysis from the human attacker study conducted."),
    ], style={
        "maxWidth": "900px",
        "margin": "auto",
        "padding": "40px"
    })
