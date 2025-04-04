# pages/csv_plotter.py
import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import base64
import io

# Register page in multi-page Dash app
dash.register_page(__name__, name='CSV Plotter', order=4)

# --- Layout ---
layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("Interactive CSV Plotter"), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id='upload-data',
                children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
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
            ),
            html.Div(id='file-info'),
            html.Div(id='data-preview')
        ], width=12)
    ]),

    dbc.Row([
        dbc.Col([
            html.Div(id='controls-container')
        ])
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='custom-plot')
        ])
    ])
])

# --- Helper to parse uploaded file ---
def parse_data(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif filename.endswith('.xls') or filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None, html.Div(['Unsupported file format'])
    except Exception as e:
        return None, html.Div(['There was an error processing this file: {}'.format(str(e))])
    return df, None

# --- Callbacks ---
@callback(
    Output('file-info', 'children'),
    Output('data-preview', 'children'),
    Output('controls-container', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(contents, filename):
    if contents is None:
        return '', '', ''

    df, error = parse_data(contents, filename)
    if error:
        return '', error, ''

    preview = dbc.Table.from_dataframe(df.head(), striped=True, bordered=True, hover=True)

    controls = html.Div([
        html.H5("Chart Controls"),
        dbc.Row([
            dbc.Col([
                html.Label("X-axis"),
                dcc.Dropdown(options=[{'label': col, 'value': col} for col in df.columns], id='x-axis')
            ]),
            dbc.Col([
                html.Label("Y-axis"),
                dcc.Dropdown(options=[{'label': col, 'value': col} for col in df.columns], id='y-axis')
            ])
        ]),
        dbc.Row([
            dbc.Col([
                html.Label("Chart Type"),
                dcc.Dropdown(
                    options=[
                        {'label': t, 'value': t} for t in ["bar", "scatter", "line", "area", "box", "pie"]
                    ],
                    value='bar',
                    id='chart-type'
                )
            ])
        ]),
        dbc.Row([
            dbc.Col([
                html.Label("Chart Title"),
                dcc.Input(id='chart-title', type='text', placeholder='Enter chart title...', style={'width': '100%'})
            ])
        ])
    ])

    return html.Div([html.P(f"Uploaded file: {filename}")]), preview, controls

@callback(
    Output('custom-plot', 'figure'),
    Input('x-axis', 'value'),
    Input('y-axis', 'value'),
    Input('chart-type', 'value'),
    Input('chart-title', 'value'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_graph(x, y, chart_type, title, contents, filename):
    if not contents or not x or not y:
        return px.scatter(title="Waiting for input...")

    df, error = parse_data(contents, filename)
    if error or df is None:
        return px.scatter(title="Error loading file")

    if chart_type == "scatter":
        fig = px.scatter(df, x=x, y=y, title=title)
    elif chart_type == "line":
        fig = px.line(df, x=x, y=y, title=title)
    elif chart_type == "bar":
        fig = px.bar(df, x=x, y=y, title=title)
    elif chart_type == "area":
        fig = px.area(df, x=x, y=y, title=title)
    elif chart_type == "box":
        fig = px.box(df, x=x, y=y, title=title)
    elif chart_type == "pie":
        fig = px.pie(df, names=x, values=y, title=title)
    else:
        fig = px.scatter(df, x=x, y=y, title="Unsupported chart type")

    return fig
