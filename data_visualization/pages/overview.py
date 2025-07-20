# file: pages/overview.py
from dash import dcc
from dash import html
from data_loader import (
    enrich_geo,
    load_and_process_log, 
    load_snare_log_data, 
    load_miniprint_file,
    load_sav_data
)
from components import (
    interaction_bar_chart,
    common_ip_summary,
    country_bar_chart,
    average_duration_bar_chart,
    sav_trait_distribution_bar_overview,
    common_access_resources_table
)

def country_charts_grid(dfs_dict):
    return html.Div([
        html.H2("Top Source Countries per Node", style={
            "textAlign": "center",
            "marginTop": "50px",
            "marginBottom": "20px"
        }),

        html.Div([
            html.Div(country_bar_chart(name, df), style={
                "flex": "1 0 30%",      
                "maxWidth": "33.3%",
                "boxSizing": "border-box",
                "padding": "10px"
            })
            for name, df in dfs_dict.items()
        ], style={
            "display": "flex",
            "flexWrap": "wrap",
            "justifyContent": "center",
            "padding": "0 20px"
        })
    ])


def overview_layout():

    appliance_df = load_and_process_log("./data_visualization/raw_data/merged/filtered+merged_appliances.json")
    lighting_df = load_and_process_log("./data_visualization/raw_data/merged/filtered+merged_lighting.json")
    thermostat_df = load_and_process_log("./data_visualization/raw_data/merged/filtered+merged_thermostat.json")
    diagnostics_df = load_and_process_log("./data_visualization/raw_data/merged/filtered+merged_diagnostics.json")
    snare_df = load_snare_log_data("./data_visualization/raw_data/snare/snare.log")
    miniprint_df = load_miniprint_file("./data_visualization/raw_data/miniprint/miniprint_merged.json")
    user_study_df = load_sav_data("./data_visualization/raw_data/user_study/user_study.sav")
    
    appliance_df = enrich_geo(appliance_df)
    lighting_df = enrich_geo(lighting_df)
    thermostat_df = enrich_geo(thermostat_df)
    diagnostics_df = enrich_geo(diagnostics_df)
    snare_df = enrich_geo(snare_df)
    miniprint_df = enrich_geo(miniprint_df)

    dfs_dict = {
        "Snare": snare_df,
        "Appliance": appliance_df,
        "Lighting": lighting_df,
        "Thermostat": thermostat_df,
        "Diagnostics": diagnostics_df,
        "Miniprint": miniprint_df,
    }

    df_list = list(dfs_dict.values())
    df_named_list = list(dfs_dict.items())
    # print("df_named_list:", df_named_list)
    
    return html.Div([
        html.H1("Honeyfarm Overview Dashboard"),
        
        html.H2("Summary and Comparison across Nodes"),
        
        html.Div([
            html.Div([
                html.H2("Total Interactions per Node", style={"fontWeight": "bold", "marginBottom": "10px", "textAlign": "center"}),
                html.Div(interaction_bar_chart(dfs_dict))
            ], style={
                "width": "48%",
                "display": "inline-block",
                "verticalAlign": "top",
                "paddingRight": "2%"
            }),

            html.Div([
                html.H2("Personality Trait Distribution of the User Study", style={"fontWeight": "bold", "marginBottom": "10px", "textAlign": "center"}),
                html.Div(sav_trait_distribution_bar_overview(user_study_df))
            ], style={
                "width": "48%",
                "display": "inline-block",
                "verticalAlign": "top"
            })
        ], style={"padding": "20px 5%", "display": "flex", "justifyContent": "space-between"}),
                
        html.Hr(),
        
        html.Div([
            html.Div([
                html.H2("Common IPs across Nodes", style={
                    "textAlign": "center",
                    "marginBottom": "10px"
                }),
                html.Div(common_ip_summary(dfs_dict), style={
                    "Width": "96%",
                    "margin": "0 auto",
                    "padding": "20px",
                    "boxShadow": "0 0 10px rgba(0,0,0,0.05)",
                    "backgroundColor": "#fafafa",
                    "borderRadius": "8px"
                })
            ])
        ]),
        
        html.Hr(),
        
        country_charts_grid(dfs_dict),
        
        html.Hr(),
        html.Div([
            html.H2("Average Session Duration per Node", style={
                "textAlign": "center",
                "marginBottom": "10px"
            }),
            html.Div(average_duration_bar_chart(dfs_dict), style={
                "Width": "96%",
                "margin": "0 auto",
                "padding": "5 px",
                "boxShadow": "0 0 10px rgba(0,0,0,0.05)",
                "backgroundColor": "#fafafa",
                "borderRadius": "8px"
            })
        ]),
        
        html.Hr(),

        common_access_resources_table(dfs_dict)
        
    ], style={"padding": "20px 5%"})
