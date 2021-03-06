import pymysql as p
import os
import requests
from dotenv import load_dotenv
import time
#import query as q

load_dotenv()

host = os.environ.get('RDS_URL')
user = os.environ.get('RDS_USER')
password = os.environ.get('RDS_PASS')
database = os.environ.get('RDS_DB')
key=os.environ.get('API_KEY')
lat=os.environ.get('LATITUDE')
lng=os.environ.get('LONGTITUDE')

#cur=q.db().cursor()
con=p.connect(host=host,user=user,password=password,database=database)
cur=con.cursor()

def get_image(site,account,ad,rule):

    query1="select image from qrcode where site = {} and account = {} and ad = {} and rule = {};".format(site,account,ad,rule)

    cur.execute(query1)

    img = cur.fetchone()[0]

    return img


def current_temp():
    
    api="https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=hourly,daily&appid={}".format(lat,lng,key)

    r=requests.get(api)

    data=r.json()

    F=float(data['current']['temp'])

    c=F-273.15

    return c


def get_temp(site,account,ad,rule):

    c=current_temp()

    if 20<c>28:
        ad=4
        return get_image(site,account,ad,rule)

    elif 28<=c>=35:
        ad=5
        return get_image(site,account,ad,rule)
        
    else:
        ad=6
        return get_image(site,account,ad,rule)

    
def get_timing(site,account,ad,rule):

    tm=time.strftime('%p')

    if tm=='AM':
        ad=2
        return get_image(site,account,ad,rule)

    else:
        ad=3
        return get_image(site,account,ad,rule)



