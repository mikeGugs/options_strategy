import yfinance as yf
import requests
import pandas as pd
import certifi
import ssl
import urllib
import numpy as np

class GetData:

    def get_snp_500_universe():
        """Returns a dataframe with all tickers in the S&P 500 with tickers
        under label 'Symbol'."""
        context = ssl.create_default_context(cafile=certifi.where())
        result = urllib.request.urlopen(
            'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
            context=context)

        url = pd.read_html(result)
        df = url[0]
        df.drop(['Security', 'SEC filings', 'GICS Sector', 'GICS Sub-Industry',
                 'Headquarters Location', 'Date first added', 'CIK', 'Founded'],
                axis=1, inplace=True)
        return df

    def get_stock_historical_data(df):
        """Requires a dataframe containing the stocks you want to include
        under column title 'Symbol'. Returns a df with all stocks and a list
        of their closing prices for the last three months."""
        close_data = []
        bad_tickers = []
        for i in df['Symbol']:
            ticker = yf.Ticker(i)
            data = ticker.history(period='3mo')
            historical_closes = list(data.Close.values)
            try:
                close_data.append(historical_closes)
            except TypeError:
                bad_tickers.append(i)
                close_data.append('NaN')
                print(f'Not able to grab close prices for {i}. Please check.')
                continue
        df['Close'] = close_data
        return df

    def get_historical_returns(df):
        """Adds a column that transforms historical close data into
        historical returns data."""
        pct_changes = []
        for index, row in df.iterrows():
            try:
                pct_chg = np.asarray(
                    [a1 / a2 - 1 for a1, a2 in zip(row['Close'][1:],
                                                   row['Close'])])

                pct_changes.append(pct_chg)
            except RuntimeWarning:
                print(f"issue calculating pct change on {row['Symbol']}")
        df['pct changes'] = pct_changes
        return df

    def calculate_sigma(df):
        """Adds a column that calculates the standard deviation of the
        historical returns."""
        stds = []
        for index, row in df.iterrows():
            try:
                std = np.std(row['pct changes']) * (252 ** .5)
                stds.append(std)
            except:
                print(f"issue calculating sigma on {row['Symbol']}")

        df['standard deviation'] = stds
        return df


stocks = GetData.get_snp_500_universe()
closes = GetData.get_stock_historical_data(stocks)
returns = GetData.get_historical_returns(closes)
sigmas = GetData.calculate_sigma(returns)
print(sigmas.to_string())














