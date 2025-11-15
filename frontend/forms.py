"""Form components for dashboard"""
from dash import html, dcc
import dash_bootstrap_components as dbc


def create_upload_form():
    """Create file upload form"""
    return dbc.Card([
        dbc.CardHeader(html.H4("Upload Battery Measurement Data")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Battery Pack ID"),
                    dcc.Dropdown(
                        id='pack-selector',
                        placeholder="Select battery pack",
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("Test Condition"),
                    dcc.Input(
                        id='condition-input',
                        type='text',
                        placeholder='e.g., charging, discharging, idle',
                        className='form-control'
                    )
                ], width=6)
            ], className='mb-3'),
            dbc.Row([
                dbc.Col([
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select CSV File')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        multiple=False
                    )
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    html.Button(
                        'Upload and Process',
                        id='upload-button',
                        className='btn btn-primary',
                        n_clicks=0
                    )
                ])
            ])
        ])
    ], className='mb-4')


def create_diagnostic_note_form():
    """Create diagnostic note submission form"""
    return dbc.Card([
        dbc.CardHeader(html.H4("Add Diagnostic Note")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Metric ID"),
                    dcc.Input(
                        id='note-metric-id',
                        type='number',
                        placeholder='Enter metric ID',
                        className='form-control'
                    )
                ], width=4),
                dbc.Col([
                    dbc.Label("Your Name"),
                    dcc.Input(
                        id='note-user',
                        type='text',
                        placeholder='Enter your name',
                        className='form-control'
                    )
                ], width=4)
            ], className='mb-3'),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Diagnostic Note"),
                    dcc.Textarea(
                        id='note-text',
                        placeholder='Enter diagnostic observations...',
                        style={'width': '100%', 'height': 100},
                        className='form-control'
                    )
                ])
            ], className='mb-3'),
            dbc.Row([
                dbc.Col([
                    html.Button(
                        'Submit Note',
                        id='submit-note-button',
                        className='btn btn-success',
                        n_clicks=0
                    )
                ])
            ])
        ])
    ], className='mb-4')