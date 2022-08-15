import pandas_datareader as web
from datetime import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import requests
import creds
import os

ALPHA_STOCK_ENDPOINT = "https://www.alphavantage.co/query"
FINN_STOCK_ENDPOINT = "https://finnhub.io/api/v1/quote"
# STOCK = 'TSLA'

class StockData:
    def __init__(self, STOCK):
        self.alpha_params = {
            # 'function': 'TIME_SERIES_DAILY', #Daily Close Price
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': STOCK,
            'interval':'1min',
            'apikey': os.environ.get('ALPHA_A_API_KEY')
        }

        self.finn_params ={
            'symbol': STOCK,
            # 'token' : creds.FINN_STOCK_API_KEY,
            'token': os.environ.get('FINN_API_KEY')
            # 'X - Finnhub - Token': FINN_STOCK_ENDPOINT,

        }

        response = requests.get(FINN_STOCK_ENDPOINT, params=self.finn_params)
        response.raise_for_status()
        stock_data = response.json()

        # ********* Alpha Advantage API not currently being used. Free tier is insufficient (doesn't adj hist price)
        # daily_data = stock_data['Time Series (Daily)']
        # prices = [daily_data[date]['4. close'] for date, price in daily_data.items()]

        self.cur_price = float(stock_data['c'])
        self.ticker = STOCK


    def get_historical_prices(self, start_date, end_date, source='yahoo'):

        return web.DataReader(self.ticker, source, start_date, end_date)

    def calc_returns(self, df, day_offset):
        df['returns'] = -1 * df['Adj Close'].diff(periods=-day_offset) / df['Adj Close']
        stdev = df['returns'].std()
        mean = df['returns'].mean()
        nf_conf = mean - 2.33 * stdev
        nf_percentile = df['returns'].quantile(.02)
        skew = df['returns'].skew()

        return df, stdev, mean, nf_conf, nf_percentile, skew
