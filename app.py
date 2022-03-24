import urllib.request
from pprint import pprint
from html_table_parser.parser import HTMLTableParser
import pandas as pd
import json
from flask import Flask

def url_get_contents(url):
    req = urllib.request.Request(url=url)
    f = urllib.request.urlopen(req)
    return f.read()

def get_data(url):
    xhtml = url_get_contents(url).decode('utf-8')
    p = HTMLTableParser()
    p.feed(xhtml)
    #pprint(p.tables[0]) 
    df=pd.DataFrame(p.tables[0][1:],columns=p.tables[0][0])
    df1=df.set_index('Date')
    a=df1.to_json(orient='index')
    return a

def get_data_browsers(url): # function definition
    xhtml = url_get_contents(url).decode('utf-8')
    p = HTMLTableParser()
    p.feed(xhtml)
    #pprint(p.tables[0])
    b=json.loads(get_data(url))
    bdf=pd.DataFrame(b)
    c=list(b.values())
    s=list(b.keys())

    df=pd.DataFrame(p.tables[3][1:],columns=p.tables[3][0])
    df1=df.groupby('Date')
    d={}
    data={}
    for Date,group in df1:            
        group=group.drop(columns=['Date'])
        group=group.to_json(orient='index')
        group=json.loads(group)
        for i in range(0,len(c)):
            d.update({str(c[i]):list(group.values())})
        for i in d.items():
            data.update({Date:i})
    return data


app=Flask(__name__)
@app.route('/qrcode', methods=['GET'])
def data():
    return get_data_browsers('http://qrcode.samisme.cf:8080/services/example')

app.run()
