from dash import Dash, html, dcc, Input, Output
from pages.appliance import appliance_layout
from pages.lighting import lighting_layout
from pages.thermostat import thermostat_layout
from pages.diagnostics import diagnostics_layout
from pages.snare import snare_layout
from pages.miniprint import miniprint_layout
from pages.overview import overview_layout
import base64

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Encode icon image
with open("./data_visualization/assets/honeyfarm_icon.jpg", "rb") as f:
    icon_data = base64.b64encode(f.read()).decode("utf-8")

app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div(id="page-content")
], style={
    "fontFamily": "Arial, sans-serif",
    "backgroundImage": "url('./data_visualization/assets/dashboard_bg.png')",
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
        "/overview": overview_layout
    }
    if pathname in routes:
        return routes[pathname]()

    return html.Div([
        html.Div([
            html.Img(src=f"data:image/png;base64,{icon_data}", style={"width": "240px", "marginBottom": "30px"}),
            html.H1("Welcome to Honeyfarm Dashboard", style={"color": "#2c3e50"}),
            html.H3("Select a Node to View:", style={"color": "#34495e"})
        ], style={"textAlign": "center", "marginBottom": "40px"}),

        html.Div([
            create_node_card("Overview", "/overview"),
            create_node_card("Appliance", "/appliance"),
            create_node_card("Lighting", "/lighting"),
            create_node_card("Thermostat", "/thermostat"),
            create_node_card("Diagnostics", "/diagnostics"),
            create_node_card("Snare", "/snare"),
            create_node_card("Miniprint", "/miniprint")
        ], style={
            "display": "flex",
            "flexWrap": "wrap",
            "justifyContent": "center",
            "gap": "24px"
        })
    ])

def create_node_card(label, href):
    return html.Div([
        html.Div(label, style={"fontSize": "22px", "fontWeight": "bold", "marginBottom": "8px"}),
        dcc.Link("Enter Dashboard", href=href, style={"color": "#fff", "textDecoration": "underline", "fontSize": "15px"})
    ], style={
        "width": "220px",
        "height": "130px",
        "backgroundColor": "#2980b9",
        "color": "white",
        "borderRadius": "16px",
        "boxShadow": "0px 8px 20px rgba(0,0,0,0.15)",
        "padding": "24px 16px",
        "textAlign": "center",
        "transition": "transform 0.2s ease-in-out",
        "cursor": "pointer"
    })
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)