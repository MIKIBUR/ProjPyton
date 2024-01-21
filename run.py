import json
import redis
import ass
import sys
from flask import Flask, jsonify
import threading
import requests
import time
from dash.dependencies import Input, Output, State
from dash import Dash, dcc, html, Output, Input
import plotly.express as px
import pandas as pd
import random
import math

app = Flask(__name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
redis_client.flushdb()
epochTime = time.time()
MAX_RECORDS = 600
MAX_IDS = 6
redBoxes = [[{'type': 'rect', 'x0': 40, 'x1': 46, 'y0': 0, 'y1': 1050, 'fillcolor': 'rgba(255, 0, 0, 0.2)', 'line': {'width': 0}},] for _ in range(6)]
num = 30

# Initialize Dash app
dash_app = Dash(__name__, server=app)

def async_request():
    while True:
        loopStart = time.time()
        # Replace this URL with the actual endpoint you want to send requests to
        try:
            for i in range(1,7):
                url = 'http://tesla.iem.pw.edu.pl:9080/v2/monitor/'+str(i)
                response = requests.get(url)
                data = response.json()

                # Extract ID from JSON
                record_id = str(i)

                # Save the record to the queue
                save_record_to_queue(record_id, data)

        except Exception as e:
            pass

        # Sleep for 1 second before making the next request
        loopEnd = time.time()
        loopTime = loopEnd - loopStart if loopEnd - loopStart < 1 else 1 
        time.sleep(1 - loopTime)

def save_record_to_queue(record_id, data):
    # Key to represent the queue for a specific ID
    key = f'queue:{record_id}'

    # Add the record to the beginning of the queue
    redis_client.lpush(key, json.dumps(data))

    # Trim the list to the maximum allowed records
    redis_client.ltrim(key, 0, MAX_RECORDS - 1)

@app.route('/')
def index():
    return 'Flask app running!'

def get_records_by_id(record_id):
    key = f'queue:{record_id}'
    records = redis_client.lrange(key, 0, MAX_RECORDS - 1)

    # Decode the JSON strings to Python objects, skipping empty strings
    return [json.loads(record) for record in records if record]

# Dash layout
dash_app.layout = html.Div(children=[
    html.H1(id='nameAndYear'),
    ass.FootComponent(
        id='feetComponent',
        value1='1111',
        value2='2222',
        value3='3333',
        value4='4444',
        value5='5555',
        value6='6666'
    ),
    dcc.Slider(
        id='my-slider',
        min=30,
        max=600,
        step=1,
        marks={i: str(i) for i in range(30, 601, 50)},  # optional: add marks for better visualization
        value=30  # default value
    ),
    dcc.Graph(id='line-plot-1'),
    dcc.Graph(id='line-plot-2'),
    dcc.Graph(id='line-plot-3'),
    dcc.Graph(id='line-plot-4'),
    dcc.Graph(id='line-plot-5'),
    dcc.Graph(id='line-plot-6'),

    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # in milliseconds
        n_intervals=0
    )
])

# Define callback to update data every second
@dash_app.callback(
    [Output('nameAndYear', 'children'),
     Output('line-plot-1', 'figure'),
     Output('line-plot-2', 'figure'),
     Output('line-plot-3', 'figure'),
     Output('line-plot-4', 'figure'),
     Output('line-plot-5', 'figure'),
     Output('line-plot-6', 'figure'),
     Output('feetComponent', 'value1'),
     Output('feetComponent', 'value3'),
     Output('feetComponent', 'value5'),
     Output('feetComponent', 'value2'),
     Output('feetComponent', 'value4'),
     Output('feetComponent', 'value6')],
    [Input('interval-component', 'n_intervals'),
     State('my-slider', 'value')]
)
def update_data(n_intervals, num_of_points):
    rand = 2 # random.randint(1, 6)
    records = get_records(rand)
    if records is not None:
        record = records[0]
        birthdate = record.get("birthdate")
        firstname = record.get("firstname")
        lastname = record.get("lastname")
        sensorNames = [value.get("name") for value in record.get("trace").get("sensors")]
        global num 

        time_series_data = [[] for _ in range(6)]
        time_series_anomalies = [[] for _ in range(6)]
        traces = [dict() for _ in range(6)]
        figures = [dict() for _ in range(6)]
        for i in range(0,6):
                # [{'type': 'rect', 'x0': 2, 'x1': 4, 'y0': 0, 'y1': 1050, 'fillcolor': 'rgba(255, 0, 0, 0.2)', 'line': {'width': 0}},
                # {'type': 'rect', 'x0': 2, 'x1': 4, 'y0': 0, 'y1': 1050, 'fillcolor': 'rgba(255, 0, 0, 0.2)', 'line': {'width': 0}},
                # {'type': 'rect', 'x0': 2, 'x1': 4, 'y0': 0, 'y1': 1050, 'fillcolor': 'rgba(255, 0, 0, 0.2)', 'line': {'width': 0}}]
            
            time_series_data[i] = [value.get("trace").get("sensors")[i].get("value") for value in records]
            time_series_anomalies[i] = [value.get("trace").get("sensors")[i].get("anomaly") for value in records]
            traces[i] = dict(y=time_series_data[i][::-1][-num_of_points:], mode='lines', name=sensorNames[i], line = {'color': 'blue'})
            previousLimit = min(len(time_series_data[i]),num)
            currentLimit = min(len(time_series_data[i]),num_of_points)
            if num > num_of_points:
                shiftToLeft = previousLimit - currentLimit
                for refBoxDict in redBoxes[i]:
                    refBoxDict['x0'] = refBoxDict['x0'] - shiftToLeft
                    refBoxDict['x1'] = refBoxDict['x1'] - shiftToLeft
            elif num < num_of_points:
                for refBoxDict in redBoxes[i]:
                    refBoxDict['x0'] = refBoxDict['x0'] - len(time_series_data[i]) + num_of_points
                    refBoxDict['x1'] = refBoxDict['x1'] - len(time_series_data[i]) + num_of_points
            if(time_series_anomalies[i][0]):
                redBoxes[i].append({'type': 'rect', 'x0': len(time_series_data[i]), 'x1': len(time_series_data[i])+2, 'y0': 0, 'y1': 1050, 'fillcolor': 'rgba(255, 0, 0, 0.6)', 'line': {'width': 0}})
            figures[i] = {'data': [traces[i]], 'layout': {'title': sensorNames[i],'shapes': redBoxes[i]}}
        if num != num_of_points:
            num = num_of_points
            
        return firstname + ' ' + lastname + ' ' + birthdate, figures[0], figures[1], figures[2], figures[3], figures[4], figures[5],  time_series_data[0][0], time_series_data[1][0], time_series_data[2][0], time_series_data[3][0], time_series_data[4][0], time_series_data[5][0]
    else:
        return None
    
def get_records(record_id):
    records = get_records_by_id(record_id)
    return records

if __name__ == '__main__':
    # Start the async request thread
    request_thread = threading.Thread(target=async_request)
    request_thread.start()

    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
