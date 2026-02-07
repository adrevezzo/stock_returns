from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap5 as Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from stockData import StockData
import yfinance as yf
import base64
from io import BytesIO
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import pandas as pd
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get SECRET_KEY from environment variable or use a default for development
# IMPORTANT: Set FLASK_KEY environment variable in production!
secret_key = os.environ.get('FLASK_KEY')
if not secret_key:
    if os.environ.get('FLASK_ENV') == 'production':
        raise ValueError("FLASK_KEY environment variable must be set in production!")
    else:
        # Development fallback - NOT secure for production
        secret_key = 'dev-secret-key-change-in-production'
        print("WARNING: Using development SECRET_KEY. Set FLASK_KEY environment variable for production!")

app.config['SECRET_KEY'] = secret_key
Bootstrap(app)


# *************** CREATE GET STOCK DATA FORM *****************

class GetStockData(FlaskForm):
    ticker = StringField('Stock Ticker', validators=[DataRequired()])
    start_date = StringField('Start Date (mm/dd/yyyy)', validators=[DataRequired()])
    end_date = StringField('End Date (mm/dd/yyyy)', validators=[DataRequired()])
    ret_period = StringField('Return Period (days)', validators=[DataRequired()])

    submit = SubmitField("Get Data")



@app.route("/", methods=['GET', 'POST'])
def home():
    form = GetStockData()

    if form.validate_on_submit():
        try:
            ticker = form.ticker.data.strip()
            start = form.start_date.data
            end = form.end_date.data

            # Validate return period is a positive integer
            try:
                ret_per = int(form.ret_period.data)
                if ret_per <= 0:
                    flash('Return period must be a positive number.', 'error')
                    return render_template('index.html', form=form)
            except ValueError:
                flash('Return period must be a valid number.', 'error')
                return render_template('index.html', form=form)

            # Create StockData without calling __init__ to avoid Yahoo rate limit
            stock = StockData.__new__(StockData)
            stock.ticker = ticker.upper()

            # Get Historical Prices
            df = stock.get_historical_prices(start, end)

            # Get actual current/real-time price (not just last price from historical range)
            try:
                current_ticker = yf.Ticker(ticker.upper())
                current_data = current_ticker.history(period='1d')
                if not current_data.empty:
                    cur_price = float(current_data['Close'].iloc[-1])
                else:
                    # Fallback to last price from historical data if current price unavailable
                    cur_price = float(df['Close'].iloc[-1])
            except Exception:
                # Fallback to last price from historical data on error
                cur_price = float(df['Close'].iloc[-1])

            # Check if data is empty
            if df is None or df.empty:
                flash(f'No data found for ticker {ticker.upper()}. Please check the ticker symbol and date range.', 'error')
                return render_template('index.html', form=form)

            df2, stdev, mean, nf_conf, nf_per, skew = stock.calc_returns(df=df, day_offset=ret_per)

            # Generate figure optimized to fit on screen
            fig = Figure(figsize=(10, 6), facecolor='white', dpi=80)
            ax1, ax2 = fig.subplots(2, 1)

            # Create Price Action Chart with grid - Blue color scheme
            ax1.set_title(f'{ticker.upper()} Closing Prices from {start} through {end}',
                         fontsize=12, fontweight='bold', pad=10)
            ax1.plot(df.index, df['Close'], color='#2E86AB', linewidth=2.5, label='Close Price')
            ax1.set_ylabel('Price ($)', fontsize=10)
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.legend(loc='best')

            # Create Returns Distribution - Orange color scheme
            ax2.set_title(f'Distribution of {ret_per}-Day Returns (Skew = {skew:.3f})',
                         fontsize=12, fontweight='bold', pad=10)
            ax2.hist(df2['returns'], bins=30, color='#FF8C42', alpha=0.7, edgecolor='black', linewidth=1.2)
            ax2.set_xlabel('Return', fontsize=10)
            ax2.set_ylabel('Frequency', fontsize=10)
            ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
            ax2.axvline(mean, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean*100:.2f}%')
            ax2.legend(loc='best')

            fig.tight_layout(pad=2.0)

            # Convert plot to PNG image
            pngImage = BytesIO()
            FigureCanvas(fig).print_png(pngImage)

            # Encode PNG image to base64 string
            img = "data:image/png;base64,"
            img += base64.b64encode(pngImage.getvalue()).decode('utf8')

            # Close figure to prevent memory leak
            fig.clear()
            del fig

            stats_df = pd.DataFrame((stdev, mean, nf_conf, nf_per, ret_per),
                                    index=['stdev', 'mean', 'nf_conf', 'nf_per', 'ret_per'],
                                    columns=['stats'])

            return render_template('chart.html', tick=ticker, plot=img, cur_price=cur_price, stats=stats_df)

        except requests.exceptions.RequestException as e:
            flash(f'Error fetching data: Unable to connect to data source. Please try again later.', 'error')
            return render_template('index.html', form=form)
        except KeyError as e:
            flash(f'Error: Invalid ticker symbol "{ticker.upper()}". Please check and try again.', 'error')
            return render_template('index.html', form=form)
        except Exception as e:
            flash(f'An unexpected error occurred. Please try again.', 'error')
            return render_template('index.html', form=form)

    return render_template('index.html', form=form)

@app.route("/stockdata", methods=['GET', 'POST'])
def get_stock_data():
    form = GetStockData()
    return render_template('search.html', form=form)

@app.route("/blog")
def blog():

    return render_template('blog.html')


@app.route("/login")
def login():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)