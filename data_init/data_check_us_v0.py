import pandas as pd
import json
import yfinance as yf
import numpy as np
import psycopg2
from psycopg2.extras import execute_values
from tqdm import tqdm
import os
#with open('assets_us.json') as f:
# 確保文件路徑正確
file_path = os.path.join(os.path.dirname(__file__), 'assets_us.json')
with open(file_path) as f:
    data_tw = json.load(f)


#SQL　setting
#SQL_CONFIG = dict(database="portfolio_platform", user='postgres', password='password', host='db',port ='5432')
SQL_CONFIG = dict(database="portfolio_platform", user='postgres', password='password', host='localhost',port ='5432')

# 設定已下市的股票代號
delisted_tickers  = {
    "ATVI", "CDAY", "FLT", "PEAK", "PXD", "SGEN", "WRK"
}

# 移除不需要更新的股票代號
data_tw = {ticker: data_tw[ticker] for ticker in data_tw if ticker not in delisted_tickers }


# US Stocks
conn = psycopg2.connect(**SQL_CONFIG)
cursor = conn.cursor()

# 獲取目前資料庫中所有股票代號
cursor.execute("SELECT DISTINCT ticker FROM stock_price")
existing_tickers = {row[0] for row in cursor.fetchall()}

# 計算出不在 data_tw 中的股票代號集合
tickers_to_remove = existing_tickers - set(data_tw.keys())

# 清除不在 data_tw 中的股票代號
for ticker in tickers_to_remove:
    cursor.execute("DELETE FROM stock_price WHERE ticker = %s", (ticker,))
    conn.commit()
    print(f"#### 清除不在list中的股票代號 : {ticker}  ")


# 檢查DB中是否有data_tw中的股票代號，沒有就抓取
cursor.execute("SELECT DISTINCT ticker FROM stock_price")
existing_tickers = {row[0] for row in cursor.fetchall()}
to_add_tickers = {ticker for ticker in data_tw if ticker not in existing_tickers}

for ticker in tqdm(to_add_tickers):
    df = yf.download(ticker, start="2007-1-1", progress=False)
    if not df.empty:
        #values = [(ticker, df.index[i], df['Close'][i]) for i in range(len(df))]
        values = [(ticker, df.index[i], df['Close'].iloc[i]) for i in range(len(df))]

        execute_values(cursor, "INSERT INTO stock_price (ticker, date, price) VALUES %s", values)
        conn.commit()
        print(f"#### 補抓list中的缺漏的股票代號 : {ticker}  ")

# 列出資料庫中的股票代號數量
cursor.execute("SELECT COUNT(DISTINCT ticker) FROM stock_price")
num_tickers = cursor.fetchone()[0]
print(f"#### There are {num_tickers} unique tickers in the database. 資料庫中的股票代號數量 ")

cursor.close()
conn.close()