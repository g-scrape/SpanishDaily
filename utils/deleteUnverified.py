#to be ran via cron task

import mysql.connector
import os
from datetime import date
import datetime

#grab envVars locally or in prod
path = ''
if os.name == 'nt':
    path = 'C:/Users/glens/.spyder-py3/Practice Projects/SpanishDaily/SpanishDaily/home/gharold/utils/env_vars.py'
elif os.name == 'posix':
    path = '/home/gharold/utils/env_vars.py'

exec(open(path).read())

#open DB connection
connection = mysql.connector.connect(
    host=os.environ.get('DB_HOST'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASS'),
    database=os.environ.get('DB_NAME')
    )

cur = connection.cursor()

#get today's date
today = date.today()
#get a week ago
weekAgo = today - datetime.timedelta(days=7)

#count and log number of users eligble for deletion
selectQuery = f"SELECT userId from users WHERE signupDate < '{weekAgo}' and verifiedEmail = 0"

cur.execute(selectQuery)
#get number of eligible users
numDeleted = len(cur.fetchall())

if numDeleted > 0:
    #delete users
    deleteQuery = f"DELETE FROM users WHERE signupDate < '{weekAgo}' and verifiedEmail = 0"
    cur.execute(deleteQuery)

    connection.commit()

print(str(numDeleted) + " accounts deleted due to being unverified")

## do it again for the un-subbed users

#get today's date
today = date.today()
#get a week ago
monthAgo = today - datetime.timedelta(days=30)

#count and log number of users eligble for deletion
selectQuery = f"SELECT userId from users WHERE subChangeDate < '{monthAgo}' and sendEmail = 0"

cur.execute(selectQuery)
#get number of eligible users
numDeleted = len(cur.fetchall())

if numDeleted > 0:
    #delete users
    deleteQuery = f"DELETE FROM users WHERE subChangeDate < '{monthAgo}' and sendEmail = 0"
    cur.execute(deleteQuery)

    connection.commit()

print(str(numDeleted) + " accounts deleted due to being unsubscribed")