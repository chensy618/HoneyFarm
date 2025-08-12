from dash import Dash, html, dcc, Input, Output
from pages.appliance import appliance_layout
from pages.lighting import lighting_layout
from pages.thermostat import thermostat_layout
from pages.diagnostics import diagnostics_layout
from pages.snare import snare_layout
from pages.miniprint import miniprint_layout
from pages.overview import overview_layout
from pages.user_study import user_study_layout
from pages.human_attacker import human_attackers_appliance_layout
import base64

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Encode icon image
with open("./data_visualization/assets/honeyfarm_logo1.png", "rb") as f:
    icon_data = base64.b64encode(f.read()).decode("utf-8")

app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div(id="page-content")
], style={
    "fontFamily": "Arial, sans-serif",
    "backgroundSize": "cover",
    "backgroundPosition": "center",
    "minHeight": "100vh",
    "padding": "40px"
})

@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    routes = {
        "/appliance": appliance_layout,
        "/lighting": lighting_layout,
        "/thermostat": thermostat_layout,
        "/diagnostics": diagnostics_layout,
        "/snare": snare_layout,
        "/miniprint": miniprint_layout,
        "/overview": overview_layout,
        "/user_study": user_study_layout,
        "/human_attacker": human_attackers_appliance_layout
    }
    if pathname in routes:
        return routes[pathname]()

    return html.Div([
        
        
        html.Div([
            html.Img(src=f"data:image/png;base64,{icon_data}", style={"width": "240px", "marginBottom": "30px"}),
            html.H1("HoneyFarm Data Analysis Dashboard", style={"color": "#91572b"}),
        ], style={"textAlign": "center", "marginBottom": "40px"}),

        # first row with Overview, Appliance, Lighting, Thermostat, and Diagnostics
        html.Div([
            html.Div([
                create_node_card("Overview", "/overview"),
                create_node_card("Appliance", "/appliance"),
                create_node_card("Lighting", "/lighting"),
                create_node_card("Thermostat", "/thermostat"),
                create_node_card("Diagnostics", "/diagnostics"),
            ], style={
                "display": "grid",
                "gridTemplateColumns": "repeat(5, 1fr)",
                "gap": "20px"
            })
        ], style={
            "display": "flex",
            "justifyContent": "center",
            "marginBottom": "40px"
        }),

        # second row with SNARE, MiniPrint, User Study, and Human Attacker
        html.Div([
            html.Div([
                create_node_card("SNARE", "/snare"),
                create_node_card("MiniPrint", "/miniprint"),
                create_node_card("User Study", "/user_study"),
                create_node_card("Attacker Analysis", "/human_attacker")
            ], style={
                "display": "grid",
                "gridTemplateColumns": "repeat(4, 1fr)",
                "gap": "20px"
            })
        ], style={
            "display": "flex",
            "justifyContent": "center"
        })

    ])


def create_node_card(label, href):
    return html.Div([
        html.Div(label, style={
            "fontSize": "30px",
            "fontWeight": "700",
            "marginBottom": "25px",  # add margin for spacing
        }),
        dcc.Link("Enter Dashboard", href=href, style={
            "color": "#fff",
            "textDecoration": "underline",
            "fontSize": "16px"
        })
    ], style={
        "width": "220px",
        "height": "130px",
        "backgroundColor": "#2980b9",
        "color": "white",
        "borderRadius": "12px",
        "boxShadow": "0px 6px 16px rgba(0,0,0,0.12)",
        "padding": "16px 12px",
        "textAlign": "center",
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "center",
        "alignItems": "center",   # center text and link
        "transition": "transform 0.2s ease-in-out",
        "cursor": "pointer"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
