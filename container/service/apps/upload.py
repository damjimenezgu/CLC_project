# Import libraries
import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pandas as pd
from app import app

import boto3
import smart_open


# Conncet to S3
try:
    #s3 = boto3.resource('s3')
    #model_file = s3.Object('clc-prediction-bucket','model_lin_reg.txt').get()['Body'] # .read().decode('utf-8')
    model_path = 's3:clc-prediction-bucket/model_lin_reg.txt'
    model_f = smart_open.open(model_path, 'r')
    h1 = html.H1(model_f.readline(), style={"textAlign": "center", "color":  "#4397a3", "font-weight": "bold"})
    model_f.close()
except Exception as e:
    h1 = html.H1(str(e), style={"textAlign": "center", "color":  "#4397a3", "font-weight": "bold"})

# Define layout for web page "upload"
layout = html.Div([
    h1,
    # Set title
    html.H1('Upload new data set', style={"textAlign": "center", "color":  "#4397a3", "font-weight": "bold"}),
    # Set text for uploading
    html.Pre(children="Select the file to upload (must be a CSV file, separated by '|'):", style={"fontSize":"150%", "color":  "#BFBFBF"}),
    dcc.Upload(
    # Set uploading button
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px',
            'borderColor': '#BFBFBF'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])



# Define function to upload CSV (must be separated by "|")
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), sep="|")
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    # Return (print) the complete table uploaded
    return html.Div([
        # Write name of the file uploaded
        html.H5("Data set name: "),html.H5(filename),html.Br(),
        # Write time of the uploading
        html.H5("Uploading time: "),html.H5(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

# Call back to retrieve information after clicking in the upload button
@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children
