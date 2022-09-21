import yfinance as yf
import requests
import pandas as pd
from pandas_datareader import data as pdr
import certifi
import ssl
import urllib
import numpy as np
from datetime import date, datetime, timedelta


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
        df.dropna(inplace=True)
        return df

    def _add_market_cap(df):
        """Adds a column containing each stock's market capitalization."""
        yf.pdr_override()
        mkt_caps = []
        for symbol in df['Symbol']:
            try:
                mkt_cap = pdr.get_quote_yahoo(symbol)['marketCap']
                mkt_caps.append(int(mkt_cap))
            except KeyError:
                mkt_caps.append(np.NaN)
        df['Market Cap'] = mkt_caps
        df.dropna(inplace=True)
        return df

    def get_stock_historical_data(df):
        """Requires a dataframe containing the stocks you want to include
        under column title 'Symbol'. Returns a df with all stocks and a list
        of their closing prices for the last three months."""
        close_data = []
        for i in df['Symbol']:
            ticker = yf.Ticker(i.replace('.', '-'))
            data = ticker.history(period='3mo')
            historical_closes = list(data.Close.values)
            close_data.append(historical_closes)
            if not historical_closes:
                historical_closes = np.NaN
        df['Close'] = close_data
        df.dropna(inplace=True)
        return df

    def get_historical_returns(df):
        """Adds a column that transforms historical close data into
        historical returns data."""
        pct_changes = []
        for index, row in df.iterrows():
            pct_chg = np.asarray([a1 / a2 - 1 for a1, a2 in zip(row['Close'][1:],
                                                   row['Close'])])

            pct_changes.append(pct_chg)
        df['pct changes'] = pct_changes
        return df

    def get_options_data(df):
        """Will add a column to a dataframe with relevant market information
        from current put and call options options contracts on the chosen
        stocks. The criteria to be included here is that the expiry is at most
        one month from now and the strike prices are +/- 5% from the
        previous close of the underlying."""
        all_options_expiries = []
        for ticker in df['Symbol']:
            t = yf.Ticker(ticker)
            all_options_expiries.append(list(t.options))
        one_month_ahead = datetime.today() + timedelta(30)
        good_options_expiries = [
            [x for x in i if datetime.strptime(x, '%Y-%m-%d') <
             one_month_ahead] for i in all_options_expiries]
        try:
            one_month_ahead_options_expiries = [date[-1] for date in
                                                good_options_expiries]
        except IndexError:
            one_month_ahead_options_expiries = 0


        df['Options expiry'] = one_month_ahead_options_expiries

        calls = []
        puts = []

        for col, row in df.iterrows():
            minus_five_percent_from_close = (row['Close'][-1] * .95)
            plus_five_percent_from_close = (row['Close'][-1] * 1.05)
            t = yf.Ticker(row['Symbol'])
            opt1 = t.option_chain(row['Options expiry'])
            plus_minus_five_percent_strike_calls = [{'type': 'call',
                                                     'option_symbol': rows.contractSymbol,
                                                     'strike': rows.strike,
                                                     'last': rows.lastPrice,
                                                     'bid': rows.bid,
                                                     'ask': rows.ask,
                                                     'volume': rows.volume,
                                                     'ITM': rows.inTheMoney, }
                                                    for cols, rows in
                                                    opt1.calls.iterrows() if
                                                    rows.strike
                                                    < plus_five_percent_from_close and
                                                    rows.strike > minus_five_percent_from_close]
            calls.append(plus_minus_five_percent_strike_calls)
            plus_minus_five_percent_strike_puts = [{'type': 'put',
                                                    'option_symbol': rows.contractSymbol,
                                                    'strike': rows.strike,
                                                    'last': rows.lastPrice,
                                                    'bid': rows.bid,
                                                    'ask': rows.ask,
                                                    'volume': rows.volume,
                                                    'ITM': rows.inTheMoney, }
                                                   for cols, rows in
                                                   opt1.puts.iterrows() if
                                                   rows.strike
                                                   < plus_five_percent_from_close and
                                                   rows.strike > minus_five_percent_from_close]
            puts.append(plus_minus_five_percent_strike_puts)

        df['calls'] = calls
        df['puts'] = puts

        return df


class DoCalculations:

    def calculate_sigma(df):
        """Adds a column a dataframe that calculates the standard deviation of the
        historical returns of the underlying stocks."""
        stds = []
        for index, row in df.iterrows():
            std = np.std(row['pct changes']) * (252 ** .5)
            stds.append(std)

        df['standard deviation underlying'] = stds
        return df


"""
price (float) – the Black-Scholes option price
S (float) – underlying asset price
sigma (float) – annualized standard deviation, or volatility
K (float) – strike price
t (float) – time to expiration in years
r (float) – risk-free interest rate
flag (str) – ‘c’ or ‘p’ for call or put.
"""

stocks = GetData.get_snp_500_universe()
stocks_with_mcap = GetData._add_market_cap(stocks)
stocks_with_mcap.sort_values(by='Market Cap', ascending=False, inplace=True)
stocks_with_mcap_top_30 = stocks_with_mcap[:29]
closes = GetData.get_stock_historical_data(stocks_with_mcap_top_30)
returns = GetData.get_historical_returns(closes)
options = GetData.get_options_data(returns)
sigmas = DoCalculations.calculate_sigma(returns)
print(sigmas.to_string())

