import pymysql as p
import os

from dotenv import load_dotenv

load_dotenv()

host = os.environ.get('RDS_URL')
user = os.environ.get('RDS_USER')
password = os.environ.get('RDS_PASS')
database = os.environ.get('RDS_DB')

con=p.connect(host=host,user=user,password=password,database=database)
cur=con.cursor()

def get_image(site,account,ad):

    query1="select image from qrcode where site = {} and account = {} and ad = {};".format(site,account,ad)

    cur.execute(query1)

    img = cur.fetchone()[0]

    return img

