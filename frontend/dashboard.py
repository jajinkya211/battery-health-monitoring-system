"""Main Dash application for battery health monitoring dashboard"""
import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import requests
import pandas as pd
from frontend.charts import BatteryCharts
from frontend.forms import create_upload_form, create_diagnostic_note_form
from config.settings import API_HOST, API_PORT

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Battery Health Monitor"

# API base URL
API_BASE = f"http://{API_HOST}:{API_PORT}"

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Battery Health Monitoring System", className='text-center mb-4 mt-4'),
            html.Hr()
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            create_upload_form()
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Div(id='upload-status', className='alert')
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Label("Select Measurement to View"),
            dcc.Dropdown(
                id='measurement-selector',
                placeholder="Select a measurement"
            ),
            html.Button(
                'Refresh Measurements',
                id='refresh-measurements',
                className='btn btn-secondary mt-2',
                n_clicks=0
            )
        ], width=12)
    ], className='mb-4'),
    
    html.Div(id='metrics-display'),
    
    dbc.Row([
        dbc.Col([
            create_diagnostic_note_form()
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Div(id='note-status', className='alert')
        ])
    ]),
    
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # Update every 30 seconds
        n_intervals=0
    )
    
], fluid=True)


# Callbacks
@app.callback(
    Output('pack-selector', 'options'),
    Input('interval-component', 'n_intervals')
)
def update_pack_options(n):
    """Load battery pack options"""
    try:
        response = requests.get(f"{API_BASE}/battery_packs")
        packs = response.json()
        return [{'label': f"{p['model']} (ID: {p['pack_id']})", 
                'value': p['pack_id']} for p in packs]
    except:
        return []


@app.callback(
    Output('measurement-selector', 'options'),
    Input('refresh-measurements', 'n_clicks')
)
def update_measurement_options(n):
    """Load measurement options"""
    try:
        response = requests.get(f"{API_BASE}/measurements")
        measurements = response.json()
        return [{'label': f"Measurement {m['measurement_id']} - {m['condition']} ({m['timestamp']})", 
                'value': m['measurement_id']} for m in measurements]
    except:
        return []


@app.callback(
    Output('metrics-display', 'children'),
    Input('measurement-selector', 'value')
)
def display_metrics(measurement_id):
    """Display metrics for selected measurement"""
    if not measurement_id:
        return html.Div("Select a measurement to view metrics", className='text-muted')
    
    try:
        response = requests.get(f"{API_BASE}/health_metrics?measurement_id={measurement_id}")
        metrics = response.json()
        
        if not metrics:
            return html.Div("No metrics found for this measurement", className='alert alert-warning')
        
        # Convert to format expected by charts
        metrics_data = [
            {
                'cell_id': m['cell_id'],
                'soc_percent': m['soc_percent'],
                'soh_percent': m['soh_percent'],
                'internal_resistance': m['internal_resistance'],
                'temperature_c': m['temperature_c'],
                'passes_threshold': m['passes_threshold']
            }
            for m in metrics
        ]
        
        charts = BatteryCharts()
        
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=charts.create_metrics_summary_table(metrics_data))
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=charts.create_soh_chart(metrics_data))
                ], width=6),
                dbc.Col([
                    dcc.Graph(figure=charts.create_soc_chart(metrics_data))
                ], width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=charts.create_resistance_chart(metrics_data))
                ], width=6),
                dbc.Col([
                    dcc.Graph(figure=charts.create_temperature_chart(metrics_data))
                ], width=6)
            ])
        ])
    
    except Exception as e:
        return html.Div(f"Error loading metrics: {str(e)}", className='alert alert-danger')


@app.callback(
    Output('note-status', 'children'),
    Input('submit-note-button', 'n_clicks'),
    State('note-metric-id', 'value'),
    State('note-user', 'value'),
    State('note-text', 'value')
)
def submit_diagnostic_note(n_clicks, metric_id, user, note):
    """Submit diagnostic note"""
    if n_clicks == 0:
        return ""
    
    if not all([metric_id, user, note]):
        return html.Div("Please fill all fields", className='alert alert-warning')
    
    try:
        response = requests.post(
            f"{API_BASE}/diagnostic_notes",
            json={
                'metric_id': metric_id,
                'user_name': user,
                'note': note
            }
        )
        
        if response.status_code == 201:
            return html.Div("Note submitted successfully!", className='alert alert-success')
        else:
            return html.Div("Error submitting note", className='alert alert-danger')
    
    except Exception as e:
        return html.Div(f"Error: {str(e)}", className='alert alert-danger')


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)