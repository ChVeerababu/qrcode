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

def get_image(qr,site,typ):

    query1="select image from qrcode where qr = {} and site = {} and typ = {};".format(qr,site,typ)

    cur.execute(query1)

    img = cur.fetchone()[0]

    query2='select name from qrcode_image where id = {}'.format(img)

    cur.execute(query2)

    res = cur.fetchone()[0]

    return res

