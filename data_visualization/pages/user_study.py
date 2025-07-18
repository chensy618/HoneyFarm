# file: pages/user_study.py
from dash import html
from data_loader import load_sav_data
from components import (
    sav_trait_distribution_bar,
    sav_confidence_bar,
    likert_bar_chart,
    likert_pie_chart,
    likert_line_chart,
    analyze_q7_confidence,
    analyze_q8_surprise,
    analyze_q9_confusion,
    analyze_q10_frustration,
    analyze_q11_selfdoubt,
    analyze_q12_emotion_transitions,  
)


def user_study_layout():

    df = load_sav_data("./data_visualization/raw_data/user_study/user_study.sav")
    # print(df.columns.tolist())
    
    return html.Div([
        html.H1("Honeyfarm User Study Dashboard"),
        html.H2("User Study Analysis and Insights"),

        html.H2("Descriptive Statistics"),
        html.Div([
            html.Div([
                html.H4("Personality Trait Distribution", style={"fontWeight": "bold", "marginBottom": "10px"}),
                html.Div(sav_trait_distribution_bar(df))
            ], style={
                "width": "48%",
                "display": "inline-block",
                "verticalAlign": "top",
                "paddingRight": "2%"
            }),

            html.Div([
                html.H4("Confidence Level", style={"fontWeight": "bold", "marginBottom": "10px"}),
                html.Div(sav_confidence_bar(df))
            ], style={
                "width": "48%",
                "display": "inline-block",
                "verticalAlign": "top"
            })
        ], style={"padding": "20px 5%", "display": "flex", "justifyContent": "space-between"}),

        html.Hr(),
        
        html.Div([

            html.Div([
                html.H3("Surprise Level"),
                likert_pie_chart(df, "Q3_surprise_experience", "Q3: How surprised were you by the system's responses or behaviour?")
            ], style={"width": "48%", "display": "inline-block", "paddingRight": "2%"}),

            html.Div([
                html.H3("Confusion Level"),
                likert_pie_chart(df, "Q4_confused_experience", "Q4: How confused did you feel during the process?")
            ], style={"width": "48%", "display": "inline-block"}),

        ], style={"padding": "20px 5%"}),

        html.Hr(),
        
        html.Div([

            html.Div([
                html.H3("Frustration Level"),
                likert_pie_chart(df, "Q5_frustrated_experience", "Q5: How frustrated did you feel at any point during the interaction?")
            ], style={"width": "48%", "display": "inline-block", "paddingRight": "2%"}),

            html.Div([
                html.H3("Self-Doubt Level"),
                likert_pie_chart(df, "Q6_selfdoubt_experience", "Q6: To what extent did you experience self-doubt?")
            ], style={"width": "48%", "display": "inline-block"}),

        ], style={"padding": "20px 5%"}),

        html.Hr(),
        
        html.Div([
            html.Div([
                html.H3("Confidence Triggers"),
                analyze_q7_confidence(df)
            ], style={"width": "48%", "display": "inline-block", "paddingRight": "2%"}),
            
            html.Div([
                html.H3("Surprise Triggers"),
                analyze_q8_surprise(df)
            ], style={"width": "48%", "display": "inline-block"})
        ], style={"padding": "20px 5%"}),

        html.Hr(),
        
        html.Div([
            html.Div([
                html.H3("Frustration Triggers"),
                analyze_q10_frustration(df)
            ], style={"width": "48%", "display": "inline-block", "paddingRight": "2%"}),

            html.Div([
                html.H3("Self-Doubt Triggers"),
                analyze_q11_selfdoubt(df)
            ], style={"width": "48%", "display": "inline-block"})
        ], style={"padding": "20px 5%"}),

        html.Hr(),
        
        html.Div([
            html.Div([
                html.H3("Emotion Transitions"),
                analyze_q12_emotion_transitions(df)
            ], style={"width": "100%", "display": "inline-block", "paddingRight": "2%"}),
        ], style={"padding": "20px 5%"}),

        html.Hr(),
        
        html.Div([

            html.Div([
                html.H3("The Realism of the Emulated System"),
                likert_line_chart(df, "Q13_felt_like_real_system", "Q13: I felt like I was interacting with a real system")
            ], style={"width": "48%", "display": "inline-block", "paddingRight": "2%"}),

            html.Div([
                html.H3("Planning Behavior Variation"),
                likert_line_chart(df, "Q14_planned_next_move_based_on_system", "Q14: The system responses influenced how I planned my next move")
            ], style={"width": "48%", "display": "inline-block"}),

        ], style={"padding": "20px 5%"}),

        html.Hr(),
        
        html.Div([

            html.Div([
                html.H3("Emotion Transitions"),
                likert_line_chart(df, "Q15_emotion_invoked_by_response", "Q15: The responses invoke my emotional transitions.")
            ], style={"width": "48%", "display": "inline-block", "paddingRight": "2%"}),

            html.Div([
                html.H3("Adaptive Strategies"),
                likert_line_chart(df, "Q16_strategy_adapted_to_behavior", "Q16:  I tried to adapt my strategy based on the system’s behavior.")
            ], style={"width": "48%", "display": "inline-block"})
        ], style={"padding": "20px 5%"}),

        html.Hr(),
        
        html.Div([
                html.H3("Engagement Reflection"),
                likert_line_chart(df, "Q17_engage_differently_next_time", "Q17: I would act differently if I were to engage with the system again.")
            ], style={"width": "100%", "display": "inline-block", "paddingRight": "2%"}),

        html.Div("Further analysis on per-trait emotion breakdown and correlation studies coming soon...", style={
            "textAlign": "center",
            "marginTop": "40px",
            "fontStyle": "italic"
        })
    ])

