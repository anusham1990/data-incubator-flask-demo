
# Imports

#import os
import bokeh
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource
from bokeh.embed import components
from bokeh.resources import CDN
from flask import Flask, render_template, request, redirect
import numpy as np 
import pandas as pd
import requests

# Gathering Data 

API_URL = "https://www.alphavantage.co/query" 
symbols =  ['QCOM',"INTC","PDD"]

time_data = {}

for symbol in symbols:
    data = { "function": "TIME_SERIES_MONTHLY", 
    "symbol": symbol,
    "outputsize" : "full",
    "datatype": "json", 
    "apikey": "WNZNE5X63OBPP78N" } 

    response = requests.get(API_URL, data) 
    response_json = response.json()
    #print(response_json)
    data = pd.DataFrame.from_dict(response_json['Monthly Time Series'], orient= 'index').sort_index(axis=1)
    data = data.rename(columns={ '1. open': 'Open', '2. high': 'High', '3. low': 'Low', '4. close': 'Close', '5. volume': 'Volume'})
    data = data[[ 'Open', 'High', 'Low', 'Close', 'Volume']]
    data['Date'] = pd.to_datetime(data.index)
    time_data[symbol] = data

# Function to plot graph

def plot_price(symbol):
    
    #output_file("line.html")

    source = ColumnDataSource(time_data[symbol])
    
    p = figure(x_axis_type = 'datetime') #p = figure(plot_width=400, plot_height=400
    p.line(x = 'Date', y = 'Open', source = source,  legend = symbol + " " + 'Open' , color = 'red' ) 
    p.line(x = 'Date', y = 'High', source = source,  legend = symbol + " " + 'High' , color = 'green')
    p.line(x = 'Date', y = 'Low' , source = source,  legend = symbol + " " + 'Low'  , color = 'yellow') 
    p.line(x = 'Date', y = 'Close',source = source,  legend = symbol + " " + 'Close', color = 'blue') 
    p.yaxis.axis_label = 'Stock Price'
    p.xaxis.axis_label = 'Date'
    
    #html = file_html(p, "line.html")
    #show(p)
    return p

#symbol = 'QCOM' # 'INTC', 'PDD'
#plot_price(symbol)

# Flask app


app = Flask(__name__)
app.vars={}

@app.route('/')
def main():
    return redirect('/home')

@app.route('/home', methods = ['GET','POST'])
def home():
    if request.method=='GET':
        return render_template('basic.html')
    else:
        app.vars['company'] = request.form['options']
        return redirect('/results')

@app.route('/results', methods = ['GET','POST'])
def results():
    if request.method=='GET':
        company = app.vars['company']
        return render_template('results.html', company = company)
    else:
        app.vars['company'] = request.form['options']
        return redirect('/results')

@app.route('/bokehPlot', methods = ['GET'])
def bokehPlot():
    company = app.vars['company']
    script, div = components(plot_price(company))
    return """
    <!doctype html>
    <head>
        {bokeh_css}
    </head>
    <body>
        {div}
        {bokeh_js}
        {script}
    </body>
    """.format(script=script, div=div, bokeh_css=CDN.render_css(), bokeh_js=CDN.render_js())

if __name__ == '__main__':
    app.run()

