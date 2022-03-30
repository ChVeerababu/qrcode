import urllib.request
from pprint import pprint
from html_table_parser.parser import HTMLTableParser
import pandas as pd
import json
from flask import Flask,jsonify,render_template,request
import pymysql as p
from datetime import datetime




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


def db(database_name='QRCODE_DATA'):
    return p.connect(host="database-1.czejdnwyu0eq.ap-south-1.rds.amazonaws.com",user="root",password="Ivisivis5",database=database_name)

def query_db(query, args=(), one=False):
    cur = db().cursor()
    cur.execute(query, args)
    r = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
    cur.connection.close()
    return (r[0] if r else None) if one else r
def dbcheck():
    
    my_query = query_db("select * from QRCODE")

    json_output = json.dumps(my_query,indent=4)

    df=pd.DataFrame(my_query)
    #print(df)
    date=list(df.groupby(['DATE']).groups.keys())
    vis=df['DATE'].value_counts().to_dict()
    #print(vis)
    #vis=list(vis.values())
    unis=df.groupby(['DATE','IP']).size().reset_index(name='COUNT')
    uni=unis['DATE'].value_counts().to_dict()
    #print(uni)
    #uni=list(uni.values())
    bro=df.value_counts(['DATE','BROWSER'])
    data = bro.to_dict()
    bro_data =  [(i[0],{i[1]:data[i]}) for i in data]
    #print(bro_data)
    d={}
    for i in bro_data:
        if i[0] not in d:
            d[i[0]]=[i[1]]
        else:
            d[i[0]].append(i[1])

    #bro = list(d.values())
    #print(d)
    #print(bro)
    os=df.value_counts(['DATE','OS'])
    data = os.to_dict()
    os_data =  [(i[0],{i[1]:data[i]}) for i in data]
    e={}
    for i in os_data:
        if i[0] not in e:
            e[i[0]]=[i[1]]
        else:
            e[i[0]].append(i[1])

    #os = list(e.values())
    #print(os)
    #print(e)
    fdf={}
    for i in list(vis.keys()):
        fdf.update({i:[{'VISITS':vis.get(i)},{'UNIQUES':uni.get(i)},{'BROWSERS':d.get(i)},{'OS':e.get(i)}]})    

    return json.dumps(fdf,indent=4)
   



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
@app.route('/api/v1/daywise')
def daywise():
    return dbcheck()




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

        '''else:
            if 
            cur.execute("update Hour_Wise_Data set VISITS=%d,  where DATE=%s and HOUR=%s",[v+1,u+1,tm[:10],tm[11:13]]))
            con.commit()      '''

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
        con.commit()'''
        
    
@app.route('/qrcode', methods=['GET'])
def data():
    return get_data_browsers('http://qrcode.samisme.cf:8080/services/example')

if __name__ == '__main__':
    app.run()'''
