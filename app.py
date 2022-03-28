import urllib.request
from pprint import pprint
from html_table_parser.parser import HTMLTableParser
import pandas as pd
import json
from flask import Flask,jsonify,render_template
import pymysql as p


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

con=p.connect(host="database-1.czejdnwyu0eq.ap-south-1.rds.amazonaws.com",user="root",password="Ivisivis5",database="QRCODE_DATA")
cur=con.cursor()

sql="insert into QRCODE(DATE,TIME,IP,BROWSER,OS)values(%s,%s,%s,%s, %s)"


app=Flask(__name__)
@app.route('/')
def index():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        data={'ip': str(request.environ['REMOTE_ADDR']),'timestamp':datetime.now(),'browser':str(request.user_agent._browser), 'os':str(request.user_agent._platform)}
        tm=data['timestamp'].strftime("%Y-%m-%d %H-%M-%S")
        cur.executemany(sql,[(tm[:10],tm[11:],data['ip'],data['browser'],data['os'])])
        con.commit()
        
    else:
        data={'ip': str(request.environ['HTTP_X_FORWARDED_FOR']),'timestamp':datetime.now(),'browser':str(request.user_agent._browser), 'os':str(request.user_agent._platform)}
        tm=data['timestamp'].strftime("%Y-%m-%d %H-%M-%S")
        cur.executemany(sql,[(tm[:10],tm[11:],data['ip'],data['browser'],data['os'])])
        con.commit()
        
    return render_template('index.html')
@app.route('/qrcode', methods=['GET'])
def data():
    return get_data_browsers('http://qrcode.samisme.cf:8080/services/example')

if __name__ == '__main__':
    app.run()
