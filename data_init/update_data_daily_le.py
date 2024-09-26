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

import requests
import configparser
import time
import os
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
            try:
                df = yf.download(ticker, start=latest_date.strftime('%Y-%m-%d'),
                                 end=datetime.date.today().strftime('%Y-%m-%d'), progress=False)

                if df.empty:
                        raise Exception(f"No data returned for {ticker}")

            except Exception as e:
                    # Send error message if data fetching fails
                    error_msg = f"Error fetching data for {ticker}: {str(e)}"
                    send_message(error_msg)
                    continue  # Skip this ticker if data fetch fails 


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
            try:
                df = yf.download(ticker, start=latest_date.strftime('%Y-%m-%d'),
                                end=datetime.date.today().strftime('%Y-%m-%d'), progress=False)

            except Exception as e:
                    # Send error message if data fetching fails
                    error_msg = f"Error fetching data for {ticker}: {str(e)}"
                    send_message(error_msg)
                    continue  # Skip this ticker if data fetch fails 


            value = [(ticker, df.index[i], df['Close'][i]) for i in range(len(df))]
            with conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curs:
                    sql = "insert into stock_price_tw (ticker, date, price) values %s"
                    execute_values(curs, sql, value)
    print("Stock prices TW updated")

#=================================
#config_file = 'config.ini'

TIMER = 3
# for telegram bot
#TG_TOKEN = 6554601926:AAFluHl3lfFrjSuifdn_-sW6hA21Estpm28
#TG_CHAT_ID = 871430150


def get_config():
    global TIMER
    global TG_TOKEN, TG_CHAT_ID

    file_path = os.path.join(os.path.dirname(__file__), 'config.ini')

    try:
        
        #with open(config_file, 'r') as fp: #use this way to avoid not-close isseue
        with open(file_path, 'r') as fp:
            config = configparser.ConfigParser()
            config.read_file(fp)
            fp.close()
    except:
        raise Exception('ERROR loading config file: ', config_file, '\n')

    TIMER = int(eval(config['GENERAL']['TIMER']))

    # telegram settings
    TG_TOKEN = config['TELEGRAM']['tg_token']
    TG_CHAT_ID = config['TELEGRAM']['tg_chat_id']
    if not(TG_TOKEN and TG_CHAT_ID):
        raise Exception('ERROR initializing TG_TOKEN or TG_CHAT_ID\n', 'TG_TOKEN: ', TG_TOKEN, '\n', 'TG_CHAT_ID:', TG_CHAT_ID, '\n')

    

    return

## 發送Telegram 訊息
def send_message(msg):
    # 1. print in lost
    print(TG_TOKEN)
    print(TG_CHAT_ID)
    print(msg)
    # 2. sned message to TG
    if msg is None:
        print("No message!")
        return

    while (True):
        try:
            tgurl = f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={TG_CHAT_ID}&text=' + msg
            requests.get(tgurl)
            break
        except:
            time.sleep(TIMER)
            #raise Exception('ERROR sending message to TG\n')

    return


get_config()
msg = ""
msg += "Telegram robot init ok! (update_data_daily_le.py)\n"
send_message(msg)

#=================================

# Schedule the task
schedule.every().day.at("17:00").do(update_data)
schedule.every().day.at("18:00").do(update_data_tw)
# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)