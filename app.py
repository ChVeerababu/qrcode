import json
import pymysql as p
import time
import pandas as pd
import threading
import os
from flask import Flask, render_template, flash, request, redirect, url_for,send_file


from test import get_image

from dotenv import load_dotenv

load_dotenv()

host = os.environ.get('RDS_URL')
user = os.environ.get('RDS_USER')
password = os.environ.get('RDS_PASS')
database = os.environ.get('RDS_DB')

rest=[]

app=Flask(__name__)



account = os.environ.get('QRCODE_ACCOUNT')
site =os.environ.get('QRCODE_SITE')
ad = 1



@app.route('/', methods=['GET'])
def index():
    tm=time.strftime("%Y-%m-%d %H-%M-%S")
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        data={'ip': request.environ['REMOTE_ADDR'],'timestamp':tm,'browser':request.user_agent._browser, 'os':request.user_agent._platform }
        a = [tm[:10],tm[11:13],data['ip'],data['browser'],data['os']]
    else:
        data={'ip': request.environ['HTTP_X_FORWARDED_FOR'],'timestamp':tm,'browser':request.user_agent._browser, 'os':request.user_agent._platform }
        a = [tm[:10],tm[11:13],data['ip'],data['browser'],data['os']] 

    threading.Thread(target=dbstdata(a,data)).start()

    
    try:
        res = get_image(site,account,ad)
    except:
        res = None


    return render_template('index.html',res = res)


def dbstdata(a,data):
    tm=time.strftime("%Y-%m-%d %H-%M-%S")
    con=p.connect(host=host,user=user,password=password,database=database)
    cur=con.cursor()
    sql="insert into RawData(Date,Hour,Ip,Browser,Os,SITE)values(%s,%s,%s,%s,%s,%s)"
    sqls="insert into HourWise(SITE,DATE,HOUR,VISITS,UNIQUES,BROWSER,OS,IP)values(%s,%s,%s,%s,%s,%s,%s,%s)"
    cur.executemany("select * from HourWise where Date=%s and Hour=%s and SITE=%s order by Date and Hour",[(tm[:10],tm[11:13],site)])
    check=cur.fetchall()

    cur.executemany(sql,[(a[0],a[1],a[2],a[-2],a[-1],site)])
    con.commit() 

    if len(check)==0:
        rest.clear()
    if len(rest)==0:
        v,u=1,1
        mn=[tm[:10],tm[11:13],v,u,{data['browser']:1},{data['os']:1},[data['ip']]]
        rest.append(mn)
        if len(check)==0:
            cur.executemany(sqls,[(site,rest[-1][0],rest[-1][1],str(rest[-1][2]),str(rest[-1][3]),str(rest[-1][-3]),str(rest[-1][-2]),str(rest[-1][-1]))])
            con.commit()
        if len(check)==1:
            cur.executemany("update HourWise set SITE=%s, VISITS=%s,UNIQUES=%s,BROWSER=%s,OS=%s,IP=%s where DATE=%s and HOUR=%s and SITE=%s order by DATE and HOUR desc limit 1",\
            [(site,str(rest[-1][2]),str(rest[-1][3]),str(rest[-1][-3]),str(rest[-1][-2]),str(rest[-1][-1]),tm[:10],tm[11:13],site)])
            con.commit()
    

    else:
        
        rest[-1][-1]=eval(check[-1][-2])
        rest[-1][-2]=eval(check[-1][-3])
        rest[-1][2]=eval(check[-1][2])
        rest[-1][3]=eval(check[-1][3])
        rest[-1][4]=eval(check[-1][4])
        rest[-1][2]+=1
        
        if a[2] not in rest[-1][-1]:
            rest[-1][3]+=1
            rest[-1][-1].append(a[2])
        if a[3] in rest[-1][4]:
            rest[-1][4][a[3]] += 1
        else:
            rest[-1][4][a[3]] = 1
        if a[-1] in rest[-1][-2]:
            rest[-1][-2][a[-1]] += 1
        else:
            rest[-1][-2][a[-1]] = 1
        if len(check)==0:
            cur.executemany(sqls,[(site,rest[-1][0],rest[-1][1],str(rest[-1][2]),str(rest[-1][3]),str(rest[-1][-3]),str(rest[-1][-2]),str(rest[-1][-1]))])
            con.commit()
        if len(check)==1:
            cur.executemany("update HourWise set SITE=%s,VISITS=%s,UNIQUES=%s,BROWSER=%s,OS=%s,IP=%s where DATE=%s and HOUR=%s and SITE=%s order by DATE and HOUR desc limit 1",\
            
            [(site,str(rest[-1][2]),str(rest[-1][3]),str(rest[-1][-3]),str(rest[-1][-2]),str(rest[-1][-1]),tm[:10],tm[11:13],site)])
            con.commit()

def db(database_name=database):
    return p.connect(host=host,user=user,password=password,database=database)

def query_db(query, args=(), one=False):
    cur = db().cursor()
    cur.execute(query, args)
    r = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
    cur.connection.close()
    return (r[0] if r else None) if one else r





@app.route('/hr/result', methods=['GET'])
def res():
    
    my_query = query_db("select * from HourWise")

    json_output = json.dumps(my_query)
    
    jsn=eval(json_output)

    d={}
    date=[]
    l=[]
    for i in jsn:
        if i['DATE'] in date:
            l.append(i)
            d[i['DATE']]=l
            del i['DATE']
            del i['IP']
        else:
            date.append(i['DATE'])
            d[i['DATE']]=[i]
            del i['DATE']
            del i['IP']
            l=[i]
    dfc=json.dumps(d,indent=4)
    return dfc


if __name__=="__main__":
    app.run(host='0.0.0.0',port=5000)






