import json
import redis
import ass
import sys
from flask import Flask
import threading
import requests
import time
from dash.dependencies import Input, Output
from dash import Dash, dcc, html, Output, Input

app = Flask(__name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
redis_client.flushdb()
epochTime = time.time()
MAX_RECORDS = 600
MAX_IDS = 6
records_copy = []
redBoxes = [[[]for _ in range(6)] for _ in range(6)]

# Initialize Dash app
dash_app = Dash(__name__, server=app)

def async_request():
    while True:
        loopStart = time.time()
        # Replace this URL with the actual endpoint you want to send requests to
        try:
            for i in range(1,7):
                url = 'http://tesla.iem.pw.edu.pl:9080/v2/monitor/'+str(i)
                response = requests.get(url, timeout=1)
                data = response.json()

                # Extract ID from JSON
                record_id = str(i)

                # Save the record to the queue
                save_record_to_queue(record_id, data)

        except Exception as e:
            print('Blad pobierania danych')
            sys.stdout.flush()

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

def get_records_by_id(record_id):
    key = f'queue:{record_id}'
    records = redis_client.lrange(key, 0, MAX_RECORDS - 1)

    # Decode the JSON strings to Python objects, skipping empty strings
    return [json.loads(record) for record in records if record]

def get_records(record_id):
    records = get_records_by_id(record_id)
    return records

# Dash layout
dash_app.layout = html.Div(children=[
    html.Div(children = [
        html.H1(id='nameAndYear'),
        dcc.RadioItems(
            id='radio-items',
            options=[
                {'label': 'Janek Grzegorczyk', 'value': 1},
                {'label': 'Elżbieta Kochalska', 'value': 2},
                {'label': 'Albert Lisowski', 'value': 3},
                {'label': 'Ewelina Nosowska', 'value': 4},
                {'label': 'Piotr Fokalski', 'value': 5},
                {'label': 'Bartosz Moskalski', 'value': 6}
            ],
            value=1,
            style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'center', 'alignItems': 'center', 'width':'70%', 'fontWeight':'15px'}
        )
    ],style={'display': 'flex',
            'flexDirection': 'row',
            'background': '#333',
            'color': '#fff',
            'padding': '20px',
            'borderRadius': '15px',
            'margin': '0px 0px 10px 0px',
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)'}),
    ass.FootComponent(
        id='feetComponent',
        value1='1111',
        value1anomaly=False,
        value2='2222',
        value2anomaly=False,
        value3='3333',
        value3anomaly=False,
        value4='4444',
        value4anomaly=False,
        value5='5555',
        value5anomaly=False,
        value6='6666',
        value6anomaly=False
    ),
    dcc.Graph(id='line-plot-1'),
    dcc.Graph(id='line-plot-2'),
    dcc.Graph(id='line-plot-3'),
    dcc.Graph(id='line-plot-4'),
    dcc.Graph(id='line-plot-5'),
    dcc.Graph(id='line-plot-6'),

    dcc.Interval(
        id='interval-component',
        interval=1*1000,
        n_intervals=0
    ),
    html.Div([
        html.P("© 2024 Politechnika Warszawska. All rights reserved.", style={
            'color': '#fff',
            'padding': '10px',
            'textAlign': 'center',
            'margin': '0'
        }),
        html.P("Authors: Mateusz Charczuk, Mikołaj Burdzy", style={
            'color': '#fff',
            'padding': '10px',
            'textAlign': 'center',
            'margin': '0'
        })
    ], style={'padding': '20px', 'backgroundColor': '#333'})
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
     Output('feetComponent', 'value6'),
     Output('feetComponent', 'value1anomaly'),
     Output('feetComponent', 'value2anomaly'),
     Output('feetComponent', 'value3anomaly'),
     Output('feetComponent', 'value4anomaly'),
     Output('feetComponent', 'value5anomaly'),
     Output('feetComponent', 'value6anomaly')],
    [Input('interval-component', 'n_intervals'),
     Input('radio-items', 'value')]
)
def update_data(n_intervals, radio_value):
    global records_copy
    patient_number = radio_value-1
    records = get_records(patient_number+1)
    isIsodErr = False
    if records == records_copy:
        isIsodErr = True
    if records is not None:
        record = records[0]
        birthdate = record.get("birthdate")
        firstname = record.get("firstname")
        lastname = record.get("lastname")
        sensorNames = [value.get("name") for value in record.get("trace").get("sensors")]

        time_series_data = [[] for _ in range(6)]
        time_series_anomalies = [[] for _ in range(6)]
        traces = [dict() for _ in range(6)]
        figures = [dict() for _ in range(6)]
        
        for sensor in range(0,6):
            time_series_data[sensor] = [value.get("trace").get("sensors")[sensor].get("value") for value in records]
            time_series_anomalies[sensor] = [value.get("trace").get("sensors")[sensor].get("anomaly") for value in records]
            traces[sensor] = dict(y=time_series_data[sensor][::-1], mode='lines', name=sensorNames[sensor], line = {'color': 'blue'})
            redBoxes[patient_number][sensor] = [{'type': 'rect', 'x0': i, 'x1': i+1, 'y0': 0, 'y1': 1050, 'fillcolor': 'rgba(255, 0, 0, 0.6)', 'line': {'width': 0}} for i, value in enumerate(time_series_anomalies[sensor][::-1]) if value]
            if(len(time_series_data[sensor]) > MAX_RECORDS-1 and not isIsodErr):
                for refBoxDict in redBoxes[patient_number][sensor]:
                    if refBoxDict['x0'] < 0:
                        refBoxDict['visible'] = False
            figures[sensor] = {'data': [traces[sensor]], 'layout': {'title': sensorNames[sensor],'shapes': redBoxes[patient_number][sensor]}}

        records_copy = records 
        first_last_name = firstname + ' ' + lastname + ' ' + birthdate
        tupl = (first_last_name, figures[0], figures[1], figures[2], figures[3], figures[4], figures[5],  time_series_data[0][0], time_series_data[1][0], time_series_data[2][0], time_series_data[3][0], time_series_data[4][0], time_series_data[5][0],  time_series_anomalies[0][0], time_series_anomalies[1][0], time_series_anomalies[2][0], time_series_anomalies[3][0], time_series_anomalies[4][0], time_series_anomalies[5][0])
        return tupl
    else:
        return None

if __name__ == '__main__':
    # Start the async request thread
    request_thread = threading.Thread(target=async_request)
    request_thread.start()

    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
