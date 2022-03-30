import urllib.request
from pprint import pprint
from html_table_parser.parser import HTMLTableParser
import pandas as pd
import json
from flask import Flask,jsonify,render_template,request
import pymysql as p
from datetime import datetime





con=p.connect(host="database-1.czejdnwyu0eq.ap-south-1.rds.amazonaws.com",user="root",password="Ivisivis5",database="QRCODE_DATA")
cur=con.cursor()
#cur.execute("create table Hour_Wise_Data(DATE date,HOUR char(10),VISITS int(10),UNIQUES int(10),BROWSER VARCHAR(65530),OS VARCHAR(65530),IP VARCHAR(65530))")
#con.commit()
app=Flask(__name__)
con.commit()
sql="insert into Raw_Data(Date,Hour,Ip,Browser,Os)values(%s,%s,%s,%s,%s)"
sqls="insert into Hour_Wise_Data(DATE,HOUR,VISITS,UNIQUES,BROWSER,OS,IP)values(%s,%s,%s,%s,%s,%s,%s)"
#upsql="update Hour_Wise_Data set VISITS=v
#create table Raw_Data(Date char(20),Hour char(10),Ip char(20),Browser char(30),Os char(30))


@app.route('/')
def index():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        v,u=1,1
        data={'ip': str(request.environ['REMOTE_ADDR']),'timestamp':datetime.now(),'browser':str(request.user_agent._browser), 'os':str(request.user_agent._platform)}
        tm=data['timestamp'].strftime("%Y-%m-%d %H-%M-%S")
        cur.executemany(sql,[(tm[:10],tm[11:13],data['ip'],data['browser'],data['os'])])
        con.commit()
        cur.execute("select * from Raw_Data")
        b=cur.fetchall()
        print("raw:",b)
        
        cur.executemany("select * from Hour_Wise_Data where DATE=%s and HOUR=%s",[(str(tm[:10]),str(tm[11:13]))])
        a=cur.fetchall()
        if len(a)==0:
            cur.executemany(sqls,[(tm[:10],tm[11:13],v,u,data['browser'],data['os'],data['ip'])])
            con.commit()

        else:
            bro,os,ip=[a[0][-3]],[a[0][-2]],[a[0][-1]]
            v,u=a[0][2],a[0][3]
            if a[0][-1] != data['ip'] and a[0][-2] != data['os']  and a[0][-3] != data['browser'] :
                bro.append(data['browser'])
                os.append(data['os'])
                ip.append(data['ip'])
                cur.executemany("update Hour_Wise_Data set VISITS=%s,UNIQUES=%s,BROWSER=%s,OS=%s,IP=%s where DATE=%s and HOUR=%s",[(str(v+1),str(u+1),bro,os,ip,tm[:10],tm[11:13])])
                con.commit()
            elif a[0][-1] == data['ip'] and a[0][-2] == data['os']  and a[0][-3] == data['browser'] :

                cur.executemany("update Hour_Wise_Data set VISITS=%s,UNIQUES=%s,BROWSER=%s,OS=%s,IP=%s where DATE=%s and HOUR=%s",[(str(v+1),str(u),bro,os,ip,tm[:10],tm[11:13])])
                con.commit()
            elif a[0][-1] != data['ip'] and a[0][-2] == data['os']  and a[0][-3] == data['browser'] :

                ip.append(data['ip'])
                cur.executemany("update Hour_Wise_Data set VISITS=%s,UNIQUES=%s,BROWSER=%s,OS=%s,IP=%s where DATE=%s and HOUR=%s",[(str(v+1),str(u+1),bro,os,ip,tm[:10],tm[11:13])])
                con.commit()
            elif a[0][-1] != data['ip'] and a[0][-2] != data['os']  and a[0][-3] == data['browser'] :
                os.append(data['os'])
                ip.append(data['ip'])
                cur.executemany("update Hour_Wise_Data set VISITS=%s,UNIQUES=%s,BROWSER=%s,OS=%s,IP=%s where DATE=%s and HOUR=%s",[(str(v+1),str(u+1),bro,os,ip,tm[:10],tm[11:13])])
                con.commit()
            elif a[0][-1] != data['ip'] and a[0][-2] == data['os']  and a[0][-3] != data['browser'] :
                bro.append(data['browser'])
                ip.append(data['ip'])
                cur.executemany("update Hour_Wise_Data set VISITS=%s,UNIQUES=%s,BROWSER=%s,OS=%s,IP=%s where DATE=%s and HOUR=%s",[(str(v+1),str(u+1),bro,os,ip,tm[:10],tm[11:13])])
                con.commit()
            elif a[0][-1] == data['ip'] and a[0][-2] != data['os']  and a[0][-3] != data['browser'] :
                bro.append(data['browser'])
                os.append(data['os'])
                cur.executemany("update Hour_Wise_Data set VISITS=%s,UNIQUES=%s,BROWSER=%s,OS=%s,IP=%s where DATE=%s and HOUR=%s",[(str(v+1),str(u),bro,os,ip,tm[:10],tm[11:13])])
                con.commit()
            elif a[0][-1] == data['ip'] and a[0][-2] == data['os']  and a[0][-3] != data['browser'] :
                bro.append(data['browser'])
                cur.executemany("update Hour_Wise_Data set VISITS=%s,UNIQUES=%s,BROWSER=%s,OS=%s,IP=%s where DATE=%s and HOUR=%s",[(str(v+1),str(u),bro,os,ip,tm[:10],tm[11:13])])
                con.commit()
            elif a[0][-1] == data['ip'] and a[0][-2] != data['os']  and a[0][-3] == data['browser'] :
                os.append(data['os'])
                cur.executemany("update Hour_Wise_Data set VISITS=%s,UNIQUES=%s,BROWSER=%s,OS=%s,IP=%s where DATE=%s and HOUR=%s",[(str(v+1),str(u),bro,os,ip,tm[:10],tm[11:13])])
                con.commit()
            else:
                return a[0]

        return "hello"
            
        
    else:
        v,u=1,1
        data={'ip': str(request.environ['HTTP_X_FORWARDED_FOR']),'timestamp':datetime.now(),'browser':str(request.user_agent._browser), 'os':str(request.user_agent._platform)}
        tm=data['timestamp'].strftime("%Y-%m-%d %H-%M-%S")
        cur.executemany(sql,[(tm[:10],tm[11:13],data['ip'],data['browser'],data['os'])])
        con.commit()
        cur.executemany(sqls,[(tm[:10],tm[11:13],str(v),str(u),data['browser'],data['os'],data['ip'])])
        con.commit()
        cur.execute("select * from Raw_Data")
        b=cur.fetchall()
        print("raw:",b)
        cur.executemany("select * from Hour_Wise_Data where DATE=%s or HOUR=%s",[(str(tm[:10]),str(tm[11:13]))])
        a=cur.fetchall()
        bro,os,ip=[],[],[]
        if len(a)==0:
            cur.executemany(sqls,[(tm[:10],tm[11:13],v,u,data['browser'],data['os'],data['ip'])])
            con.commit()

        else:
            bro,os,ip=[a[0][-3]],[a[0][-2]],[a[0][-1]]
            v,u=a[0][2],a[0][3]
            if a[0][-1] != data['ip'] and a[0][-2] != data['os']  and a[0][-3] != data['browser'] :
                bro.append(data['browser'])
                os.append(data['os'])
                ip.append(data['ip'])
                cur.executemany("update Hour_Wise_Data set VISITS=%s,UNIQUES=%s,BROWSER=%s,OS=%s,IP=%s where DATE=%s and HOUR=%s",[(str(v+1),str(u+1),bro,os,ip,tm[:10],tm[11:13])])
                con.commit()
            elif a[0][-1] == data['ip'] and a[0][-2] == data['os']  and a[0][-3] == data['browser'] :

                cur.executemany("update Hour_Wise_Data set VISITS=%s,UNIQUES=%s,BROWSER=%s,OS=%s,IP=%s where DATE=%s and HOUR=%s",[(str(v+1),str(u),bro,os,ip,tm[:10],tm[11:13])])
                con.commit()
            elif a[0][-1] != data['ip'] and a[0][-2] == data['os']  and a[0][-3] == data['browser'] :

                ip.append(data['ip'])
                cur.executemany("update Hour_Wise_Data set VISITS=%s,UNIQUES=%s,BROWSER=%s,OS=%s,IP=%s where DATE=%s and HOUR=%s",[(str(v+1),str(u+1),bro,os,ip,tm[:10],tm[11:13])])
                con.commit()
            elif a[0][-1] != data['ip'] and a[0][-2] != data['os']  and a[0][-3] == data['browser'] :
                os.append(data['os'])
                ip.append(data['ip'])
                cur.executemany("update Hour_Wise_Data set VISITS=%s,UNIQUES=%s,BROWSER=%s,OS=%s,IP=%s where DATE=%s and HOUR=%s",[(str(v+1),str(u+1),bro,os,ip,tm[:10],tm[11:13])])
                con.commit()
            elif a[0][-1] != data['ip'] and a[0][-2] == data['os']  and a[0][-3] != data['browser'] :
                bro.append(data['browser'])
                ip.append(data['ip'])
                cur.executemany("update Hour_Wise_Data set VISITS=%s,UNIQUES=%s,BROWSER=%s,OS=%s,IP=%s where DATE=%s and HOUR=%s",[(str(v+1),str(u+1),bro,os,ip,tm[:10],tm[11:13])])
                con.commit()
            elif a[0][-1] == data['ip'] and a[0][-2] != data['os']  and a[0][-3] != data['browser'] :
                bro.append(data['browser'])
                os.append(data['os'])
                cur.executemany("update Hour_Wise_Data set VISITS=%s,UNIQUES=%s,BROWSER=%s,OS=%s,IP=%s where DATE=%s and HOUR=%s",[(str(v+1),str(u),bro,os,ip,tm[:10],tm[11:13])])
                con.commit()
            elif a[0][-1] == data['ip'] and a[0][-2] == data['os']  and a[0][-3] != data['browser'] :
                bro.append(data['browser'])
                cur.executemany("update Hour_Wise_Data set VISITS=%s,UNIQUES=%s,BROWSER=%s,OS=%s,IP=%s where DATE=%s and HOUR=%s",[(str(v+1),str(u),bro,os,ip,tm[:10],tm[11:13])])
                con.commit()
            elif a[0][-1] == data['ip'] and a[0][-2] != data['os']  and a[0][-3] == data['browser'] :
                os.append(data['os'])
                cur.executemany("update Hour_Wise_Data set VISITS=%s,UNIQUES=%s,BROWSER=%s,OS=%s,IP=%s where DATE=%s and HOUR=%s",[(str(v+1),str(u),bro,os,ip,tm[:10],tm[11:13])])
                con.commit()
            else:
                return a[0]

            
    return render_template('index.html')





'''@app.route('/')
def index():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        data={'ip': str(request.environ['REMOTE_ADDR']),'timestamp':datetime.now(),'browser':str(request.user_agent._browser), 'os':str(request.user_agent._platform)}
        tm=data['timestamp'].strftime("%Y-%m-%d %H-%M-%S")
        cur.executemany(sql,[(tm[:10],tm[11:13],data['ip'],data['browser'],data['os'])])
        con.commit()
        
    else:
        data={'ip': str(request.environ['HTTP_X_FORWARDED_FOR']),'timestamp':datetime.now(),'browser':str(request.user_agent._browser), 'os':str(request.user_agent._platform)}
        tm=data['timestamp'].strftime("%Y-%m-%d %H-%M-%S")
        cur.executemany(sql,[(tm[:10],tm[11:13],data['ip'],data['browser'],data['os'])])
        con.commit()
        
    
@app.route('/qrcode', methods=['GET'])
def data():
    return get_data_browsers('http://qrcode.samisme.cf:8080/services/example')'''

if __name__ == '__main__':
    app.run()
