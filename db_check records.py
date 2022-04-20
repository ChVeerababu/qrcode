import pymysql as p
import time


tm=time.strftime("%Y-%m-%d %H-%M-%S")
con=p.connect(host="database-1.czejdnwyu0eq.ap-south-1.rds.amazonaws.com",user="root",password="Ivisivis5",database="QRCODE_DATA")
cur=con.cursor()
cur.executemany("select * from HourWise where Date=%s and Hour=%s order by Date and Hour",[(tm[:10],tm[11:13])])
check=cur.fetchall()
print(check)
print(len(check))
