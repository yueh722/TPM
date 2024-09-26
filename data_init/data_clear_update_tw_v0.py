import pandas as pd
import json
import yfinance as yf
import numpy as np
import psycopg2
from psycopg2.extras import execute_values
from tqdm import tqdm
import os
##with open('assets_tw.json') as f:
# 確保文件路徑正確
file_path = os.path.join(os.path.dirname(__file__), 'assets_tw.json')
with open(file_path) as f:
    data_tw = json.load(f)


#SQL　setting
#SQL_CONFIG = dict(database="portfolio_platform", user='postgres', password='password', host='db',port ='5432')
SQL_CONFIG = dict(database="portfolio_platform", user='postgres', password='password', host='localhost',port ='5432')

# TW Stocks
conn = psycopg2.connect(**SQL_CONFIG)
cursor = conn.cursor()
cursor.execute("TRUNCATE TABLE stock_price_tw")
print("TW stock price cleared")
for ticker in tqdm(data_tw):
    df = yf.download(ticker, start="2007-1-1", progress=False)
    value =[(ticker, df.index[i], df['Close'][i]) for i in range(len(df))]
    with conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curs:
            sql = "insert into stock_price_tw (ticker, date, price) values %s"
            execute_values(curs, sql, value)
print("TW stock price updated")
