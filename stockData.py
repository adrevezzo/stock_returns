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


#
# df = get_stock_prices(ticker='tsla', start_date='08/04/2015', end_date='08/03/2022')
# plt.plot(df.index, df.Close, color='red')
# plt.show()