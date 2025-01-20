import dash
from dash import dcc, html, Input, Output

from load_pro import load_model_data, load_obs_data
from plotting import station_plots, urban_rural

model_data = load_model_data()
obs_data = load_obs_data()

regionwithstation = {
    'Region Bregenz': ['BREGENZ', 'DORNBIRN', 'ROHRSPITZ'],
    'Region Innsbruck': ['INNSBRUCK-FLUGPLATZ', 'INNSBRUCK-UNIV', 'RINN'],
    'Region Salzburg': ['SALZBURG-FLUGHAFEN', 'SALZBURG-FREISAAL'],
    'Region Klagenfurt': ['KLAGENFURT-FLUGHAFEN', 'VILLACH-STADT'],
    'Region Linz': ['LINZ-STADT', 'HOERSCHING', 'REICHENAUMUEHLKREIS'],
    'Region Graz': ['GRAZ-FLUGHAFEN', 'GRAZSTRASSGANG', 'GRAZ-UNIVERSITAET'],
    'Region St. Pölten': ['ST_POELTENLANDHAUS', 'LILIENFELD-TARSCHBERG'],
    'Region Wien': ['WIEN-INNERESTADT', 'SCHWECHAT', 'WIEN-MARIABRUNN', 'KLAUSEN-LEOPOLDSDORF'],
    'Region Eisenstadt': ['EISENSTADT-NORDOST']
}

app = dash.Dash(__name__)
app.css.config.serve_locally = True

app.layout = html.Div([
    html.H1(
        "WRF Casestudy Dashboard",
        className="dashboard-title"
    ),

    html.Div([

        html.Div([
            html.H2("Singleselection", className="section-title"),
            html.Div([
                html.Label("Select Case", className="dropdown-label"),
                dcc.Dropdown(
                    id='case-dropdown',
                    options=[{'label': 'Case 1', 'value': 'Case1'}],
                    value='Case1',
                    multi=False,
                    className="dropdown",
                    placeholder="Choose a case"
                )
            ], className="dropdown-container"),
            html.Div([
                html.Label("Land Use Scheme", className="dropdown-label"),
                dcc.Dropdown(
                    id='lus-dropdown',
                    options=[{'label': 'Noah LUS', 'value': 'noah'}],
                    value='noah',
                    multi=False,
                    className="dropdown",
                    placeholder="Select LUS"
                )
            ], className="dropdown-container"),
            html.Div([
                html.Label("Select Region", className="dropdown-label"),
                dcc.Dropdown(
                    id='region-dropdown',
                    options=[
                        {'label': region, 'value': region} for region in regionwithstation.keys()
                    ],
                    value='Region Innsbruck',
                    multi=False,
                    className="dropdown",
                    placeholder="Select a region"
                )
            ], className="dropdown-container"),
        ], className="dropdown-group"),
        

        html.Div([
            html.H2("Multiselection", className="section-title"),
            html.Div([
                html.Label("Urban Canopy Model", className="dropdown-label"),
                dcc.Dropdown(
                    id='ucm-dropdown',
                    options=[
                        {'label': 'Bulk', 'value': 'bulk'},
                        {'label': 'SLUCM', 'value': 'slucm'},
                        {'label': 'BEP', 'value': 'bep'}
                    ],
                    value=['bulk', 'slucm', 'bep'],
                    multi=True,
                    className="dropdown",
                    placeholder="Select UCM models"
                )
            ], className="dropdown-container"),
            html.Div([
                html.Label("Stations", className="dropdown-label"),
                dcc.Dropdown(
                    id='stations-dropdown',
                    options=[
                        {'label': 'INNSBRUCK-FLUGPLATZ', 'value': 'INNSBRUCK-FLUGPLATZ'}
                    ],
                    value=['INNSBRUCK-FLUGPLATZ'],
                    multi=True,
                    className="dropdown",
                    placeholder="Select stations"
                )
            ], className="dropdown-container"),
            html.Div([
                html.Label("Variables", className="dropdown-label"),
                dcc.Dropdown(
                    id='variables-dropdown',
                    options=[
                        {'label': 'Temperature [°C]', 'value': 'Temperature [°C]'},
                        {'label': 'Water Vapor Mixing Ratio [g/kg]', 'value': 'Water Vapor Mixing Ratio [g/kg]'},
                        {'label': 'Windspeed [m/s]', 'value': 'Windspeed [m/s]'},
                        {'label': 'Winddirection [°]', 'value': 'Winddirection [°]'}
                    ],
                    value=['Temperature [°C]'],
                    multi=True,
                    className="dropdown",
                    placeholder="Select variables"
                )
            ], className="dropdown-container"),
        ], className="dropdown-group"),
    ], className="dashboard-container"),

    html.Div(id='container', className="output-container")
], className="main-container")

@app.callback(
    [Output('stations-dropdown', 'options'),
     Output('stations-dropdown', 'value')],
    Input('region-dropdown', 'value')
)
def update_stations_dropdown(selected_region):
    if selected_region:

        station_options = [{'label': station, 'value': station} for station in regionwithstation[selected_region]]

        station_values = regionwithstation[selected_region]
    else:
        # Default empty state
        station_options = []
        station_values = []
    
    return station_options, station_values

@app.callback(
    Output('container', 'children'),
    [
        Input('case-dropdown', 'value'),
        Input('lus-dropdown', 'value'),
        Input('ucm-dropdown', 'value'),
        Input('region-dropdown', 'value'),
        Input('stations-dropdown', 'value'),
        Input('variables-dropdown', 'value')
    ]
)
def update_regions(case, lus, ucm, region, stations, variables):

    figures_urban_rural = urban_rural(obs_data, stations, case, variables)

    figures_by_variable = station_plots(obs_data, model_data, stations, ucm, variables)

    variable_plots = []
    for var_name, figures in figures_by_variable.items():
        row = html.Div(
            children=figures,
            style={
                'display': 'flex',
                'flex-direction': 'row',
                'flex-wrap': 'nowrap',  
                'overflow-x': 'auto',  
                'padding': '10px',
                'margin-bottom': '20px',
                'gap': '10px'
            }
        )

        variable_plots.append(html.Div([
            html.H3(var_name, style={'margin-bottom': '10px'}),
            row
        ]))

    container = html.Div([

        html.Div(
            children=figures_urban_rural,
            style={
                'width': '50%',
                'padding': '10px',
                'display': 'inline-block',
                'vertical-align': 'top'
            }
        ),

        html.Div(
            children=variable_plots,
            style={
                'width': '50%',
                'padding': '10px',
                'display': 'inline-block',
                'overflow-x': 'auto'
            }
        )
    ], style={'width': '100%', 'display': 'flex'})

    return container


if __name__ == '__main__':
    app.run_server(debug=True)
