import yfinance as yf
import json
import os

def check_delisted_tickers(tickers):
    delisted_tickers = []
    for ticker in tickers:
        # 獲取股票的數據
        stock = yf.Ticker(ticker)
        
        # 獲取股票的歷史價格 ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        hist = stock.history(period="max")
        
        # 如果沒有數據，認為該股票已下市
        if hist.empty:
            delisted_tickers.append(ticker)
    
    return delisted_tickers
    
print("=" * 20)    

# 檢查美股下市的股票
file_path_us = os.path.join(os.path.dirname(__file__), 'assets_us.json')
with open(file_path_us) as f:
    tickers_us = json.load(f)

delisted_tickers_us = check_delisted_tickers(tickers_us)
print(f"已下市的美股 delisted_tickers_us : {delisted_tickers_us} \n")
print(f"總計 : {len(delisted_tickers_us)} \n")

print("=" * 20)

# 檢查台股下市的股票
file_path_tw = os.path.join(os.path.dirname(__file__), 'assets_tw.json')
with open(file_path_tw) as f:
    tickers_tw = json.load(f)

delisted_tickers_tw = check_delisted_tickers(tickers_tw)
print(f"已下市的台股 delisted_tickers_tw : {delisted_tickers_tw} \n")
print(f"總計 : {len(delisted_tickers_tw)} \n")

print("=" * 20)