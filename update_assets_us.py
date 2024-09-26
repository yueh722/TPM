import pandas as pd
import yfinance as yf
import json
#download sp500 list
sp500url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
sp500 = pd.read_html(sp500url, header=0)[0]
sp500 = sp500[['Symbol', 'Security']]
sp500.columns = ['ticker', 'name']
sp500 = sp500.set_index('ticker')['name'].to_dict()
#download NASDQ list
nasdaqurl = 'https://en.wikipedia.org/wiki/NASDAQ-100'
nasdaq = pd.read_html(nasdaqurl, header=0)[4]
nasdaq = nasdaq[['Ticker', 'Company']]
nasdaq.columns = ['ticker', 'name']
nasdaq = nasdaq.set_index('ticker')['name'].to_dict()
#Add nasdaq after sp500
sp500.update(nasdaq)
#Add Special stocks after sp500
stocks = {"BTC-USD":"BTC-USD | Bitcoin USD", "ETH-USD" : "ETH-USD | Ethereum USD", "SPY" : "SPDR S&P 500 ETF Trust","IEF" : "iShares 7-10 Year Treasury Bond ETF",
          "IAU": "iShares Gold Trust","XME":"SPDR S&P Metals & Mining ETF" ,"XLI":" Industrial Select Sector SPDR Fund","XLRE":"Real Estate Select Sector SPDR Fund",
          "XLF":"Financial Select Sector SPDR Fund","XLE":"Energy Select Sector SPDR Fund","XLK":"Technology Select Sector SPDR Fund","XTL":"SPDR S&P Telecom ETF","XLP":"Consumer Staples Select Sector SPDR Fund","XLY":"Consumer Discretionary Select Sector SPDR Fund"
          ,"XLU":"Utilities Select Sector SPDR Fund","XLV":"Health Care Select Sector SPDR Fund"}
sp500.update(stocks)
#save as json
with open('assets_us.json', 'w') as f:
    json.dump(sp500, f)
