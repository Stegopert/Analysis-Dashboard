import plotly.graph_objects as go
from dash import dcc

def station_plots(obs_data, mod_data, stations, models, variables):
    figures_by_variable = {}
    var_mapping = {
        'Temperature [°C]': 'T2',
        'Pressure': 'PSFC',
        'Water Vapor Mixing Ratio [g/kg]': 'Q2',
        'Windspeed [m/s]': 'WS10',
        'Winddirection [°]': 'WD10'
    }

    var_pairs = [(var, var_mapping[var]) for var in variables if var in var_mapping]

    colors = {
        'bulk': 'green',
        'slucm': 'red',
        'bep': '#9467bd'
    }

    for var_name, var_code in var_pairs:
        row_figures = []
        for station in stations:

            fig = go.Figure()

            observed_data = obs_data.loc[(slice(None), station), var_name]
            fig.add_trace(go.Scatter(
                x=observed_data.index.get_level_values('DateTime'),
                y=observed_data.values,
                mode='lines' if var_name != 'Winddirection [°]' else 'markers',
                name=f'Observed - {station}',
                line=dict(color='black', width=1),
                marker=dict(color='black', size=5) if var_name == 'Winddirection [°]' else None
            ))

            for model in models:
                model_prediction = mod_data.loc[(slice(None), slice(None), model, station), var_code]
                fig.add_trace(go.Scatter(
                    x=model_prediction.index.get_level_values('DateTime'),
                    y=model_prediction.values,
                    mode='lines' if var_name != 'Winddirection [°]' else 'markers',
                    name=f'{model}',
                    line=dict(color=colors.get(model, 'white'), width=1),
                    marker=dict(color=colors.get(model, 'white'), symbol='x', size=5) if var_name == 'Winddirection [°]' else None
                ))

            fig.update_layout(
                height=500,
                width=700,
                title_text=f"{var_name} Observed vs Model Data for {station}",
                template="plotly_white",
                xaxis_title="DateTime",
                yaxis_title=var_name
            )

            row_figures.append(dcc.Graph(figure=fig))

        figures_by_variable[var_name] = row_figures

    return figures_by_variable

def urban_rural(df, stations, case, variables):
    figures = []
    filtered_df = df.loc[case]

    for var in variables:
        fig = go.Figure()
        
        for station in stations:
            if station in filtered_df.index.get_level_values('STATION'):
                station_df = filtered_df.xs(station, level='STATION')
                if var != 'Winddirection [°]':
                    fig.add_trace(go.Scatter(
                        x=station_df.index,
                        y=station_df[var],
                        mode='lines',
                        name=f'{station}'
                    ))
                    #y-labels
                    y_labels = {
                        'Temperature [°C]': 'Temperature [°C]',
                        'Pressure [hPa]': 'Pressure [hPa]',
                        'Water Vapor Mixing Ratio [g/kg]': 'Water Vapor Mixing Ratio [g/kg]',
                        'Windspeed [m/s]': 'Windspeed [m/s]',
                        'Winddirection [°]': 'Winddirection [°]'
                        
                    }
                    ylabel = y_labels.get(var)
                    fig.update_yaxes(title_text=ylabel)
                else:
                    fig.add_trace(go.Scatter(
                        x=station_df.index,
                        y=station_df[var],
                        mode='markers',
                        name=f'{station}'
                    ))
        

        fig.update_layout(
            title=f"Urban/Rural comparison for {var}",
            xaxis_title='Time',
            yaxis_title=var,
            template="plotly_white",
            legend_title="Stations"
        )
        figures.append(dcc.Graph(figure=fig))

    return figures
