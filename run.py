import json
import redis
from flask import Flask, jsonify
import threading
import requests
import time
from dash.dependencies import Input, Output
from dash import Dash, dcc, html, Output, Input
import plotly.express as px
import pandas as pd
import random
from math import log

app = Flask(__name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
epochTime = time.time()
MAX_RECORDS = 600
MAX_IDS = 6

# Initialize Dash app
dash_app = Dash(__name__, server=app)

def async_request():
    while True:
        loopStart = time.time()
        # Replace this URL with the actual endpoint you want to send requests to
        try:
            for i in range(1,7):
                url = 'http://tesla.iem.pw.edu.pl:9080/v2/monitor/'+str(i)
                # print(time.time() - epochTime)
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

    dcc.Graph(id='line-plot-1'),
    dcc.Graph(id='line-plot-2'),

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
     Output('line-plot-2', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_data(n_intervals):
    rand = 2 # random.randint(1, 6)
    records = get_records(rand)
    record = records[0]
    birthdate = record.get("birthdate")
    firstname = record.get("firstname")
    lastname = record.get("lastname")

    time_series_data_1 = [log(value.get("trace").get("sensors")[0].get("value")) for value in records]
    time_series_data_2 = [log(value.get("trace").get("sensors")[1].get("value")) for value in records]
    time_series_data_3 = [log(value.get("trace").get("sensors")[2].get("value")) for value in records]

    time_series_data_4 = [log(value.get("trace").get("sensors")[3].get("value")) for value in records]
    time_series_data_5 = [log(value.get("trace").get("sensors")[4].get("value")) for value in records]
    time_series_data_6 = [log(value.get("trace").get("sensors")[5].get("value")) for value in records]

    # Create traces for line plots
    trace1 = dict(x=list(range(len(time_series_data_1))), y=time_series_data_1[::-1], mode='lines', name='Line 1')
    trace2 = dict(x=list(range(len(time_series_data_2))), y=time_series_data_2[::-1], mode='lines', name='Line 2')
    trace3 = dict(x=list(range(len(time_series_data_3))), y=time_series_data_3[::-1], mode='lines', name='Line 3')

    trace4 = dict(x=list(range(len(time_series_data_4))), y=time_series_data_4[::-1], mode='lines', name='Line 4')
    trace5 = dict(x=list(range(len(time_series_data_5))), y=time_series_data_5[::-1], mode='lines', name='Line 5')
    trace6 = dict(x=list(range(len(time_series_data_6))), y=time_series_data_6[::-1], mode='lines', name='Line 6')

    # Create figures for line plots
    figure1 = {'data': [trace1, trace2, trace3], 'layout': {'title': 'Line Plot 1', 'yaxis_type': 'log'}}
    figure2 = {'data': [trace4, trace5, trace6], 'layout': {'title': 'Line Plot 2', 'yaxis_type': 'log'}}

    return firstname + ' ' + lastname + ' ' + birthdate, figure1, figure2

def get_records(record_id):
    records = get_records_by_id(record_id)
    return records

if __name__ == '__main__':
    # Start the async request thread
    request_thread = threading.Thread(target=async_request)
    request_thread.start()

    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
