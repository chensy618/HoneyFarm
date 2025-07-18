# file: pages/human_attacker.py
from dash import html, dcc
import pandas as pd
from components import (
    human_top_command_bar,
    human_top_user_pie,
    human_ip_duration_table,
    human_latest_commands_table
)

# Load CSV with proper delimiter
df = pd.read_csv("./data_visualization/raw_data/human/appliance_human_attackers.csv", sep=";") #update paths !!!!
ef = pd.read_csv("./data_visualization/raw_data/human/lighting_human_attacker.csv", sep=";")
jf = pd.read_csv("./data_visualization/raw_data/human/thermostat_human_attackers.csv", sep=";")
uf = pd.read_csv("./data_visualization/raw_data/human/diagnostics_human_attackers.csv", sep=";")

def human_attackers_appliance_layout():
    return html.Div([
        html.H1("Human Attacker Data Analysis", style={"paddingBottom": "50px"}),
        html.H2("Appliance Node"),
        html.Div([
            html.Div([
                html.H4("Top Commands"),
                dcc.Graph(figure=human_top_command_bar(df))
            ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top"}),

            html.Div([
                html.H4("Top Usernames"),
                dcc.Graph(figure=human_top_user_pie(df))
            ], style={"width": "48%", "display": "inline-block", "marginLeft": "4%", "verticalAlign": "top"})
        ], style={"padding": "20px 5%"}),

        html.Div([
            html.H4("IP Session Duration"),
            human_ip_duration_table(df)
        ], style={"padding": "20px 5%"}),

        html.Div([
            html.H4("All Executed Commands"),
            human_latest_commands_table(df)
        ], style={"padding": "20px 5%"}),

        html.H2("Lighting Node"),
        html.Div([
            html.Div([
                html.H4("Top Commands"),
                dcc.Graph(figure=human_top_command_bar(ef))
            ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top"}),

            html.Div([
                html.H4("Top Usernames"),
                dcc.Graph(figure=human_top_user_pie(ef))
            ], style={"width": "48%", "display": "inline-block", "marginLeft": "4%", "verticalAlign": "top"})
        ], style={"padding": "20px 5%"}),

        html.Div([
            html.H4("IP Session Duration"),
            human_ip_duration_table(ef)
        ], style={"padding": "20px 5%"}),

        html.Div([
            html.H4("All Executed Commands"),
            human_latest_commands_table(ef)
        ], style={"padding": "20px 5%"}),

        html.H2("Thermostat Node"),
        html.Div([
            html.Div([
                html.H4("Top Commands"),
                dcc.Graph(figure=human_top_command_bar(jf))
            ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top"}),

            html.Div([
                html.H4("Top Usernames"),
                dcc.Graph(figure=human_top_user_pie(jf))
            ], style={"width": "48%", "display": "inline-block", "marginLeft": "4%", "verticalAlign": "top"})
        ], style={"padding": "20px 5%"}),

        html.Div([
            html.H4("IP Session Duration"),
            human_ip_duration_table(jf)
        ], style={"padding": "20px 5%"}),

        html.Div([
            html.H4("All Executed Commands"),
            human_latest_commands_table(jf)
        ], style={"padding": "20px 5%"}),

        html.H2("Diagnostics Node"),
        html.Div([
            html.Div([
                html.H4("Top Commands"),
                dcc.Graph(figure=human_top_command_bar(uf))
            ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top"}),

            html.Div([
                html.H4("Top Usernames"),
                dcc.Graph(figure=human_top_user_pie(uf))
            ], style={"width": "48%", "display": "inline-block", "marginLeft": "4%", "verticalAlign": "top"})
        ], style={"padding": "20px 5%"}),

        html.Div([
            html.H4("IP Session Duration"),
            human_ip_duration_table(uf)
        ], style={"padding": "20px 5%"}),

        html.Div([
            html.H4("All Executed Commands"),
            human_latest_commands_table(uf)
        ], style={"padding": "20px 5%"})
    ])

