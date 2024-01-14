import os
import boto3
import pandas as pd
from dash import Dash, html, dcc
from dash.dependencies import Output, Input
import plotly.express as px
from flask import Flask, jsonify

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('REGION')
table_name = os.getenv('TABLE_NAME')

# Boto3 client
dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key,
                          region_name=region_name)

# Table name
table = dynamodb.Table(table_name)

server = Flask(__name__)
app = Dash(__name__, server=server)

# Define the layout with styled H1
app.layout = html.Div(children=[
    html.H1(children='Network Statistics Dashboard', style={'textAlign': 'center', 'fontFamily': 'Sans-serif'}),

    dcc.Graph(id='speed-time-graph'),
    dcc.Graph(id='ping-time-graph'),

    dcc.Interval(
            id='interval-component',
            interval=1*5000, # in milliseconds
            n_intervals=0
    )
])

@app.callback(
    [Output('speed-time-graph', 'figure'),
     Output('ping-time-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    # Fetch data from DynamoDB
    response = table.scan()
    data = response['Items']

    # Convert to DataFrame
    df = pd.DataFrame(data)
    # Sort descending time
    df['Index'] = pd.to_datetime(df['Index'])
    df = df.sort_values(by="Index")

    # Process JSON fields for speed
    df['download_speed'] = df['download'].apply(lambda x: float(x['speed']))
    df['upload_speed'] = df['upload'].apply(lambda x: float(x['speed']))

    # Process JSON fields for ping
    df['ping_mean'] = df['ping'].apply(lambda x: float(x['latency']))
    df['ping_high'] = df['ping'].apply(lambda x: float(x['high']))
    df['ping_low'] = df['ping'].apply(lambda x: float(x['low']))

    # Combine upload and download speed in one figure
    df_melted = df.melt(id_vars=['timestamp'], value_vars=['download_speed', 'upload_speed'], 
                        var_name='Type', value_name='Speed')
    fig_speed = px.line(df_melted, x='timestamp', y='Speed', color='Type', title='Upload and Download Speed Over Time (Mb/s)')

    # Create ping figure with shaded area for min and max
    fig_ping = px.line(df, x='timestamp', y='ping_mean', title='Ping Statistics Over Time (ms)')
    fig_ping.add_scatter(x=df['timestamp'], y=df['ping_high'], fill='tonexty', mode='lines', line=dict(width=0), name='Max Ping')
    fig_ping.add_scatter(x=df['timestamp'], y=df['ping_low'], fill='tonexty', mode='lines', line=dict(width=0), name='Min Ping')

    return fig_speed, fig_ping

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)
