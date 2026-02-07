import yfinance as yf
import pandas_datareader as web
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ALPHA_STOCK_ENDPOINT = "https://www.alphavantage.co/query"
FINN_STOCK_ENDPOINT = "https://finnhub.io/api/v1/quote"

class StockData:
    def __init__(self, STOCK, price_source='yahoo'):
        """
        Initialize StockData with ticker symbol.

        Args:
            STOCK: Ticker symbol (e.g., 'AAPL', 'TSLA')
            price_source: Source for current price data ('yahoo', 'finnhub', 'alpha')
                         Default: 'yahoo' (free, no API key required)
        """
        self.ticker = STOCK
        self.price_source = price_source

        # API parameters (kept for backward compatibility)
        self.alpha_params = {
            # 'function': 'TIME_SERIES_DAILY', #Daily Close Price
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': STOCK,
            'interval':'1min',
            'apikey': os.environ.get('ALPHA_STOCK_API_KEY')
        }

        self.finn_params = {
            'symbol': STOCK,
            # 'token' : creds.FINN_STOCK_API_KEY,
            'token': os.environ.get('FINN_STOCK_API_KEY')
            # 'X - Finnhub - Token': FINN_STOCK_ENDPOINT,
        }

        # Fetch current price using selected source
        self.cur_price = self._get_current_price()

    def _get_current_price(self):
        """Fetch current price from selected data source."""
        if self.price_source == 'yahoo':
            return self._get_price_yahoo()
        elif self.price_source == 'finnhub':
            return self._get_price_finnhub()
        elif self.price_source == 'alpha':
            return self._get_price_alpha()
        else:
            # Default to Yahoo if invalid source
            return self._get_price_yahoo()

    def _get_price_yahoo(self):
        """Get current price from Yahoo Finance (FREE - no API key needed)."""
        try:
            print(f"DEBUG: Fetching Yahoo price for ticker: '{self.ticker}'")
            stock = yf.Ticker(self.ticker)

            # Use history() instead of info - more reliable and less rate-limited
            # Get the most recent trading day's close price
            print(f"DEBUG: Calling stock.history(period='1d')")
            hist = stock.history(period='1d')
            print(f"DEBUG: History returned, empty={hist.empty}, shape={hist.shape if not hist.empty else 'N/A'}")

            if hist.empty:
                raise ValueError(f"No price data available for {self.ticker}")

            # Get the most recent close price
            price = hist['Close'].iloc[-1]

            if price is None or price == 0:
                raise ValueError(f"Invalid price data for {self.ticker}")

            return float(price)

        except Exception as e:
            raise ValueError(f"Error fetching Yahoo Finance data for {self.ticker}: {str(e)}")

    def _get_price_finnhub(self):
        """Get current price from Finnhub API (requires API key)."""
        try:
            response = requests.get(FINN_STOCK_ENDPOINT, params=self.finn_params, timeout=10)
            response.raise_for_status()
            stock_data = response.json()

            if 'c' not in stock_data or stock_data['c'] == 0:
                raise ValueError(f"Invalid ticker symbol: {self.ticker}")

            return float(stock_data['c'])

        except Exception as e:
            raise ValueError(f"Error fetching Finnhub data for {self.ticker}: {str(e)}")

    def _get_price_alpha(self):
        """Get current price from Alpha Vantage API (requires API key)."""
        # ********* Alpha Vantage API - requires paid tier for full functionality
        raise NotImplementedError("Alpha Vantage integration not fully implemented")


    def get_historical_prices(self, start_date, end_date, source='yahoo'):
        """
        Fetch historical prices with error handling.

        Args:
            start_date: Start date (format: 'mm/dd/yyyy')
            end_date: End date (format: 'mm/dd/yyyy')
            source: Data source ('yahoo', 'stooq', etc.)
                   Default: 'yahoo' (free, reliable, no API key needed)

        Returns:
            DataFrame with historical price data
        """
        try:
            if source == 'yahoo':
                # Convert date format from 'mm/dd/yyyy' to 'yyyy-mm-dd' for yfinance
                start_formatted = datetime.strptime(start_date, '%m/%d/%Y').strftime('%Y-%m-%d')
                end_formatted = datetime.strptime(end_date, '%m/%d/%Y').strftime('%Y-%m-%d')

                # Use yfinance for Yahoo Finance data (more reliable)
                stock = yf.Ticker(self.ticker)
                df = stock.history(start=start_formatted, end=end_formatted)

                if df.empty:
                    raise ValueError(f"No data available for {self.ticker}")

                return df
            else:
                # Use pandas_datareader for other sources (stooq, etc.)
                df = web.DataReader(self.ticker, source, start_date, end_date)

                if df.empty:
                    raise ValueError(f"No data available for {self.ticker}")

                return df

        except Exception as e:
            raise Exception(f"Error fetching historical data for {self.ticker}: {str(e)}")

    def calc_returns(self, df, day_offset):
        # Calculate returns: (future_price - current_price) / current_price
        df['returns'] = df['Close'].diff(periods=-day_offset) / df['Close']
        stdev = df['returns'].std()
        mean = df['returns'].mean()
        nf_conf = mean - 2.33 * stdev
        nf_percentile = df['returns'].quantile(.02)
        skew = df['returns'].skew()

        return df, stdev, mean, nf_conf, nf_percentile, skew
