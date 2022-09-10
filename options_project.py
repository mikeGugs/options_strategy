import yfinance as yf
import requests
import pandas as pd
import certifi
import ssl
import urllib

context = ssl.create_default_context(cafile=certifi.where())
result = urllib.request.urlopen(
    'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
    context=context)

url = pd.read_html(result)
df = url[0]
df.drop(['Security', 'SEC filings', 'GICS Sector', 'GICS Sub-Industry',
        'Headquarters Location', 'Date first added', 'CIK', 'Founded'],
        axis=1, inplace=True)


close_data = []
bad_tickers = []

for i in df['Symbol']:
    ticker = yf.Ticker(i)
    data = ticker.history(start='2022-06-01', end='2022-09-10')
    historical_closes = data.Close.values
    try:
        close_data.append(historical_closes)
    except TypeError:
        bad_tickers.append(i)
        close_data.append('NaN')
        print('whoops')
        continue


df['Close'] = close_data

print(df)