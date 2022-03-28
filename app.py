import urllib.request
from pprint import pprint
from html_table_parser.parser import HTMLTableParser
import pandas as pd
import json
from flask import Flask,jsonify


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
            data.update({Date:i})#[str(c[i]):list(group.values())]
    asdf=json.dumps(data,indent=4)
    return asdf
    



'''get_data_browsers('http://qrcode.samisme.cf:8080/services/example')


            
        #
             #i
    #main=json.loads(data)
    #dags=json.dumps(data)
    #return json.dumps(data, sort_keys=True, indent=4) #, default=json_util.default
    #anm=jsonify(**data)
    #res=list(zip(data.items()))
    #res=jsonify(data)  #, sort_keys=True
    #nms=json.loads(res)'''
    



app=Flask(__name__)
@app.route('/')
def index():
    return "Hello World"
@app.route('/qrcode', methods=['GET'])
def data():
    return get_data_browsers('http://qrcode.samisme.cf:8080/services/example')

if __name__ == '__main__':
    app.run()
