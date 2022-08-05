import pandas_datareader as web
from datetime import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt


def get_stock_prices(ticker, start_date, end_date, source='yahoo'):

    cur = (datetime.now() - relativedelta(days=1)).strftime("%m/%d/%Y")
    end = (datetime.now() - relativedelta(years=25)).strftime("%m/%d/%Y")

    df = web.DataReader(ticker, 'yahoo', start_date, end_date)

    # plt.plot(df.index, df.Close, color='red')

    return df

def calc_returns(df, day_offset):
    df['returns'] = -1 * df['Adj Close'].diff(periods=-day_offset) / df['Adj Close']
    stdev = df['returns'].std()
    mean = df['returns'].mean()
    nf_conf = mean - 2.33 * stdev
    nf_percentile = df['returns'].quantile(.02)

    return df, stdev, mean, nf_conf, nf_percentile
#
# df = get_stock_prices(ticker='tsla', start_date='08/04/2015', end_date='08/03/2022')
# # plt.plot(df.index, df.Close, color='red')
# # plt.show()
# df['returns'] = -1*df['Adj Close'].diff(periods=-16)/df['Adj Close']
# stdev = df['returns'].std()
# mean = df['returns'].mean()
# nf_conf = mean - 1.96*stdev
# plt.hist(df['returns'], bins=30)
# plt.title(f'Mean return is: {mean*100: .2f}%\nLower 95% Conf return is: {nf_conf*100: .2f}%')
# plt.show()

# print(df.head(15))