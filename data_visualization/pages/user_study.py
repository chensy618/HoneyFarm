# file: pages/user_study.py
from dash import html

def user_study_layout():
    return html.Div([
        html.H1("Honeyfarm User Study Dashboard"),
        html.H4("User Study Analysis and Insights"),
        html.Div("This page will be used to display insights and analysis from the user study conducted."),
    ], style={
        "maxWidth": "900px",
        "margin": "auto",
        "padding": "40px"
    })
