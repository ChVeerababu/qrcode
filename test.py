import pymysql as p
import os
import requests
from dotenv import load_dotenv
import time


load_dotenv()

host = os.environ.get('RDS_URL')
user = os.environ.get('RDS_USER')
password = os.environ.get('RDS_PASS')
database = os.environ.get('RDS_DB')
#key=os.environ.get('API_KEY')
#lat=os.environ.get('LATITUDE')
#long=os.environ.get('LONGTITUDE')


con=p.connect(host=host,user=user,password=password,database=database)
cur=con.cursor()

def get_image(site,account,ad,rule):

    query1="select image from qrcode where site = {} and account = {} and ad = {} and rule = {};".format(site,account,ad,rule)

    cur.execute(query1)

    img = cur.fetchone()[0]

    return img

def current_temp():
    
    api="https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=hourly,daily&appid={}".format(lat,long,key)
    r=requests.get(api)
    data=r.json()
    F=float(data['current']['temp'])
    c=F-273.15
    return c

'''def current_temp():
    c=current_temp()
    if 20<c>28:
        return render_template('index.html',res = res)
    elif 28<=c>=35:
        return render_template('index.html',res = res)
    else:
        return render_template('index.html',res = res)
def current_time():
    tm=time.strftime('%P')
    elif tm=='AM':
        return render_template('index.html',res = res)
    else:
        return render_template('index.html',res = res)'''



