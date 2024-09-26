import pandas as pd
import json
import yfinance as yf
import numpy as np
import psycopg2
from psycopg2.extras import execute_values
from tqdm import tqdm
import datetime
import schedule
import time
from config import SQL_CONFIG
#SQL　setting

def update_data():
    # Connect to the database
    conn = psycopg2.connect(**SQL_CONFIG)
    cursor = conn.cursor()
    print("Stock prices US updating")
    # Get the list of tickers
    cursor.execute("SELECT DISTINCT ticker FROM stock_price")
    tickers = [row[0] for row in cursor.fetchall()]

    for ticker in tqdm(tickers):
        # Get the latest date for this ticker
        cursor.execute(f"SELECT MAX(date) FROM stock_price WHERE ticker = '{ticker}'")
        latest_date = cursor.fetchone()[0]
        # If the latest date is not today, update the data
        if latest_date < datetime.date.today():
            df = yf.download(ticker, start=latest_date.strftime('%Y-%m-%d'),
                             end=datetime.date.today().strftime('%Y-%m-%d'), progress=False)
            value = [(ticker, df.index[i], df['Close'][i]) for i in range(len(df))]
            with conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curs:
                    sql = "insert into stock_price (ticker, date, price) values %s"
                    execute_values(curs, sql, value)
    print("Stock prices US updated")
def update_data_tw():
    # Connect to the database
    conn = psycopg2.connect(**SQL_CONFIG)
    cursor = conn.cursor()
    print("Stock prices US updating")
    # Get the list of tickers
    cursor.execute("SELECT DISTINCT ticker FROM stock_price_tw")
    tickers = [row[0] for row in cursor.fetchall()]

    for ticker in tqdm(tickers):
        # Get the latest date for this ticker
        cursor.execute(f"SELECT MAX(date) FROM stock_price_tw WHERE ticker = '{ticker}'")
        latest_date = cursor.fetchone()[0]
        # If the latest date is not today, update the data
        if latest_date < datetime.date.today():
            df = yf.download(ticker, start=latest_date.strftime('%Y-%m-%d'),
                             end=datetime.date.today().strftime('%Y-%m-%d'), progress=False)
            value = [(ticker, df.index[i], df['Close'][i]) for i in range(len(df))]
            with conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curs:
                    sql = "insert into stock_price_tw (ticker, date, price) values %s"
                    execute_values(curs, sql, value)
    print("Stock prices TW updated")
# Schedule the task
schedule.every().day.at("17:00").do(update_data)
schedule.every().day.at("18:00").do(update_data_tw)
# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)