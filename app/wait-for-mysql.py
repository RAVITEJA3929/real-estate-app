import pymysql
import sys
import time
import os

db_config = {}
with open('database.db', 'r') as f:
    for line in f:
        if '=' in line.strip():
            key, value = line.strip().split('=', 1)
            db_config[key] = value

max_retries = 30
retry_count = 0
while retry_count < max_retries:
    try:
        conn = pymysql.connect(host=db_config['host'], user=db_config['user'], password=db_config['password'], database=db_config['database'], connect_timeout=5)
        conn.close()
        sys.exit(0)
    except:
        retry_count += 1
        time.sleep(1)

sys.exit(1)
